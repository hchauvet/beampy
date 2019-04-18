"""
Beampy module to create a boxed group 
"""
from beampy.document import document
from beampy.functions import set_curentslide, set_lastslide
from beampy.modules.core import group
from beampy.modules.text import text
from beampy.modules.svg import rectangle
from beampy.geometry import center
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

    perentid : str or None, optional
        Beampy id of the parent group (the default is None). This parentid is
        given automatically by Beampy render.

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

    title_color : svg color name as string, optional
        The color of the title (the default value is 'white').

    title_align : {'left','right','center'}, optional
        The horizontal alignment of the title (the default value is
        'left').

    title_xoffset : int, optional
        The horizontal offset in pixel from the box border of the
        title (the default value is 10).

    auto_height_margin : int, optional
        The vertical margin in pixel (top and bottom) to use when box height is not specified 
        (the default theme sets this value to 15).

    """

    def __init__(self, title=None, x='center', y='auto', width=None,
                 height=None, parentid=None, **kwargs):

        self.title = title
        self.check_args_from_theme(kwargs)
        
        super(box, self).__init__(x=x,
                                  y=y,
                                  width=width,
                                  height=height,
                                  parentid=parentid,
                                  opengroup=False)
        
        # Build the title if it's not None
        self.bp_title = None # to store beampy text object for the title
        
        if self.title is not None:
            # Title should not be in group
            self.build_title()
            self.yoffset = self.head_height

    def build_title(self):
        
        self.title_xpos = self.title_xoffset
        self.title_ypos = 5

        self.bp_title = text(self.title, x=self.title_xpos,
                             y=self.title_ypos, color=self.title_color,
                             width=self.width-20)

        # Add y offset to the group (the height taken by the title)
        if self.head_height is None:
            self.head_height = (self.bp_title.height + 10).value

        # print(self.height, self.width)
        # self.remove_element_in_group(self.bp_title.id)
        # self.bp_title = None

    def build_background(self):
        if self.shadow:
            self.svg_shadow = '#drop-shadow'            
        else:
            self.svg_shadow = None

            
        self.main_svg = rectangle(width=self.width,
                                  height=self.height,
                                  rx=self.rounded,
                                  ry=self.rounded,
                                  edgecolor=self.color,
                                  linewidth=self.linewidth,
                                  color=self.background_color,
                                  svgfilter=self.svg_shadow,
                                  x=self.center+center(0),
                                  y=self.center+center(0))

        if self.svg_shadow is not None:
            self.main_svg.add_svgdef('''
            <filter id="drop-shadow"> <feGaussianBlur in="SourceAlpha"
            stdDeviation="3"/> <feOffset dx="4" dy="4" result="offsetblur"/>
            <feMerge> <feMergeNode/> <feMergeNode in="SourceGraphic"/> </feMerge>
            </filter>
            ''')
        
        if self.bp_title is not None:
            clipid = "#boxborder_{id}".format(id=self.id)


            self.title_svg = rectangle(width=self.width,
                                       height=self.head_height,
                                       color=self.color,
                                       edgecolor=self.color,
                                       linewidth=self.linewidth,
                                       svgclip=clipid,
                                       x="-%ipx"%(self.linewidth/2),
                                       y="-%ipx"%(self.linewidth/2))

            self.title_svg.rounded = self.rounded
            self.title_svg.add_svgdef('''
            <clipPath id="boxborder_%s">
            <rect width="{width}" height="{clipheight}" 
            rx="{rounded}" ry="{rounded}" stroke="{color}" 
            stroke-width="{linewidth}"/>
            </clipPath>
            ''' % self.id, ['width', 'clipheight', 'rounded',
                           'color', 'linewidth'])
            
            # Added to clip the title square
            self.title_svg.clipheight = self.head_height * 2
            
    def pre_render(self):
        set_curentslide(self.slide_id)

        if self.init_height is None:
            for eid in self.elementsid:
                elem = document._slides[self.slide_id].contents[eid]

                if elem.height.value is None:
                    elem.height.run_render()
                    
                if elem.width.value is None:
                    elem.width.run_render()
        
            self.compute_group_size()
            self.update_size(self.width, self.height+self.yoffset +
                             2*self.auto_height_margin)
            # Report offset on auto placed elements
            for eid in self.elementsid:
                document._slides[self.slide_id].contents[eid].positionner.y['final'] += self.yoffset + self.auto_height_margin

        else:
            # The case of the height is given and elements have a
            # fixed shift, weed need to update the shift with the
            # title yoffset TODO: This should be included in the group
            # class !!!
            for eid in self.elementsid:
                elemp = document._slides[self.slide_id].contents[eid].positionner
                if elemp.y['align'] not in ['auto', 'center'] and elemp.y['reference'] != 'relative':
                    document._slides[self.slide_id].contents[eid].positionner.y['shift'] += self.yoffset

        # Create the backgroud objects
        with self:
            self.build_background()

        # Propagate the layer inside the group
        # (as we added element in render time)
        self.propagate_layers()
        
        # Manage position of new objects 
        self.main_svg.first()

        # Replace the title of the box
        if self.bp_title is not None:
            self.title_svg.above(self.main_svg)

            # Set the correct layers for the title
            logging.debug('set layer to box title to %s ' % str(self.layers))
            self.bp_title.layers = self.layers

            title_xpos = self.left + self.title_xoffset

            if self.title_align == 'center':
                title_xpos = self.left + (self.title_svg.width-self.bp_title.width)/2

            if self.title_align == 'right':
                title_xpos = self.right - (self.bp_title.width + self.title_xpos)

            self.bp_title.positionner.update_y(self.top + 5)
            self.bp_title.positionner.update_x(title_xpos)

        set_lastslide()
