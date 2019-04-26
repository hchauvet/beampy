# -*- coding: utf-8 -*-

# Default theme of Beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

THEME = {}

THEME['document'] = {
    'format': 'html5', #could be svg // pdf // html5
    'width': 800,
    'height': 600,
    'optimize': True,
    'resize_raster':True,
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

THEME['slide'] = {
    'background': "white",
    'layout': None, #Could be changed to a function that will decorate the current slide with elements
                    #this can be used to create a specific layout for a theme 
                    #Could also be a string that refer to the key of the LAYOUT[key] dict if you need several layouts 
                    #for a presentation
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
    'va': '',
    'opacity':1,
    'extra_packages': []
}


THEME['title'] = {
    'size': 28,
    'font': 'CMR',
    'color': 'ForestGreen',
    'x': {'shift':0.5, 'unit':'cm'},
    'y': {'shift':1.25, 'unit':'cm'},
    'reserved_y': '1.5cm',
    'align': '',
    'va': 'baseline',
    'opacity': 1
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
    'subtitle_size':20,
    'template': None #here you redefine a link to a function "def mytitle(titlein, author, subtitle, date, args)"" that is executed in maketitle to replace the default template
}

THEME['tableofcontents'] = {
    'width': None,
    'height': None,
    'x': 25,
    'y': 'center',
    'section_yoffset': 50,
    'subsection_xoffset': 20,
    'subsection_yoffset': 10,
    'section_style': 'round',
    'subsection_style': None,
    'section_decoration_color': THEME['title']['color'],
    'section_decoration_size': 13,
    'section_number_color': 'white',
    'section_text_color': THEME['title']['color'],
    'subsection_text_color': THEME['text']['color'],
    'subsection_decoration_color': 'gray',
    'subsection_decoration_size': 13/2,
    'hidden_opacity': 0.2
}

THEME['video'] = {
    'width': None,
    'height': None,
    'x': 'center',
    'y': 'auto',
    'autoplay': False,
    'control': True,
    'still_image_time': 0.0,
    'embedded': True
}

THEME['animatesvg'] = {
    'start': 0,
    'end': 'end',
    'x': 'center',
    'y': 'auto',
    'width': None,
    'fps': 25,
    'autoplay': False
}

THEME['tikz'] = {
    'x': 0,
    'y': 0,
    'tikz_header': None,
    'tex_packages': None,
    'latex_pre_tikzpicture': None,
    'figure_options': None,
    'figure_anchor': 'top_left'
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
    'width':None,
    'item_layers': None
}

THEME['line'] = {
    'x':'center',
    'y':'auto',
    'color': THEME['title']['color'],
    'linewidth': '2px',
    'opacity': 1
}

THEME['rectangle'] = {
    'x':'center',
    'y':'auto',
    'color': THEME['title']['color'],
    'linewidth': '2px',
    'opacity': 1,
    'edgecolor': THEME['text']['color'],
    'height': '10px',
    'width': '%spx'%(THEME['document']['width']),
    'rx':0,
    'ry':0,
    'svgfilter': None,
    'svgclip': None
}

THEME['circle'] = {
    'x':'center',
    'y':'auto',
    'color': THEME['title']['color'],
    'linewidth': '1px',
    'opacity': 1,
    'edgecolor': THEME['title']['color'],
    'r': '3px'
}

THEME['box'] = {
    'rounded': 10,
    'linewidth': 1,
    'color': THEME['title']['color'],
    'head_height': None,
    'shadow': False,
    'background_color': 'white',
    'title_color': 'white',
    'title_align': 'left',
    'title_xoffset': 10,
    'auto_height_margin': 15
}
