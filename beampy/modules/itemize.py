# -*- coding: utf-8 -*-
"""
@author: devauch

Class to manage item lists for beampy
"""

from beampy import document
from beampy.modules.text import text

def color_text( textin, color ):
	
	'''
		Adds Latex color to a string.
	'''
	
	if "#" in color:
		textin = r'{\color[HTML]{%s} %s }'%( color.replace('#','').upper(), textin)
	
	else:
		textin =r'{\color{%s} %s }'%( color, textin)

	return textin


def itemize( items_list, item_style = 'bullet', item_spacing = '+1cm' , item_indent = '2cm', item_color = 'default', text_color = 'default' ):
	
	'''
	
	Generates a list or an enumeration.
	
	'''
	
	number = 1
	
	if item_color == 'default' :
		item_color = document._theme.get( 'title', 'color' )
	
	if text_color == 'default' :
		text_color = document._theme.get( 'text', 'color' )
	
	for the_item in items_list :
		
		if item_style == 'bullet' :
			item_char = r'$\bullet$'
		
		elif item_style == 'number' :
			item_char = str(number) + r'.'
			number += 1
		
		else :
			item_char = item_style
		
		# Add color
		
		item_char = color_text( item_char, item_color )
		the_item = color_text( the_item, text_color )
		
		text( item_char + r' ' + the_item, x = item_indent,  y = item_spacing )
