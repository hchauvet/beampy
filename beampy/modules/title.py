# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs
from beampy.modules.text import render_text

def title( title, usetex=True):
    """
        Add a title to a slide
    """

    args = {"x":"0.5cm" , "y": "1.2cm", "reserved_y":"1.4cm",
    "font": "CMR", "font-size": 28, "fill": "#3333b3", 'usetex': usetex,
    'align':'', 'ha':'left', 'va':'baseline' }

    #Load theme properties
    if document._theme != None:
        args['fill'] = document._theme.get('title','color')
        args['size'] = document._theme.get('title','size')
        args['x'] = document._theme.get('title','x')
        args['y'] = document._theme.get('title','y')
        args['reserved_y'] = document._theme.get('title','yspace')
        
    titleout = {'type': 'svg', 'content':title, "args":args, "render": render_text }

    document._contents[gcs()]['title']=titleout
