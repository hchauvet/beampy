# -*- coding: utf-8 -*-
"""
@author: hugo

Module to write raw svg commands in slides
"""

from beampy import document
from beampy.functions import (getsvgwidth, getsvgheight)
from beampy.modules.core import beampy_module

import tempfile
import os 
    
class svg( beampy_module ):


    def __init__(self, svg_content, **kwargs):
        """
            Insert svg content to a presentation
            
            # arguments
            
            - svg_content: the raw svg string 
            
            ## Optionals
            
            - x['center']: x coordinate of the image
                           'center': center image relative to document._width
                           '+1cm": place image relative to previous element

            - y['auto']: y coordinate of the image
                         'auto': distribute all slide element on document._height
                         'center': center image relative to document._height (ignore other slide elements)
                         '+3cm': place image relative to previous element
        """
        
        
        #The input type of the module 
        self.type = 'svg'
        
        #Add args to the module 
        self.load_args( kwargs )
        
        #Save the content 
        self.content = svg_content
        
        #Register the module 
        self.register()
        
        

    def render(self):
        """
            The render of an svg part 
        """
        
        #TODO: Parse the svg to get height and width 
        #Need to get the height and width of the svg command 
        tmpsvg = '<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" xmlns:xlink="http://www.w3.org/1999/xlink">%s</svg>'%self.content

        #Need to create a temp file
        tmpfile, tmpname = tempfile.mkstemp(prefix='beampytmp')
        with open( tmpname + '.svg', 'w' ) as f:
            f.write( tmpsvg )

        svg_width =  getsvgwidth(tmpname + '.svg')
        svg_height = getsvgheight(tmpname + '.svg')
        
        #remove the svg
        os.remove( tmpname + '.svg' )
        
        #Update the final svg size
        self.update_size(svg_width, svg_height)
        #Add the final svg output of the figure
        self.svgout = self.content
        
        
        
