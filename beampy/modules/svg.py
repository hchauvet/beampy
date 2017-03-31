# -*- coding: utf-8 -*-
"""
@author: hugo

Module to write raw svg commands in slides
"""

from beampy import document
from beampy.functions import (getsvgwidth, getsvgheight)
from beampy.modules.core import beampy_module
from beampy.functions import convert_unit

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
 
        
        
class rectangle(svg):
    
    def __init__(self, **kwargs):
        """
            Create an svg rectangle
            
            Arguments:
            -x['center']: horizontal position in the slide
            -y['auto']: vertical position in the slide
            
            -color: the svg colorname to fill your rectangle
            -linewidth: the with of the stroke line
            -opacity: the value of the rectangle opacity from 0 to 1
            -edgecolor: the color of the rectangle edges
            
        """
        
        #The input type of the module 
        self.type = 'svg'
        
        #Add args to the module 
        self.check_args_from_theme( kwargs )
        
        
        #Build style for the rectangle
        beampy_svg_kword = {'color': 'fill',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity',
                            'edgeolor': 'stroke'}
        
        style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))
                
        self.content = '<rect width="{width}" height="{height}" style="{style}" />'.format(width=self.width, height=self.height, style=style)
        
        #Register the module 
        self.register()


class line(svg):
    
    def __init__(self, x2, y2, **kwargs):
        """
            Create an svg line
            
            # Arguments:
            
            -x["center"]: horizontal position in the slide
            -y["auto"]: vertical position in the slide
            -x2: the horizontal position of the end point
            -y2: the vertical position of the end point
            
            -color: the svg colorname to fill your rectangle
            -linewidth: the with of the stroke line
            -opacity: the value of the rectangle opacity from 0 to 1
            
            # exemple:
            
            line(x=0, y="20px", x2="40px", y2="20px", color="crimson")
        """
        
        #The input type of the module 
        self.type = 'svg'
        
        #Add args to the module 
        self.check_args_from_theme( kwargs )
        self.x2 = x2
        self.y2 = y2
        self.args['x2'] = self.x2
        self.args['y2'] = self.y2
        
        #convert unit of x2 and y2
        self.x2 = convert_unit(self.x2)
        self.y2 = convert_unit(self.y2)
        
        #Build style for the rectangle
        beampy_svg_kword = {'color': 'stroke',
                            'linewidth': 'stroke-width',
                            'opacity': 'opacity'}
        
        style = ''
        for kw in beampy_svg_kword:
            if hasattr(self, kw):
                style += '%s:%s;'%(beampy_svg_kword[kw], getattr(self,kw))
                
        self.content = '<line x1="0" y1="0" x2="{x2}px" y2="{y2}px" style="{style}"/>'.format(x2=self.x2, y2=self.y2, style=style)
        
        #Register the module 
        self.register()


def hline(y, **kwargs):
    """
        Create an horizontal line at y position
    """
    
    y = convert_unit(y)
    y = '%spx'%y
    
    return line(x=0, y=y, x2='%spx'%document._width, y2=y, **kwargs)
    
