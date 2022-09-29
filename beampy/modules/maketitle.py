# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Beampy title module

"""
from beampy.core.store import Store
from beampy.core.group import group
from beampy.modules.text import text
import datetime


def default_maketitle(titlein, author=None, subtitle=None, date=None,
                      title_width=None, vert_space=None, **kwargs):

    args = Store.theme('maketitle')

    if date in ('Today', 'today', 'now'):
        date = datetime.datetime.now().strftime("%d/%m/%Y")

    if title_width is None:
        title_width = Store.theme('document')['width']*0.75

    if vert_space is None:
        vert_space = Store.theme('document')['height']*0.05

    with group(y='center') as g:

        text(titlein, x='center', width=title_width, y=0, color=args['title_color'],
             size=args['title_size'], align='center')

        if author is not None:
            if isinstance(author, str):
                text(author, x='center', width=title_width,
                     y="+"+str(2*vert_space), color=args['author_color'],
                     size=args['author_size'], align='center')

            elif isinstance(author, list):
                text(', '.join(author), x='center', width=title_width,
                     y="+" + str(vert_space), color=args['author_color'],
                     size=args['author_size'], align='center')

        if subtitle is not None:
            text(subtitle, x='center', width=title_width, y="+" +
                 str(vert_space), color=args['subtitle_color'],
                 size=args['subtitle_size'])

        if date is not None:
            text(date, x='center', width=title_width, y="+" +
                 str(vert_space), color=args['date_color'],
                 size=args['date_size'])
    
    return g

def maketitle(*args, **kwargs):
    """

    Create title content for the presentation. The function could be
    overwritten by Beampy theme. Theme could add or change the arguments of
    :py:func:`maketitle` function. The default theme use the set of parameters
    described below. These arguments should not be modified by other themes.

    Parameters
    ----------

    titlein : str
        The title of the presentation.

    author : str or list of str or None, optional
        The name of the author, or the list of author names (the default value
        is None).

    subtitle : str or None, optional
        The subtitle for the presentation (the default value is None).

    date : str or {'Today', 'today', 'now'} or None, optional
        The date for the presentation (the default value is None). If `date` is
        a str it will be displayed as the given str. If the `date` is either
        'Today' or 'today' or 'now' it will replaced automatically by the
        current date.

    title_width : int or float or str or None, optional
        The width of the `titlein` text (the default is value is None, which
        implies `tilte_width` = `document._width` * 0.75). If a `title_width`
        is given it is passed to the `beampy.text()` module to constrain the
        width of the `titlein` text.

    vert_space : int or float or str or None, optional
        The vertical spacing of maketitle elements (the default value is None,
        which implies `vert_space` = `document._height` * 0.75). `vert_space`
        could take any values allowed by the positioning system of beampy (see
        `x` or `y` allowed values for :py:mod:`beampy.base_module`).


    """

    # get_command_line(maketitle)
    # Check function arguments from THEME

    # The maketitle disable the layout that could be defined in THEME['slide']
    # slide = Store.get_current_slide()
    # slide.render_layout = False

    if callable(Store.theme('maketitle')['template']):
        titlegroup = Store.theme('maketitle')['template'](*args, **kwargs)
    else:
        titlegroup = default_maketitle(*args, **kwargs)

    return titlegroup
