# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.modules.text import text
from beampy.modules.core import *
from beampy.functions import get_command_line
import datetime

def maketitle(titlein, author=None, subtitle=None, date=None):
    """
        Function to create the presentation title slide
    """
    #get_command_line(maketitle)
    #Check function arguments from THEME
    args = check_function_args(maketitle, {})

    if date in ('Today', 'today', 'now'):
        date = datetime.datetime.now().strftime("%d/%m/%Y")

    if args['template'] == None:
        with group(y="center"):

            text(titlein, width=750, y=0, color=args['title_color'], size=args['title_size'], align='center')

            if author != None :
                text(author, width=750, y="+1.5cm", color=args['author_color'], size=args['author_size'], align='center')

            if subtitle != None:
                text(subtitle, width=750, y="+1cm", color=args['subtitle_color'], size=args['subtitle_size'])

            if date != None:
                text(date, width=750, y="+20", color=args['date_color'], size=args['date_size'])

    else:
        args['template'](titlein, author, subtitle, date, args)
