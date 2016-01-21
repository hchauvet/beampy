# -*- coding: utf-8 -*-

# Default theme of Beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

THEME = {

'document':{
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
        "pdf2svg": "auto"} },

'text':{
    'size':20,
    'font':'CMR',
    'color':'#000000',
    'align':'',
    'x':'center',
    'y':'auto',
    'width':None,
    'usetex':True,
    'va': ''},

'title':{
    'size': 28,
    'font': 'CMR',
    'color': 'ForestGreen',
    'x': {'shift':0.5, 'unit':'cm'},
    'y': {'shift':1.2, 'unit':'cm'},
    'reserved_y': '1.5cm',
    'align': '',
    'va': 'baseline'},

'titleslide':{
    'title_size':30,
    'title_color':'ForestGreen',
    'author_size':20,
    'author_color':'black',
    'date_size':15,
    'date_color':'#888888',
    'subtitle_color':'#888888',
    'subtitle_size':20},

'link':{
    'fill':'ForestGreen'}

}
