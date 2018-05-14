# -*- coding: utf-8 -*-

# HipsterOrange Theme for beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

# version: 0.1
# Author: H. chauvet



########################## THEME DICT ##########################################

THEME = {}

THEME['document'] = {
    'format': 'html5', #could be svg // pdf // html5
    'width': 800,
    'height': 600
}

THEME['text'] = {
    'size': 20,
    'font': 'CMR',
    'color': '#000000',
    'align': '',
    'x': 'center',
    'y': 'auto',
    'width': None,
    'usetex': True,
    'va': ''
}


THEME['title'] = {
    'size': 28,
    'font': 'CMR',
    'color': 'DarkOrange',
    'x': 'center',
    'y': {'shift': 1.2, 'unit': 'cm'},
    'reserved_y': '1.5cm',
    'align': '',
    'va': 'baseline'
}


THEME['maketitle'] = {
    'title_color': THEME['title']['color'],
    'author_size': THEME['text']['size'],
    'background-color': 'WhiteSmoke',
    'date_color': '#888888',
    'subtitle_color': '#888888',
}

THEME['link'] = {
    'fill': THEME['title']['color']
}

THEME['itemize'] = {
    'x': 'center',
    'y': 'auto',
    'item_style': 'bullet',
    'item_spacing': '+1cm',
    'item_indent': '0cm',
    'item_color': THEME['title']['color'],
    'text_color': THEME['text']['color'],
    'width': None
}

##################################################################


####################### Define a new maketitle layout ##########################

from beampy.modules.core import group
from beampy.modules.text import text
from beampy.document import document
from beampy.modules.svg import hline, rectangle

def hipstertitle(titlein, author= None, subtitle = None, date= None):

    args = THEME['maketitle']

    rectangle(x=0, y=0, width=document._width,
              height=document._height, color=args['background-color'],
              edgecolor=None)

    with group(x=0.015, y='center', width=document._width-document._width*0.015):

        t = text(r"{\scshape %s}" % (titlein), x=0, width=document._width*0.9,
             y=0, color=args['title_color'], size=args['title_size'],
             align='left')

        hl = hline(y=t.bottom+"0.2cm", color=args['title_color'], linewidth='1.5pt')

        if author is not None :
            a = text(author, x=0, y=hl.bottom+20, color=args['author_color'],
                     size=args['author_size'], align='left',
                     width=document._width*0.45)

        if subtitle is not None:
            st = text(r"\textit{%s}" % (subtitle),
                      x={"align": 'right', 'shift': 0.02, 'anchor':'right'},
                      y=hl.bottom+{"anchor":"top", "shift": 20},
                      color=args['subtitle_color'], size=args['subtitle_size'],
                      width=document._width*0.45, align='left')

    if date is not None:
        text(date, x='center', y={"align":'bottom', 'shift':0.05},
             color=args['date_color'], size=args['date_size'])

THEME['maketitle']['template'] = hipstertitle
