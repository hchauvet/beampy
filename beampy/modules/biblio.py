#-*- coding:utf-8 -*-
from beampy import document
from beampy.modules.text import text

def cite( list_authors, x='center', y=580, color="default", size=10):
    """
    function to write citation on slide

    Arguments
    ---------

    list_authors : python list of authors
    """

    citestr = '[' + ', '.join(list_authors) + ']'

    if color == 'default':
        color = document._theme['title']['color']

    text( citestr, x=x, y=y, color=color, size=size)
