#!/usr/bin/env python3

"""
Beampy module to create circle from svg premitive
"""
from beampy.core.module import beampy_module
from beampy.core.geometry import Length
from beampy.core.functions import convert_unit

class circle(beampy_module):
    """
    Insert an svg circle. This class extend the beampy_module one.

    Parameters
    ----------

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the rectangle (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the rectangle (the default theme sets this to
        'auto'). See positioning system of Beampy.

    margin: int or list of int
        Set the margin around the rectangle

    opacity : float, optional
        Opacity of the circle (the default theme sets this to 1). The
        value ranges between 0 (transparent) and 1 (solid).

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
    """

    def __init__(self, x=None, y=None, width=None, margin=None, opacity=None, r=None,
                 color=None, linewidth=None, edgecolor=None, *args, **kwargs):


        super().__init__(x, y, width, width, margin, 'svg', **kwargs)

        self.set(opacity=opacity, color=color, edgecolor=edgecolor)

        self.update_signature()
        self.apply_theme()

        if width is not None:
            self.r = Length(width)/2
        else:
            self.r = Length(self.r)

        self.linewidth = Length(self.linewidth)

        print(self.r, self.linewidth)
        # Build style for the rectangle
        beampy_svg_kword = {'color': 'fill',
                            'linewidth': 'stroke-width',
                            'edgecolor': 'stroke'}

        self.style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                self.style += f'{beampy_svg_kword[kw]}:{getattr(self,kw)};'

        self.cx = self.r + self.linewidth/2
        self.cy = self.r + self.linewidth/2

        # A dummy content for the cache
        content = (f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}" '
                   f'style="{self.style}"/>')

        self.add_content(content, 'svg')

    def render(self):

        out = (f'<circle cx="{self.cx.value}" cy="{self.cy.value}" '
               f'r="{self.r.value}" style="{self.style}"/>')

        self.width = (self.r * 2 + self.linewidth).value
        self.height = (self.r * 2 + self.linewidth).value

        self.svgdef = out
        self.content_width = self.width
        self.content_height = self.height
