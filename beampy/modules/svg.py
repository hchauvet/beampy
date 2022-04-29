# -*- coding: utf-8 -*-
"""
@author: hugo

Module to write raw svg commands in slides
"""

from beampy.core.document import document
from beampy.core._svgfunctions import inkscape_get_size
from beampy.core.group import group
from beampy.core.module import beampy_module
from beampy.core.geometry import convert_unit
from beampy.core.content import Content

import logging
import tempfile


class svg(beampy_module):
    """
    Insert svg content.

    Parameters
    ----------

    svg_content : string
        Svg elements to add written in svg syntax without svg document tag
        "<svg xmlns...>"

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the svg (the default is 0). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the svg (the default is 0). See positioning
        system of Beampy.

    """

    
    def __init__(self, svg_content, x=None, y=None, width=None, height=None,
                 margin=None, inkscape_size=True, *args, **kwargs):

        # inti the module
        super().__init__(x, y, width, height, margin, 'svg')

        # Update the signature
        self.update_signature()

        #add arguments as attributes
        self.set(svg_content=svg_content, inkscape_size=inkscape_size)

        #apply theme to None
        self._theme_exclude_args = ['inkscape_size']
        self.apply_theme()

        #Register the module
        self.add_content(svg_content, 'svg')

    def render(self):
        """
            The render of an svg part
        """

        #Need to create a temp file
        if self.inkscape_size:
            logging.debug('Run inkscape to get svg size')
            # Need to get the height and width of the svg command
            tmpsvg = ('<svg xmlns="http://www.w3.org/2000/svg" version="1.2" '
                      'baseProfile="tiny" '
                      'xmlns:xlink="http://www.w3.org/1999/xlink">'
                      f'{self.svg_content} </svg>')

            # Use NamedTemporaryFile, that automatically remove the file on close by default
            with tempfile.NamedTemporaryFile(mode='w', prefix='beampytmp', suffix='.svg') as f:
                f.write(tmpsvg)

                # Need to flush the file to make it's content updated on disk
                f.file.flush()
                
                # Get the dimension of the svg using inkscape
                svg_width, svg_height = inkscape_get_size(f.name)
                # update beampy module width/height
                self.width = svg_width
                self.height = svg_height
        else:
            svg_width = self.width.value
            svg_height = self.height.value

        # Set the svg to beampy module
        self.svgdef = self.svg_content

        # Update the final width/height of the content
        self.content_width = svg_width
        self.content_height = svg_height


        #Set rendered flag to true (needed for the cache)
        self.rendered = True


