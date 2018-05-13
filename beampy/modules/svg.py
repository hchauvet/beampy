# -*- coding: utf-8 -*-
"""
@author: hugo

Module to write raw svg commands in slides
"""

from beampy import document
from beampy.functions import (getsvgwidth, getsvgheight)
from beampy.modules.core import beampy_module
from beampy.geometry import convert_unit, positionner

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
        #The input type of the module
        self.type = 'svg'

        #Add args to the module
        self.load_args(kwargs)

        #Save the content
        self.content = svg_content

        #Register the module
        self.register()



    def render(self):
        """
            The render of an svg part
        """

        #TODO: Parse the svg to get height and width
        #Need to get the height and width of the svg command
        tmpsvg = '<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" xmlns:xlink="http://www.w3.org/1999/xlink">%s</svg>'%self.content

        #Need to create a temp file
        tmpfile, tmpname = tempfile.mkstemp(prefix='beampytmp')
        with open( tmpname + '.svg', 'w' ) as f:
            f.write( tmpsvg )

        svg_width =  getsvgwidth(tmpname + '.svg')
        svg_height = getsvgheight(tmpname + '.svg')

        #remove the svg
        os.remove( tmpname + '.svg' )

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

    """

    def __init__(self, **kwargs):

        # The input type of the module
        self.type = 'svg'

        # Add args to the module
        self.check_args_from_theme( kwargs )


        # Build style for the rectangle
        beampy_svg_kword = {'color': 'fill',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity',
                            'edgecolor': 'stroke'}

        style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        self.content = '<rect width="{width}" height="{height}" style="{style}" />'.format(width=self.width, height=self.height, style=style)

        # Register the module
        self.register()


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

        style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        self.content = '<line x1="0" y1="0" x2="{x2}px" y2="{y2}px" style="{style}"/>'.format(x2=self.x2, y2=self.y2, style=style)

        # Register the module
        self.register()


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

    # create horizontal line
    cur_x = 0
    while (cur_x <= document._height):
        hline('%spx'%cur_x, **kwargs)
        cur_x += dx

    cur_y = 0
    while (cur_y <= document._width):
        vline('%spx'%cur_y, **kwargs)
        cur_y += dy

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

        style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        svg_tmp = ''

        curslide = document._slides[self.slide_id]
        base_hline = '<line id="{id}" x1="0" y1="0" x2="{x2}px" y2="{y2}px" style="{style}"/>'.format(x2=curslide.curwidth,
                                                                                                      y2=0, style=style,
                                                                                                      id='hlineXX')

        self.content = svg_tmp
        # Register the module
        # self.register()
