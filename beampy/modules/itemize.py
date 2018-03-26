# -*- coding: utf-8 -*-
"""
@author: devauch

Class to manage item lists for beampy
"""

from beampy import document
from beampy.modules.text import text
from beampy.modules.core import group
from beampy.functions import convert_unit, color_text, check_function_args

# TODO: Implement itemize with beampy module class


def itemize( items_list, **kwargs):

    '''

    Generates a list or an enumeration.

    See THEME['itemize'] for option

    TODO: ADD doc for function arguments
    '''

    args = check_function_args(itemize, kwargs)
    number = 1

    if args['width'] is not None:
        in_width = float(convert_unit(args['width'])) - float(convert_unit(args['item_indent']))
    else:
        in_width = float(document._width) - float(convert_unit(args['item_indent']))

    if args['item_layers'] is not None:
        if len(items_list) != len(args['item_layers']):
            raise ValueError('Length of item_layers is not the same as the length of items_list')


    with group(width=args['width'], x=args['x'], y=args['y']) as groupitem:

        for i, the_item in enumerate(items_list) :

            if args['item_style'] == 'bullet' :
                item_char = r'$\bullet$'

            elif args['item_style'] == 'number' :
                item_char = str(number) + r'.'
                number += 1

            else :
                item_char = args['item_style']

            # Add color

            item_char = color_text( item_char, args['item_color'] )
            the_item = color_text( the_item, args['text_color'] )

            if i == 0 :
                t = text( item_char + r' ' + the_item, x = args['item_indent'],
                        y = 0, width=in_width )
            else:
                t = text( item_char + r' ' + the_item, x = args['item_indent'],
                        y = args['item_spacing'], width=in_width )

            # Add layers to item
            if args['item_layers'] is not None:
                layer = args['item_layers'][i]
                if isinstance(layer, str):
                    eval('t[%s]'%layer)
                else:
                    t[args['item_layers'][i]]

    return groupitem