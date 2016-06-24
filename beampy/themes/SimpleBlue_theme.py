# -*- coding: utf-8 -*-

# HipsterOrange Theme for beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

# version: 0.1
# Author: H. chauvet & Olivier!



########################## THEME DICT ##########################################

THEME = {}

lead_color = 'SteelBlue'
standard_text_color = 'black'


THEME['document'] = {
    'format': 'html5', #could be svg // pdf // html5
    'width': 800,
    'height': 600
}

THEME['text'] = {
    'size':20,
    'font':'CMR',
    'color': standard_text_color,
    'align':'',
    'x':'center',
    'y':'auto',
    'width':None,
    'usetex':True,
    'va': ''
}

THEME['title'] = {
    'size': 28,
    'font': 'CMR',
    'color': lead_color,
    'x': {'shift':0.5, 'unit':'cm'},
    'y': {'shift':1.2, 'unit':'cm'},
    'reserved_y': '1.5cm',
    'align': '',
    'va': 'baseline'
}


THEME['maketitle'] = { # name should be 'titlepage' :-)
    'title_color':THEME['title']['color'],
    'author_size':THEME['text']['size'],
    'date_color':standard_text_color,
    'subtitle_color':standard_text_color,
}


THEME['link'] = {
    'fill':THEME['title']['color']
}

THEME['itemize'] = {
    'x':'center',
    'y':'auto',
    'item_style':'bullet',
    'item_spacing':'+1cm',
    'item_indent':'0cm',
    'item_color':THEME['title']['color'],
    'text_color':THEME['text']['color'],
    'width':None
}
