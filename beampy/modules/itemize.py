# -*- coding: utf-8 -*-
"""
@author: devauch

Class to manage item lists for beampy
"""

from beampy import document
from beampy.modules.text import text
from beampy.modules.core import begingroup, endgroup
from beampy.functions import convert_unit, color_text, check_function_args

def itemize( items_list, **kwargs):

	'''

	Generates a list or an enumeration.

	See THEME['itemize'] for option

	TODO: ADD doc for function arguments
	'''

	args = check_function_args(itemize, kwargs)
	number = 1

	if args['width']!=None:
		in_width = float(convert_unit(args['width'])) - float(convert_unit(args['item_indent']))
	else:
		in_width = float(document._width) - float(convert_unit(args['item_indent']))

	begingroup(width=args['width'], x=args['x'], y=args['y'])

	for i, the_item in enumerate(items_list) :

		if args['item_style'] == 'bullet' :
			item_char = r'$\bullet$'

		elif args['item_style'] == 'number' :
			item_char = str(number) + r'.'
			number += 1

		else :
			item_char = item_style

		# Add color

		item_char = color_text( item_char, args['item_color'] )
		the_item = color_text( the_item, args['text_color'] )

		if i == 0 :
			text( item_char + r' ' + the_item, x = args['item_indent'],
			y = 0, width=in_width )
		else:
			text( item_char + r' ' + the_item, x = args['item_indent'],
			y = args['item_spacing'], width=in_width )

	endgroup()
