# -*- coding: utf-8 -*-
"""
@author: hugo

Module to write raw svg commands in slides
"""

from beampy import document
from beampy.functions import (getsvgwidth, getsvgheight)
from beampy.modules.core import beampy_module, group
from beampy.geometry import convert_unit

import logging
import tempfile
import os


class svg( beampy_module ):
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

    
    def __init__(self, svg_content, **kwargs):
        # The input type of the module
        self.type = 'svg'

        # Need to call inkscape to get width and height
        self.inkscape_size = True
        
        # Add args to the module
        self.load_args(kwargs)

        # Save the content
        self.content = svg_content
        
        #Register the module
        self.register()

    def render(self):
        """
            The render of an svg part
        """

        #Need to create a temp file
        if self.inkscape_size:
            logging.debug('Run inkscape to get svg size')
            # Need to get the height and width of the svg command
            tmpsvg = '<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" xmlns:xlink="http://www.w3.org/1999/xlink">'
            if self.out_svgdefs is not None:
                tmpsvg += '<defs>%s</defs>' % (' '.join(self.out_svgdefs))

            tmpsvg += ' %s</svg>' % (self.content)

            tmpfile, tmpname = tempfile.mkstemp(prefix='beampytmp')
            with open(tmpname + '.svg', 'w') as f:
                f.write(tmpsvg)

            svg_width = getsvgwidth(tmpname + '.svg')
            svg_height = getsvgheight(tmpname + '.svg')

            # remove the svg
            os.remove(tmpname + '.svg')
        else:
            svg_width = convert_unit(self.width.value)
            svg_height = convert_unit(self.height.value)

        #Update the final svg size
        self.update_size(svg_width, svg_height)
        #Add the final svg output of the figure
        self.svgout = self.content

        #Set rendered flag to true (needed for the cache)
        self.rendered = True


class rectangle(svg):
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

    opacity: float, optional
        Opacity of the rectangle (the default theme sets this to 1). The
        value ranges between 0 (transparent) and 1 (solid).

    rx: int, optional
        The number of pixels for the rounding the rectangle corners in
        x direction (The default theme sets this value to 0). 

    ry: int, optional
        The number of pixels for the rounding the rectangle corners in
        y direction (The default theme sets this value to 0). 
    
    svgfilter: string or None, optional
        Set the id of the svg filter ('#name') to apply to the
        rectangle (default value is None, which means no
        filter). Filter definitaion should be added to slide.svgdefout
        list.

    svgclip: string or None, optional
       Set the id of the clip object ('#name') to apply on the
       rectangle (the default value is None, which means no clip to
       apply). Clip definition should be added to slide.svgdefout
       list.

    """

    def __init__(self, **kwargs):

        # The input type of the module
        self.type = 'svg'

        # Add args to the module
        self.check_args_from_theme( kwargs )

        # The size can be computed easily if no filter or clip path is given
        if self.svgclip is not None or self.svgfilter is not None:
            self.inkscape_size = True
        else:
            self.inkscape_size = False

        
        # Build style for the rectangle
        beampy_svg_kword = {'color': 'fill',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity',
                            'edgecolor': 'stroke'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                self.style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        self.dxdy = int(convert_unit(self.linewidth)/2)
        self.content = ''''<rect x="{dx}" y="{dy}" rx="{rx}" ry="{ry}"
        width="{width}" height="{height}" style="{style}" {filter}
        {clip}/>'''

        # Store svg definitions
        self.svgdefs = []
        self.svgdefsargs = []
        
        # Register the module
        self.register()
        
    def pre_render(self):

        if self.svgfilter is None:
            self.svgfilter = ''
        else:
            self.svgfilter = 'filter="url({id})"'.format(id=self.svgfilter)
            
        if self.svgclip is None:
            self.svgclip = ''
        else:
            self.svgclip = 'clip-path="url({id})"'.format(id=self.svgclip)
            
        # Update the width height of the rectangle
        self.content = self.content.format(width=self.width-self.dxdy*2,
                                           height=self.height-self.dxdy*2,
                                           dx=self.dxdy, dy=self.dxdy,
                                           rx=self.rx, ry=self.ry,
                                           style=self.style,
                                           filter=self.svgfilter,
                                           clip=self.svgclip)


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
        

