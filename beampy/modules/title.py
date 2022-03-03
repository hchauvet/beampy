# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy.core.store import Store
from beampy.modules.text import text

class title(text):

    def __init__(self, textin , x=None, y=None, size=None, color=None,
                 reserved_y=None, align=None, va=None, opacity=None, font=None,
                 *args, **kwargs):
        """
            Add a title to a slide
        """

        # self.register()
        self.name = 'title'
        
        self.set(size=size, color=color, reserved_y=reserved_y, align=align,
                 va=va, opacity=opacity, font=font)

    	# Update the signature of the __init__ call
        self.update_signature(textin, x, y, size=size, color=color,
                              reserved_y=reserved_y, align=align, va=va,
                              opacity=opacity, font=font, **kwargs)

        # Load default from theme
        # This method alse set as attribute the signature arguments
        self.apply_theme(parent='text')

	    # Init the text object
        super().__init__(textin, x=self.x, y=self.y, width='100%', height=None, margin=0,
                         size=self.size, font=self.font, color=self.color,
                         opacity=self.opacity, usetex=None, va=self.va,
                         align=self.align, **kwargs)
