#-*- coding:utf-8 -*-

from beampy.modules.tikz import tikz
from beampy.functions import convert_unit

def arrow(x, y, dx, dy, style='->', color="black", lw='2pt', in_angle=None, out_angle=None, bend=None, head_style=""):
    """
    function to draw arrows on slide

    Arguments
    ---------

    x: initial x position of the arrow
    y: initial y position

    dx: end of arrow relative to x
    dy: end of arrow relative to y

    style ["->"]: arrow style "-": a simple line
                              "->": simple arrow
                              "<->": two way arrows

    color ['black']: arrow color (you can use svgnames)

    lw ["2pt"]: set the line width in point

    in_angle  [None]: angle at the end of the arrow
    out_angle [None]: angle at the start of the arrow
    bend [None]: direction of arrow bending "left" or "right"

    head_style [""]: change head_style of arrow: "latex", "stealth"
    """



    tikz_cmd = r"""
    \coordinate (a) at ({x},{y});
    \coordinate (b) at ({xf},{yf});

    \path[{style}, {color}, line width={lw}, {headstyle}] (a) edge {options} (b);
    """


    #Convert px to pt (tikz doesn't accept px)
    cmdx = "%0.1fpt"%(float(convert_unit(str(dx))) * 72.27/96.0)
    cmdy = "%0.1fpt"%(float(convert_unit(str(dy))) * 72.27/96.0)

    if head_style != "":
        head_style = ">=%s"%(head_style)

    options=[]
    if bend != None:
        options += ['bend %s'%bend]

    if in_angle != None:
        options += ['in=%0.1f'%in_angle]

    if out_angle != None:
        options += ['out=%0.1f'%out_angle]

    options = ','.join(options)
    if options != '':
        options = '[%s]'%options

    tikz_cmd = tikz_cmd.format( x=0, y=0, xf=cmdx, yf=cmdy, style=style,
                                color=color, lw=lw, headstyle=head_style,
                                options=options )

    #Run tikz command
    if dx < 0:
        tmpanchor='right'
    else:
        tmpanchor='left'

    if dy < 0:
        tmpanchor += '_top'
    else:
        tmpanchor += '_bottom'

    return tikz( tikz_cmd, x=x, y=y, figure_anchor=tmpanchor)
