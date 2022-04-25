#!/usr/bin/env python3

"""
Create svg rectangle module for beampy_slideshow
"""
from beampy.core.geometry import convert_unit
from beampy.core.module import beampy_module


class rectangle(beampy_module):
    """
    Insert an svg rectangle.

    Parameters
    ----------

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the rectangle (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the rectangle (the default theme sets this to
        'auto'). See positioning system of Beampy.

    height : string, optional
         Height of the rectangle (the default theme sets this to '10px').
         The value is given as string with a unit accepted by svg syntax.

    width : string, optional
         Width of the rectangle (the default theme sets this to
         :py:mod:`document._width`). The value is given as string with a unit
         accepted by svg syntax.

    margin: TODO import doc from  beampy_module init method

    color : string, optional
        Color filling the rectangle (the default theme sets this to
        THEME['title']['color']). The color is given either as HTML hex value
        "#ffffff" or as svg colornames "blank".

    linewidth : string, optional
        Rectangle edge line width (the default theme sets this to '2px'). The
        value is given as string followed by an unit accepted by svg syntax.

    edgecolor : string, optional
        Color of the rectangle edge (the default theme sets this to
        THEME['text']['color']). The color is given either as HTML hex value
        "#ffffff" or as svg colornames "blank".

    opacity : float, optional
        Opacity of the rectangle (the default theme sets this to 1). The
        value ranges between 0 (transparent) and 1 (solid).

    rx : int, optional
        The number of pixels for the rounding the rectangle corners in
        x direction (The default theme sets this value to 0).

    ry : int, optional
        The number of pixels for the rounding the rectangle corners in
        y direction (The default theme sets this value to 0).

    svgfilter : string or None, optional
        Set the id of the svg filter ('#name') to apply to the
        rectangle (default value is None, which means no
        filter). Filter definitaion should be added to slide.svgdefout
        list.

    svgclip : string or None, optional
       Set the id of the clip object ('#name') to apply on the
       rectangle (the default value is None, which means no clip to
       apply). Clip definition should be added to slide.svgdefout
       list.

    """

    def __init__(self, x=None, y=None, width=None, height=None, margin=None,
                 opacity=None, rx=None, ry=None, color=None, edgecolor=None,
                 linewidth=None, svgfilter=None, svgclip=None, **kwargs):

        # The input type of the module
        content_type = 'svg'

        self.opacity = opacity
        self.rx = rx
        self.ry = ry
        self.svgfilter = svgfilter
        self.svgclip = svgclip
        self.linewidth = linewidth
        self.color = color
        self.edgecolor = edgecolor

        # The size can be computed easily if no filter or clip path is given
        if self.svgclip is not None or self.svgfilter is not None:
            self.inkscape_size = True
        else:
            self.inkscape_size = False

        # Register the module
        super().__init__(x, y, width, height, margin, content_type, **kwargs)

        # Create a signature for the module
        self.update_signature()

        # Apply the theme for None arguments
        self.apply_theme()

        # Build style for the rectangle
        beampy_svg_kword = {'color': 'fill',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity',
                            'edgecolor': 'stroke'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                value = ''
                if getattr(self, kw) is not None:
                    value = getattr(self, kw)
                    self.style += '%s:%s;'%(beampy_svg_kword[kw], value)

        #self.dxdy = int(convert_unit(self.linewidth)/2)

        # Set a dummy content to generate a unique key for this rectangle
        # The true svg will be done in render method
        content = f'<rect rx="{self.rx}" ry="{self.ry}" style="{self.style}"'
        content += f'{self.svgfilter}{self.svgclip}/>'
        self.add_content(content, content_type)

    def render(self):
        """ Render the rectangle svg
        """

        if self.svgfilter is None:
            self.svgfilter = ''
        else:
            self.svgfilter = f'filter="url({self.svgfilter})"'

        if self.svgclip is None:
            self.svgclip = ''
        else:
            self.svgclip = f'clip-path="url({self.svgclip})"'

        out = (f'<rect width="{self.width.value}" height="{self.height.value}" '
               f'rx="{self.rx}" ry="{self.ry}" '
               f'style="{self.style}" {self.svgfilter} {self.svgclip}/>')

        # For svg form their is no data
        self.svgdef = out
        self.content_width = self.width.value
        self.content_height = self.height.value
