# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import (gcs, load_args_from_theme, check_function_args,
    inherit_function_args)
from beampy.modules.text import render_text
from beampy.geometry import positionner

def title( title_text , **kwargs):
    """
        Add a title to a slide
    """

    #Check function arguments from THEME
    args = check_function_args(title, kwargs)
    #Add text arguments because we use the text render
    args = inherit_function_args('text', args)

    if args['width'] == None:
        args['width'] = document._width
    
    titleout = {'type': 'svg',
                "positionner": positionner( args['x'], args['y'],
                                            width=args['width'], height=None),
                'content':title_text,
                "args":args,
                "render": render_text }

    titleout['positionner'].id = 'title'
    document._contents[gcs()]['title']=titleout
