# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs
from beampy.modules.text import text

class title( text ):

    def __init__(self, titlein , **kwargs):
        """
            Add a title to a slide
        """

        #Set the type as text
        self.type = 'text'
        #Check function arguments from THEME
        self.check_args_from_theme(kwargs)

        self.content = titlein

        self.svgtext = ''  # To store the svg produced by latex
        
        #Add text arguments because we use the text render
        self.load_extra_args('text')
        #Re-compute the title when color or size is changed
        self.args_for_cache_id = ['color','size']
        
        if self.width == None:
            self.width = document._width
        self.height = None

        #Add the title to the slide
        document._slides[gcs()].title = self

        #Register this module
        self.register()
