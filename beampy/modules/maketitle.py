# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.modules.text import *
from beampy.modules.core import *
import datetime

def maketitle(titlein, author=None, subtitle=None, date=None):
    """
        Function to create the presentation title slide
    """

    args = {"title_size": "", "title_color": "", "author_color": "",
            "date_color": "", "author_size": "", "date_size": "",
            "subtitle_color": "", "subtitle_size": ""}

    #Load theme properties
    load_args_from_theme('titleslide', args)

    if date in ('Today', 'today', 'now'):
        date = datetime.datetime.now().strftime("%d/%m/%Y")

    begingroup(y="center")

    text(titlein, width="750", y=0, color=args['title_color'], size=args['title_size'], align='center')

    if author != None :
        text(author, width="750", y="+1.5cm", color=args['author_color'], size=args['author_size'], align='center')

    if subtitle != None:
        text(subtitle, width="750", y="+1cm", color=args['subtitle_color'], size=args['subtitle_size'])

    if date != None:
        text(date, width="750", y="+20", color=args['date_color'], size=args['date_size'])

    endgroup()
