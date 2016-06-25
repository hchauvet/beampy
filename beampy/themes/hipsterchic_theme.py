# -*- coding: utf-8 -*-

# HipsterOrange Theme for beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

# version: 0.1
# Author: H. chauvet

####################### Define a new maketitle layout ##########################


########################## THEME DICT ##########################################

THEME = {}

THEME['document'] = {
    'format': 'html5', #could be svg // pdf // html5
    'width': 800,
    'height': 600
}

THEME['text'] = {
    'size':20,
    'font':'CMR',
    'color':'#000000',
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
    'color': 'DarkOrange',
    'x': {'shift':0.5, 'unit':'cm'},
    'y': {'shift':1.2, 'unit':'cm'},
    'reserved_y': '1.5cm',
    'align': '',
    'va': 'baseline'
}


THEME['maketitle'] = {
    'title_color':THEME['title']['color'],
    'author_size':THEME['text']['size'],
    'background-color': 'WhiteSmoke',
    'date_color':'#888888',
    'subtitle_color':'#888888',
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

##################################################################

from beampy.modules.core import group
from beampy.modules.text import text
from beampy.document import document
from beampy.modules.tikz import tikz

def hipstertitle(titlein, author= None, subtitle = None, date= None):

    
    args = THEME['maketitle']
    
    #TODO: the rectangle with a raw svg command
    tikz(r'\draw[fill={color}, line width=1.5pt] (0,0) rectangle (100,100);'.format(color=args['background-color']),
     x=0, y=0)

    with group(x=0.015, y='center', width=document._width-document._width*0.015):

        text(r"{\scshape %s}"%(titlein), x= 0, width=document._width*0.9, 
        y=0, color=args['title_color'], size=args['title_size'], 
        align='left')

        #TODO: the line with a raw svg command not tikz
        tikz(r'\draw[color={color}, line width=1.5pt] (0,0) -- ++ (800,0);'.format(color=args['title_color']),
         x=0, y='+0.2cm')

        if author != None :
            a = text(author, x=0, y="+0.6cm", color=args['author_color'],
            size=args['author_size'], align='left', width=document._width*0.45)

        if subtitle != None:
            st = text(r"\textit{%s}"%(subtitle), x={"align":'right', 'shift':0.02},
                 y=a.bottom+{"align":"bottom", "shift":0},
                 color=args['subtitle_color'], size=args['subtitle_size'],
                 width=document._width*0.45, align='left')

    if date != None:
        text(date, x='center', y={"align":'bottom', 'shift':0.05},
        color=args['date_color'], size=args['date_size'])

THEME['maketitle']['template'] = hipstertitle
