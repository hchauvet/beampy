#-*- coding:utf-8 -*-

from beampy.modules.tikz import tikz
from beampy.functions import convert_unit


def arrow(x, y, dx, dy, style='->', color="black", lw='2pt', in_angle=None,
          out_angle=None, bend=None, head_style="", dashed=False):
    """
    Draw an arrow on slide. Ticks is used to render the arrow.

    Parameters
    ----------

    x : int or float or {'center', 'auto'} or str
        Horizontal position for the arrow. See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str
        Vertical position for the arrow. See positioning system of Beampy.

    dx : int or str
        Arrow horizontal displacement relative to x. `dx` could given in pixel
        as an integer or a float or in as string with an unit like '2cm'. It
        could be negative (left of x) or positive (right of x).

    dy : int or str
        Arrow vertical displacement relative to y. `dy` could given in pixel
        as an integer or a float or in as string with an unit like '2cm'. It
        could be negative (top of y) or positive (bottom of y).

    style : str in {'-', '->', '<-', '<->'}, optional
        Arrow style (the default value is '->'). The style is the one defined
        by Ticks style:

        * '->' or '<-', simple arrow.
        * '<->', two way arrows.
        * '-', a line.

    color : string, optional
        Arrow Color (the default value is 'black'). The color is given as Latex
        svgnames.

    lw : str or int, optional
        Arrow line width (the default is '2pt'). If the value is given as
        string followed by an unit, it is converted by beampy convert_unit
        function. It could also be given as an integer.

    in_angle : int or None, optional
        Angle at the end of the arrow (the default value is None which implies
        that the angle is automatically computed).

    out_angle : int or None, optional
        Starting angle of the arrow (the default value is None which implies
        that the angle is automatically computed).

    bend : {'left' or 'right'} or None, optional
        Direction of arrow bending (the default value is None, which implies a
        straight arrow). 'left' bends the arrow to the left and 'right' to the
        right.

    head_style : {'latex' or 'stealth' or ''}, optional
        Tikz head style of the arrow (the default value is '', which implies
        default head style of Ticks).

    dashed : True or False, optional
        Create a dashed arrow line (the default value is False).

    """

    tikz_cmd = r"""
    \coordinate (a) at ({x},{y});
    \coordinate (b) at ({xf},{yf});

    \path[{style}, {color}, line width={lw}, {headstyle}] (a) edge {options}(b);
    """

    # Convert px to pt (tikz doesn't accept px)
    cmdx = "%0.1fpt"%(float(convert_unit(str(dx))) * 72.27/96.0)
    cmdy = "%0.1fpt"%(-float(convert_unit(str(dy))) * 72.27/96.0)

    if head_style != "":
        head_style = ">=%s"%(head_style)

    options = []
    if bend is not None:
        options += ['bend %s' % bend]

    if in_angle is not None:
        options += ['in=%0.1f' % in_angle]

    if out_angle is not None:
        options += ['out=%0.1f' % out_angle]

    if dashed:
        options += ['dashed']

    options = ','.join(options)
    if options != '':
        options = '[%s]' % options

    tikz_cmd = tikz_cmd.format(x=0, y=0, xf=cmdx, yf=cmdy, style=style,
                               color=color, lw=lw, headstyle=head_style,
                               options=options)

    # Run tikz command
    if dx < 0 or (isinstance(dx, str) and '-' in dx):
        tmpanchor = 'right'
    else:
        tmpanchor = 'left'

    if dy < 0 or (isinstance(dy, str) and '-' in dy):
        tmpanchor += '_bottom'
    else:
        tmpanchor += '_top'

    return tikz(tikz_cmd, x=x, y=y, figure_anchor=tmpanchor)
