# -*- coding: utf-8 -*-
"""
Part of beampy project.

Placement class for relative placement of elements in slides

@author: hugo
"""
from beampy.function import dict_deep_update

DEFAULT_X = {'align': 'left', 'reference': 'slide', 'shift': 0, 'unit': 'cm'}
DEFAULT_Y = {'align': 'left', 'reference': 'slide', 'shift': 0, 'unit': 'cm'}

class positionner():

    def __init__(self, x, y, width, height):
        """
            This class need position x and y of the element
            
            width and height is the size of the svg or html object
        """
        
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        #Need to convert x, y to a standart dict 
        self.convert_position()
        
        #Compute elements anchors
        self.compute_anchors()
        
    def compute_anchors(self):
        """
            Compute the anchors for the element self.left self.right self.top and self.bottom
        """
        
        #Bottom
        self.bottomx = self.height
        
        #top
        self.top = 0
        
        #left
        self.left = 0
        
        #right 
        self.right = self.width
        
        #xcenter
        self.xcenter = self.width/2.
        
        #ycenter
        self.ycenter = self.height/2.
        
        
    def convert_position(self):
        #Function to convert position of an element
        
        tmpx = DEFAULT_X
        tmpy = DEFAULT_Y
        
        #Check if x or y are only floats  
        if type(self.x) == type(float)()) or type(self.x) == type(int()):
            tmpx['shift'] = self.x
        
        elif type(self.x) == type(dict()):
            tmpx = dict_deep_update(tmpx, self.x)
            
        else:
            print("[Error] x position need to be a float or a dict")
            
            
        if type(self.y) == type(float)()) or type(self.y) == type(int()):
            tmpy['shift'] = self.y
        
        elif type(self.y) == type(dict()):
            tmpy = dict_deep_update(tmpx, self.y)
            
        else:
            print("[Error] y position need to be a float or an int or a dict")
            
            
        #Store the dict for positions
        self.x = tmpx
        self.y = tmpy
        
        #Convert position unit
        if self.x['unit'] in ['cm', 'pt', 'px', 'mm']:
            self.x['shift'] = float( convert_unit( '%f%s'%(self.x['shift'], self.x['unit']) ) )
            
        if self.y['unit'] in ['cm', 'pt', 'px', 'mm']:
            self.y['shift'] = float( convert_unit( '%f%s'%(self.y['shift'], self.y['unit']) ) )
            
    def place_element(self, relative_element=None, abs_xposition=None, abs_yposition=None):
        """
            Method to place the given element. This method is used by renders.py in 
            the place_content function
            
            absolute position is used when alignement = "center" and for align = "auto"
            
            relative_element is used when reference = "previous" or an other element 
        """
        
        if self.x['align'] in ['center', 'auto'] and abs_xposition != None:
            self.x['shift'] = abs_xposition
            
        if self.y['align'] in ['center', 'auto'] and abs_yposition != None:
            self.y['shift'] = abs_yposition
            
        
        
        
    def __add__(self):
        #Define addition
        
        pass
        
        
        

