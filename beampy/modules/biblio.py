#-*- coding:utf-8 -*-

from beampy.modules.text import text
from beampy.functions import check_function_args


def cite( list_authors, **kwargs):
    """
    function to write citation on slide

    Arguments
    ---------

    list_authors : python list of authors
    """
    
    # in case there is only one citation
    if type(list_authors) == type( 'this_is_a_string' ) :
        list_authors = [ list_authors ]

    citestr = '[' + ', '.join(list_authors) + ']'

    #Check arguments
    args = check_function_args(cite, kwargs)

    text( citestr, **args)
