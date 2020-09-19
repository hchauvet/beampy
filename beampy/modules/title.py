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
        
        if self.width is None:
            self.width = document._width
            
        self.initial_width = self.width
        #Re-compute the title when color or size is changed
        self.args_for_cache_id = ['initial_width', 'color', 'size',
                                  'align', 'opacity', 'nofont']

        # Init global store keys if not already created 
        if 'css_fonts' not in document._global_store:
            document._global_store['css_fonts'] = {}

        if 'svg_glyphs' not in document._global_store:
            document._global_store['svg_glyphs'] = {}
            
        if self.attrtocache is None:
            self.attrtocache = []
            
        if self.nofont:
            self.attrtocache += ['svg_glyphsids']
        else:
            self.attrtocache += ['css_fontsids']

        self.svg_glyphsids = []
        self.css_fontsids = []

        self.height = None

        #Register this module
        self.register()
        
        #Add the title to the slide
        document._slides[self.slide_id].title = self
