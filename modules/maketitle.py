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

def maketitle(titlein, author, subtitle=None, date=None):
    """
        Function to create the presentation title slide
    """

    #Check if we have titleslide in theme
    if document._theme != None:
        title_size = int(document._theme.get('titleslide','title_size'))
        title_color = document._theme.get('titleslide','title_color')
        author_color = document._theme.get('titleslide','author_color')
        date_color = document._theme.get('titleslide','date_color')
        author_size = int(document._theme.get('titleslide','author_size'))
        date_size = int(document._theme.get('titleslide','date_size'))
        subtitle_color = document._theme.get('titleslide','subtitle_color')
        subtitle_size = int(document._theme.get('titleslide','subtitle_size'))

    else:
        title_size = 40
        title_color = '#3333b3'
        author_color = "#888888"
        date_color = author_color
        author_size = 30
        date_size = 15
        subtitle_size = 30
        subtitle_color = author_color
        
    if date == None:
        date = datetime.datetime.now().strftime("%d/%m/%Y")

    begingroup(y="center")
    text(titlein, width="750", y=0, color=title_color, size=title_size, align='center')
    text(author, width="750", y="+1.5cm", color=author_color, size=author_size, align='center')
    
    if subtitle != None:
        text(subtitle, width="750", y="+1cm", color=subtitle_color, size=subtitle_size)
    
    text(date, width="750", y="+0.1cm", color=date_color, size=date_size)
    endgroup()
