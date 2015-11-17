# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs, load_args_from_theme
from beampy.modules.text import render_text

def title( title, usetex=True):
    """
        Add a title to a slide
    """

    args = {"x":"" , "y": "", "reserved_y":"",
    "font": "", "font-size": None, "color": "", 'usetex': usetex,
    'align':'', 'va':'baseline' }

    #Load theme properties
    load_args_from_theme('title', args)
        
    titleout = {'type': 'svg', 'content':title, "args":args, "render": render_text }

    document._contents[gcs()]['title']=titleout
