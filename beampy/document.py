# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:28:59 2015

@author: hugo
"""
from ConfigParser import SafeConfigParser
from beampy.statics.default_theme import THEME
#Auto change path
#import beampy
#bppath =  str(beampy).split('beampy')[1].split('from')[-1].strip().replace("'",'')+'beampy/'
import os 
bppath = os.path.dirname(__file__) + '/'

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
    _theme = THEME
    _cache = None 
    _pdf_animations = False 
    
    #Define path to external commands
    _external_cmd = {"inkscape": "inkscape",
                     "dvisvgm": "dvisvgm",
                     "pdfjoin": "pdfjoin",
                     "ffmpeg": "ffmpeg",
                     "pdf2svg": "pdf2svg"}

    def __init__(self, width=800, height=600, guide = False, text_box = False, optimize=True, cache=True):
        """
            Create document to store slides

            options
            -------

            - width[800]: with of slides

            - height[600]: height of slides

            - guide[False]: Draw guide lines on slides to test alignements

            - text_box[False]: Draw box on slide elements to test width and height detection of elements (usefull to debug placement)

            - optimize[True]: Optimize svg using scour python script. This reduce the size but increase compilation time

            - cache[True]: Use cache system to not compile slides each times if nothing changed!
        """

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
        #self.load_theme(bppath+'/statics/default.theme')

        if optimize == False:
            document._optimize_svg = False

        if cache:
            document._cache = cache

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
        document._theme = THEME
        document._cache = None



