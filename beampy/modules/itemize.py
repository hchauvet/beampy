# -*- coding: utf-8 -*-
"""
@author: devauch

Class to manage item lists for beampy
"""

from beampy import document
from beampy.modules.text import text
from beampy.modules.core import begingroup, endgroup
from beampy.functions import convert_unit

def color_text( textin, color ):
	
	'''
		Adds Latex color to a string.
	'''
	
	if "#" in    color:
		textin = r'{\color[HTML]{%s} %s }'%( color.replace('#','').upper(), textin)
	
	else:
		textin =r'{\color{%s} %s }'%( color, textin)

	return textin


def itemize( items_list, x='center', y='auto', item_style = 'bullet', item_spacing = '+1cm' , item_indent = '0cm', item_color = 'default', text_color = 'default', width=None ):
	
	'''
	
	Generates a list or an enumeration.
	
	'''
	
	number = 1
	
	if item_color == 'default' :
		item_color = document._theme['title']['color']
	
	if text_color == 'default' :
		text_color = document._theme['text']['color']
	
	
	if width!=None:
		in_width = float(convert_unit(width)) - float(convert_unit(item_indent))
	else:
		in_width = float(document._width) - float(convert_unit(item_indent))
    	    
	begingroup(width=width, x=x, y=y)
	
	for i, the_item in enumerate(items_list) :
		
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
    	    
		if i == 0 :
			text( item_char + r' ' + the_item, x = item_indent,  y = 0, width=in_width )
		else:
			text( item_char + r' ' + the_item, x = item_indent,  y = item_spacing, width=in_width )
		
	endgroup()
