# -*- coding: utf-8 -*-
"""
@author: devauch

Class to manage item lists for beampy
"""
# TODO: Implement itemize with beampy module class

from beampy import document
from beampy.modules.text import text
from beampy.modules.core import group
from beampy.functions import convert_unit, color_text, check_function_args


def itemize(items_list, **kwargs):
    '''
    Generates a list or an enumeration.

    Parameters
    ----------

    items_list : list of str
        List of item sentences.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the item list (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the item list (the default is 'auto'). See
        positioning system of Beampy.

    width : int or float or None, optional
       Width of the group containing items (the default is None, which implies
       that the width is computed to fit the longest item width).

    item_style : {'bullet','number'} or str, optional
        Style of the item markers (the default theme sets this value to
        'bullet', which implies that item marker decorator is a bullet). The
        bullet could be replaced by any string, including latex symbols. When
        `item_style`='number', the item makers is an increasing number to
        create an enumeration.

    item_spacing : int or float or str, optional
        Vertical spacing between items (the default theme sets this value to
        '+1cm'). `item_spacing` accepts the same values as Beampy `x` or `y`.

    item_indent : int or float or str, optional
        Horizontal item indent (the default theme sets this value to '0cm').
        `item_indent` accepts the same values as Beampy `x` or `y`.

    item_color : str, optional
        Color of item marker (the default theme sets this value to
        doc._theme['title']['color']). Color could be given as svg-color-names
        or HTML color hex values (expl: #fffff for white).

    text_color : str, optional
        Color of the item texts (the default theme sets this value to
        doc._theme['text']['color']). Color could be given as svg-color-names
        or HTML color hex values (expl: #fffff for white).

    item_layers : (list of int or string) or None, optional
        Place items into layers to animate them (the default theme sets this
        value to None, which implies that all items are displayed on the same
        layer). The list should have the same length as the `items_list`. The
        item in `item_layers` list could refers to a given layer number, given
        as int, or use python list index syntax (like ':', ':-1', '3:') given
        as string.

        >>> itemize(['item1 on all layers', 'item2 on layer 1'],
                    item_layers=[':',1])

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
