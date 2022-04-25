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
        
        self.set(size=size, color=color, reserved_y=reserved_y, align=align,
                 va=va, opacity=opacity, font=font)

	    # Init the text object
        super().__init__(textin, x=x, y=y, width='100%', height=None, margin=0,
                         size=size, font=self.font, color=color,
                         opacity=opacity, usetex=None, va=va,
                         align=align, **kwargs)

