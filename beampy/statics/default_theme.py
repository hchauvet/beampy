# -*- coding: utf-8 -*-

# Default theme of Beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

THEME = {}

THEME['document'] = {
    'width': 800,
    'height': 600,
    'optimize': True,
    'cache': True,
    'guide': False,
    'text_box': False,
    'html': {
        'background_color': 'black'
        },

    'external_app': {"inkscape": "auto",
        "dvisvgm": "auto",
        "pdfjoin": "auto",
        "video_encoder": 'auto',
        "pdf2svg": "auto"}
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
    'color': 'ForestGreen',
    'x': {'shift':0.5, 'unit':'cm'},
    'y': {'shift':1.2, 'unit':'cm'},
    'reserved_y': '1.5cm',
    'align': '',
    'va': 'baseline'
}

THEME['link'] = {
    'fill':THEME['title']['color']
}

THEME['maketitle'] = {
    'title_size':30,
    'title_color':THEME['title']['color'],
    'author_size':THEME['text']['size'],
    'author_color':'black',
    'date_size':15,
    'date_color':'#888888',
    'subtitle_color':'#888888',
    'subtitle_size':20
}

THEME['video'] = {
    'width':None,
    'height':None,
    'x':'center',
    'y':'auto',
    'autoplay':False,
    'control':True,
    'still_image_time':0.0
}

THEME['animatesvg'] = {
    'start':0,
    'end':'end',
    'x':'center',
    'y':'auto',
    'width':None,
    'fps':25,
    'autoplay':False
}

THEME['tikz'] = {
    'x':0,
    'y':0,
    'tikz_header':None,
    'tex_packages':None,
    'figure_options':None,
    'figure_anchor':'top_left'
}

THEME['figure'] = {
    'x':'center',
    'y':'auto',
    'width':None,
    'height':None
}

THEME['cite'] = {
    'x':'center',
    'y':{'shift':0.9, 'unit':'height'},
    'color':THEME['title']['color'],
    'size':10
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
