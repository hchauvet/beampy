#!/usr/bin/env python3

import math
from beampy.core.geometry import Length
from beampy.core.module import beampy_module
from beampy.core.group import group
from beampy.core.store import Store

class line(beampy_module):
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

    def __init__(self, x=None, y=None, x2=None, y2=None, margin=None, linewidth=None,
                 color=None, opacity=None, **kwargs):


        content_type = 'svg'

        super().__init__(x, y, 0, 0, margin, content_type, **kwargs)

        self.set(color=color, x2=x2, y2=y2, opacity=opacity,
                 linewidth=linewidth)

        self.update_signature()
        self.apply_theme()

        self.x2 = Length(self.x2)
        self.y2 = Length(self.y2, 'y')
        self.linewidth = Length(self.linewidth)

        # Build style for the rectangle
        beampy_svg_kword = {'color': 'stroke',
                            'linewidth': 'stroke-width'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                self.style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))

        # Dummy content just for the cache id generation
        content = f'<line x1="0" y1="0" x2="{self.x2}" y2="{self.y2}" style="{self.style}"/>'
        self.add_content(content, content_type)

    def post_render(self):
        """
        Add offset to the position of the line to place it correctly,
        Those opperation should not be in render function, because they will not
        be taken when the object is load from Content in Store or from Cache.
        """
        # print("run post render")
        if self.x2.value < 0:
            self.x = self.x - self.width.value

        if self.y2.value < 0:
            self.y = self.y - self.height.value


    def render(self):
        """
        Render the line
        """

        x2 = self.x2.value
        y2 = self.y2.value

        if (x2 == 0):
            angle = 0
        else:
            angle = math.atan(y2 / x2)

        # Compute the full width and height taking into account angle and linewidth
        a = math.sqrt(x2**2 + y2**2)
        b = self.linewidth.value
        self.width = round(abs(a * math.cos(angle)) + abs(b * math.sin(angle)))
        self.height = round(abs(b * math.cos(angle)) + abs(a * math.sin(angle)))

        # Need to do some offset du to the linewidth
        dx1 = round((b * math.sin(angle)) / 2)
        dy1 = round((b * math.cos(angle)) / 2)

        # Du to the signe of x2 and y2:
        if x2 < 0:
            if y2 < 0:
                dx1 = -dx1

            dx1 += self.width.value

        else:
            pass

        if y2 < 0:
            dy1 = -dy1
            if x2 > 0:
                dx1 = -dx1

            dy1 += self.height.value


        out = (f'<line x1="{dx1}px" y1="{dy1}px" x2="{x2+dx1}" y2="{y2+dy1}" '
               f'style="{self.style}"/>')

        self.svgdef = out
        self.content_width = self.width.value
        self.content_height = self.height.value

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



    return line(x=0, y=y, x2='100%', y2=0, **kwargs)


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

    return line(x=x, y=0, y2='100%', x2=0, **kwargs)


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

    cur_slide = Store.get_current_slide()
    with group(x=0, y=0, width=cur_slide.curwidth, height=cur_slide.curheight) as g:
        # create horizontal line
        cur_x = 0
        while (cur_x <= cur_slide.curheight):
            hline('%spx' % cur_x, **kwargs)
            cur_x += dx

        cur_y = 0
        while (cur_y <= cur_slide.curwidth):
            vline('%spx' % cur_y, **kwargs)
            cur_y += dy

    return g