class line(svg):
    """
    Insert an svg line.

    Parameters
    ----------

    x2 : int or float or str
        End horizontal coordinate of the line. The value is passed to unit
        converted of Beampy which translate it to pixel.

    y2 : int or float or str
        End vertical coordinate of the line. The value is passed to unit
        converted of Beampy which translate it to pixel.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the line (the default theme sets this to
        'center'). See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the line (the default theme sets this to
        'auto'). See positioning system of Beampy.

    linewidth : string, optional
        Line width (the default theme sets this to '2px'). The value is given
        as string followed by an unit accepted by svg syntax.

    color : string, optional
        Line color (the default theme sets this to THEME['title']['color']).
        The color is given either as HTML hex value "#ffffff" or as svg
        colornames "blank".

    opacity: float, optional
        Opacity of the rectangle (the default theme sets this to 1). The
        value ranges between 0 (transparent) and 1 (solid).

    """

    def __init__(self, x2, y2, **kwargs):

        # The input type of the module
        self.type = 'svg'
        
        self.inkscape_size = True
        
        # Add args to the module
        self.check_args_from_theme( kwargs )
        self.x2 = x2
        self.y2 = y2

        # convert unit of x2 and y2
        self.x2 = convert_unit(self.x2)
        self.y2 = convert_unit(self.y2)

        self.args['x2'] = self.x2
        self.args['y2'] = self.y2

        # Build style for the rectangle
        beampy_svg_kword = {'color': 'stroke',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                self.style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        self.content = '<line x1="0" y1="0" x2="{x2}px" y2="{y2}px" style="{style}"/>'

        # Store svg definitions
        self.svgdefs = []
        self.svgdefsargs = []
        
        # Register the module
        self.register()

    def pre_render(self):
        self.content = self.content.format(x2=self.x2,
                                           y2=self.y2,
                                           style=self.style)

        
def hline(y, **kwargs):
    """
    Create an horizontal line at a given horizontal position.
    Accept all arguments of :py:mod:`beampy.line`
    
    Parameters
    ----------

    y : int or float or {'center', 'auto'} or str
        Vertical position for the line (the default theme sets this to
        'auto'). See positioning system of Beampy.

    See Also
    --------

    :py:mod:`beampy.line`

    """

    if isinstance(y, str):
        y = convert_unit(y)
        y = '%spx'%y

    return line(x=0, y=y, x2='%spx'%document._width, y2=0, **kwargs)


def vline(x, **kwargs):
    """
    Create an horizontal line at a given vertical position.
    Accept all arguments of :py:mod:`beampy.line`

    Parameters
    ----------

    x : int or float or {'center', 'auto'} or str
        Horizontal position for the line (the default theme sets this to
        'auto'). See positioning system of Beampy.

    See Also
    --------

    :py:mod:`beampy.line`

    """

    if isinstance(x, str):
        x = convert_unit(x)
        x = '%spx'%x

    return line(x=x, y=0, y2='%spx'%document._height, x2=0, **kwargs)


def grid(dx, dy, **kwargs):
    """
    Create a grid with a given spacing.

    Parameters
    ----------

    Accept all arguments of :py:mod:`beampy.line`

    See Also
    --------

    :py:mod:`beampy.line`

    """

    assert dx > 0
    assert dy > 0

    with group(x=0, y=0, width=document._width, height=document._height) as g:
        # create horizontal line
        cur_x = 0
        while (cur_x <= document._height):
            hline('%spx'%cur_x, **kwargs)
            cur_x += dx

        cur_y = 0
        while (cur_y <= document._width):
            vline('%spx'%cur_y, **kwargs)
            cur_y += dy

    return g

        
# TODO: Improve grid rendering to not loop over beampy elements but create a true grid
class grid_new(svg):
    """
    Create a grid with a given spacing.

    Parameters
    ----------

    dx : int
        Horizontal spacing for the grid. The unit used is pixel.

    dy : int
        Vertical spacing for the grid. The unit used is pixel.

    linewidth : string, optional
        Line width (the default theme sets this to '2px'). The value is given
        as string followed by an unit accepted by svg syntax.

    color : string, optional
        Line color (the default theme sets this to THEME['title']['color']).
        The color is given either as HTML hex value "#ffffff" or as svg
        colornames "blank".

    opacity: float, optional
        Opacity of the rectangle (the default theme sets this to 1). The
        value ranges between 0 (transparent) and 1 (solid).

    """

    def __init__(self, dx, dy, **kwargs):

        # The input type of the module
        self.type = 'svg'

        self.inkscape_size = True
        
        # Add args to the module
        self.check_args_from_theme( kwargs )
        self.dx = dx
        self.dy = dy


        # convert unit of x2 and y2
        self.dx = convert_unit(self.dx)
        self.dy = convert_unit(self.dy)

        self.args['dx'] = self.dx
        self.args['dy'] = self.dy

        # Build style for the rectangle
        beampy_svg_kword = {'color': 'stroke',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                self.style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))


        curslide = document._slides[self.slide_id]
        base_hline = '<line id="{id}" x1="0" y1="0" x2="{x2}px" y2="{y2}px" style="{style}"/>'

        self.content = base_hline
        self.content = self.content.format(x2=curslide.curwidth, y2=0,
                                           style=self.style, id='hlineXX')
        # Register the module
        # self.register()


        
class circle(svg):
    """
    Insert an svg circle.

    Parameters
    ----------

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the rectangle (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the rectangle (the default theme sets this to
        'auto'). See positioning system of Beampy.

    r : int or float or string, optional
         radius of the circle (the default theme sets this to 3 for '3px').
         When the value is given as string it accepts a unit allow by svg syntax.
         ("em" | "ex" | "px" | "in" | "cm" | "mm" | "pt" | "pc" | "%")
    
    color : string, optional
        Color filling the circle (the default theme sets this to
        THEME['title']['color']). The color is given either as HTML hex value
        "#ffffff" or as svg colornames "blank".

    linewidth : string, optional
        Circle edge line width (the default theme sets this to '1px'). The
        value is given as string followed by an unit accepted by svg syntax.

    edgecolor : string, optional
        Color of the circle edge (the default theme sets this to
        THEME['title']['color']). The color is given either as HTML hex value
        "#ffffff" or as svg colornames "blank".

    opacity: float, optional
        Opacity of the circle (the default theme sets this to 1). The
        value ranges between 0 (transparent) and 1 (solid).

    """

    def __init__(self, **kwargs):

        # The input type of the module
        self.type = 'svg'

        self.inkscape_size = False
        
        # Add args to the module
        self.check_args_from_theme( kwargs )
        
        # Build style for the rectangle
        beampy_svg_kword = {'color': 'fill',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity',
                            'edgecolor': 'stroke'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                self.style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        self.cx = convert_unit(self.r) + int(convert_unit(self.linewidth)/2)
        self.cy = convert_unit(self.r) + int(convert_unit(self.linewidth)/2)

        self.content = '<circle cx="{cx}" cy="{cy}" r="{r}" style="{style}" />'

        # Store svg definitions
        self.svgdefs = []
        self.svgdefsargs = []
        
        # Register the module
        self.register()

    def pre_render(self):
        self.content = self.content.format(r=self.r, cx=self.cx, cy=self.cy, style=self.style)

        self.width = convert_unit(self.r) * 2 + convert_unit(self.linewidth)
        self.height = convert_unit(self.r) * 2 + convert_unit(self.linewidth)

        self.update_size(self.width, self.height)
        

