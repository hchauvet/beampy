# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:28:59 2015

@author: hugo
"""
from ConfigParser import SafeConfigParser
#TODO auto change path 
import beampy
bppath =  str(beampy).split('beampy')[1].split('from')[-1].strip().replace("'",'')+'beampy/'

class document():
    """
       Main function to define the document style etc...
    """
    #Global variables to sotre data
    _contents = {}
    _global_counter = {}
    _width = 0
    _height = 0
    _guide = False
    _text_box = False
    _optimize_svg = True
    _output_format='html5'
    _theme = None
    
    def __init__(self, width=800, height=600, guide = False, text_box = False, optimize=True):
        #reset if their is old variables
        self.reset()
        #A document is a dictionnary that contains all the slides
        self.data = self._contents
        #To store different counters 
        self.global_counter = self._global_counter
     
        #Width and height of the document
        self.width = width
        self.height = height
        self.set_size()
        
        #To add guide on each slides 
        self.guide = guide
        document._guide = guide
        
        self.text_box = text_box
        document._text_box = text_box
        
        #Load the default theme
        self.load_theme(bppath+'/statics/default.theme')        
        
        if optimize == False:
            document._optimize_svg = False
            
    def set_size(self):
        document._width = self.width
        document._height = self.height
        
    def reset(self):
        document._contents = {}
        document._global_counter = {}
        document._width = 0
        document._height = 0
        document._guide = False
        document._text_box = False
        document._theme = None

    def load_theme(self, pathtotheme):
        """
            Load a theme define in a config file conform to standard 
            python ConfigParser module see default.theme for exemple
        """
    
        #Load a theme
        themeparser = SafeConfigParser()
        themeparser.read(pathtotheme)
        
        #Add the theme parser to the document class
        self.themeparser = themeparser
        document._theme = self.themeparser
        