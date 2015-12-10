# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage pandas table output as latex for beampy
"""


#TODO: Add *args for pandas to_latex(args)
def table(pandas_table, x='center', y='auto', width=None, text_color="default"):
    """
        Function to output pandas table in beampy presentation
        
        pandas -> to_latex() is used to output the table 
        
    """
    
    if width == None:
        width = str(document._width)
    else:
        width = str(width)

	if text_color == 'default' :
		text_color = document._theme['text']['color']
		
    args = {"x":str(x), "y": str(y), "width": width,
            "font-size": size, "color": text_color }
            
            
def table_render(latex_table, args):
    #TODO
    pass



    
