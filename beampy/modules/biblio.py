#-*- coding:utf-8 -*-
from beampy import document
from beampy.modules.text import text
from beampy.functions import check_function_args
def cite( list_authors, **kwargs):
    """
    function to write citation on slide

    Arguments
    ---------

    list_authors : python list of authors
    """

    citestr = '[' + ', '.join(list_authors) + ']'

    #Check arguments
    args = check_function_args(cite, kwargs)

    text( citestr, args)
