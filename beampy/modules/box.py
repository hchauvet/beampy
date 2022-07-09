"""
Beampy module to create a boxed group 
"""
from beampy.core.content import Content
from beampy.core.store import Store
from beampy.core.group import group
from beampy.core.geometry import (Margins, horizontal_distribute, vertical_distribute, center, right)
from beampy.modules.text import text
import logging


class box(group):
    """
    Draw a box around a group.

    Parameters
    ----------

    title : str or None, optional
        The title of the box (the default value is None, which implies
        no title).

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the group (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the group (the default is 'auto'). See
        positioning system of Beampy.

    width : int or float or None, optional
        Width of the group (the default is None, which implies that the width
        is computed to fit the group contents width).

    height : int or float or None, optional
        Height of the group (the default is None). When height is None the
        height is computed to fit the group contents height.

    margins  : int or list of size 2 or 4, optional
        The margin for the box.

    modules : list or None,
        The list of module to group inside this box

    rounded : int, optional
        The number of pixel for rounded borders (the default value is
        10).

    linewidth : int, optional
        The linewidth of the border in pt (the default value is 1).

    color : svg color name as string, optional
        The color of the contour line of the box (the default value is
        'red').

    head_height : int or None, optional
        The height in pixel of the background under the title (the
        default is None, which implies that height is computed from
        title height + 10px of margins). You need to adjust this value
        for multi-lines titles.

    shadow : boolean, optional
        Draw a shadow under the box (the default value is False, which
        means no shadow).

    background_color : svg color name as string, optional
        The color of the background of the box (the default values is
        'white').

    border_color : svg color name as string, optional
        The color of the border of the box (the default values is
        'red').

    title_color : svg color name as string, optional
        The color of the title (the default value is 'white').

    title_align : {'left','right','center'}, optional
        The horizontal alignment of the title (the default value is
        'left').

    title_xoffset : int, optional
        The horizontal offset in pixel from the box border of the
        title (the default value is 10).

    title_size : int, optional
        The size of the box title font (the default theme set this
        value the size of main text).

    title_opacity: int, [0, 1]
        The opacity of the box title (the default theme set this value to 1)

    title_background_color: svg color name as string, optional
        The color of the background below the title (The default theme
        set this to the same color as the contour line).

    title_margin: int or list of size 2 or 4, optional
        Set the margin the title (the default theme sets this value to 10)

    content_margin : int or list of size 2 or 4, optional
        The inner margin for the content of the viewbox.
    """

    def __init__(self, title=None, x=None, y=None, width=None, height=None, margin=None,
                 modules=None, rounded=None, linewidth=None, color=None, head_height=None, 
                 shadow=None, background_color=None, border_color=None, title_color=None, 
                 title_align=None, title_xoffset=None, title_size=None, title_opacity=None,
                 title_background_color=None, title_margin=None, content_margin=None, **kargs):

        self.set(title=title, modules=modules)
        self.theme_exclude_args = ['title', 'modules', 'color']

        self.update_signature()
        super().__init__(x=x, y=y, width=width, height=height, margin=margin,
                         modules=modules, background=None, **kargs)
        print('End of group init width, height', self.width, self.height)

        # Compatibility with the old beampy
        if color is not None:
            self.title_background_color = color
            self.border_color = color
            
        # Manager the margins 
        self.title_margin = Margins(self.title_margin)
        self.content_margin = Margins(self.content_margin)

        # Crop the width and height to respect content margin
        # Only when the size of the box is given
        if self.init_width is not None:
            self.width = self.width.value - (self.content_margin.left + self.content_margin.right)

        if self.init_height is not None:
            self.height = self.height.value - (self.content_margin.top + self.content_margin.bottom)
        
        print('End of init width, height', self.width, self.height)
            
    def render(self):
        """
        Redefine the render for the box
        """
        
        # Create a title without adding it to the group
        if self.title is not None:
            xt = 0
            yt = 0
            if self.title_align == 'center':
                xt = 'center'
            if self.title_align == 'right':
                xt = right(self.width.value+self.content_margin.left)

            box_title = text(self.title, x=xt, y=yt, width=self.width.value, margin=list(self.title_margin), 
                             size=self.title_size, color=self.title_color, align=self.title_align, 
                             opacity=self.title_opacity, add_to_group=False)

            # Get the offset of the title
            if self.head_height is None:
                self.head_height = box_title.total_height.value

            # Remove the height available to make auto positionning
            # of elements inside the group
            self.height = self.height.value - self.head_height

        # Run the group render
        super().render()
        group_height = self.group_height()

            

        if self.head_height is None:
            self.head_height = 0

        if self.title is not None:
            self.height = self.height.value + self.head_height

        # Loop over all modules except the title (the last one)
        for m in self.modules:
            m._final_x += self.content_margin.left 
            m._final_y += self.head_height + self.content_margin.top

        # Re call the title to add it to the box
        if self.title is not None:
            bt = box_title(x=xt, y=yt)
            bt.compute_position()
            if self.title_align == 'center':
                bt._final_x += self.content_margin.left


        # Restore the width and height with the margins
        self.width = self.width.value + self.content_margin.left + self.content_margin.right
        self.height = self.height.value + self.content_margin.top + self.content_margin.bottom 

        # Create the box
        svg_shadow = (f'<filter id="drop-shadow-{self.id}"> <feGaussianBlur in="SourceAlpha" '
                      'stdDeviation="3"/> <feOffset dx="4" dy="4" result="offsetblur"/> '
                      '<feMerge> <feMergeNode/> <feMergeNode in="SourceGraphic"/> </feMerge> '
                      '</filter>')
        
        # The value of the round corners
        r = self.rounded
        # the width and height of the box
        w = self.width.value
        h = self.height.value
        # the heigh of the header
        hh = self.head_height
        # the linewidth
        lw = self.linewidth

        if self.shadow:
            box_svg = svg_shadow + f'<g class="box" width="{w}" height="{h}" style="filter: url(#drop-shadow-{self.id})">'
        else:
            box_svg = f'<g class="box" width="{w}" height="{h}">'

        if hh > 0:
            # The header part of the box
            box_svg += (f'<path d="M {lw/2} {hh+lw/2} v {-(hh-r)} q 0 {-r} {r} {-r} '
                        f'h {w-2*r-lw} q {r} 0 {r} {r} v {hh-r} Z" '
                        f'fill="{self.title_background_color}" stroke="none" stroke-width="0"/>')
            # The content background of the box
            box_svg += (f'<path d="M {lw/2} {hh+lw/2} v {(h-hh-r-lw)} q 0 {r} {r} {r} '
                        f'h {w-2*r-lw} q {r} 0 {r} {-r} v {-(h-hh-r-lw)} Z" '
                        f'fill="{self.background_color}" stroke="none" stroke-width="0"/>')
        else:
            # The content background of the box without header
            box_svg += (f'<path d="M {r+lw/2} {hh+lw/2} q {-r} 0 {-r} {r} '
                        f'v {(h-hh-2*r-lw)} q 0 {r} {r} {r} h {w-2*r-lw} q {r} 0 {r} {-r} '
                        f'v {-(h-hh-2*r-lw)} q 0 {-r} {-r} {-r} Z" '
                        f'fill="{self.background_color}" stroke="none" stroke-width="0"/>')
        # The contour of the box
        if lw > 0:
            box_svg += (f'<path d="M {r+lw/2} {lw/2} h {w-2*r-lw} q {r} 0 {r} {r} v {h-2*r-lw} q 0 {r} {-r} {r} '
                        f'h {-(w-2*r-lw)} q {-r} 0 {-r} {-r} v {-(h-2*r-lw)} q 0 {-r} {r} {-r}" ' 
                        f'stroke="{self.border_color}" stroke-width="{lw}px" fill="none"/>')

        box_svg += '</g>'
        self.svg_decoration = box_svg
        # Export to data each group for the different layers
        self.svgdef = 'Defined on export'
        self.content_width = self.width.value
        self.content_height = self.height.value

        # Fix the width and height
        self.width = self.width.value
        self.height = self.height.value

        # For group we define the signature after the renderering
        # to include the list of modules
        self.update_signature(modules=self.modules)
