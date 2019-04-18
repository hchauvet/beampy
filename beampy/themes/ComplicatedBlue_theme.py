# -*- coding: utf-8 -*-

# HipsterOrange Theme for beampy
# Main keys of the dict should be the name of the beampy modules or class
# Each modules default options need to be defined here!

# version: 0.1
# Author: H. chauvet & Olivier!



########################## THEME DICT ##########################################


THEME = {}

lead_color = 'blue'
standard_text_color = 'black'
shaded_text_color = 'gray'


THEME['document'] = {
    'format': 'html5', #could be svg // pdf // html5
    'width': 800,
    'height': 600
}

THEME['slide'] = {
    'background': "#ffffff"   
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
    'subtitle_color':shaded_text_color,
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

####################### Define a new maketitle layout ##########################

from beampy.commands import *

def theme_maketitle(titlein, author = [], affiliation = None, meeting = None, lead_author = None, date=None ):
    """
        Function to create the presentation title slide
    """

    # get_command_line(maketitle)
    # Check function arguments from THEME
    args = THEME['maketitle']

    try:
        author[lead_author] = r'\underline{' + str(author[lead_author]) + '}'
    except:
        pass

    author_string = ', '.join(author)

    if date in ('Today', 'today', 'now'):
        date = datetime.datetime.now().strftime("%d/%m/%Y")

    with group(y="center"):

        text(titlein, width=750, y=0, color=args['title_color'], size=args['title_size'], align='center')

        if author != []:
            text( author_string, width=750, y="+1.5cm", color=args['author_color'], size=args['author_size'], align='center')

        if affiliation is not None:
            text(affiliation, width=750, y="+1cm", color=args['subtitle_color'], size=args['subtitle_size'])
            
        if meeting is not None:
            text(meeting, width=750, y="+1cm", color=args['subtitle_color'], size=args['subtitle_size'])

        if date is not None:
            text(date, width=750, y="+1cm", color=args['date_color'], size=args['date_size'])

THEME['maketitle']['template'] = theme_maketitle


def background_layout():

    from beampy.document import document
    from beampy.geometry import bottom

    N = len( document._slides )
    cur_slide = int(document._curentslide.split('_')[1]) + 1

    slide_width = float(document._width)
    slide_height = float(document._height)

    # Create a progress bar
    available_width = slide_width
    prog = rectangle(x=0, y={'align':'bottom', 'anchor':'bottom', 'shift':0}, height=7,
                    width=(cur_slide/float(N) * available_width), color='lightblue',
                    edgecolor=None)

    # Display the page number 
    t1 = text('%i/%i'%(cur_slide, N),
              x={"shift": 0.01, "align":"right",
                 "anchor":"right"},
              y=prog.top-bottom(5), size=13, color='LightBlue')

# Register the layour function
THEME['slide']['layout'] = background_layout
