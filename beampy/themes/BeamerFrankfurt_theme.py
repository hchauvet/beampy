# -*- coding: utf-8 -*-

# This theme is a copy of the Beamer Frankfurt theme with the
# default color scheme
# It defines a headerbar with TOC 

# version: 0.1
# Author: H. chauvet 

THEME = {}

lead_color = '#3333b2' # The blue color
standard_text_color = 'Black'
shaded_text_color = 'Gray'


THEME['slide'] = {
    'background': "None"
}

THEME['title'] = {
    'size': 28,
    'font': 'CMR',
    'color': 'white',
    'x': '0.5cm',
    'y': 68,
    'reserved_y': '3.4cm',
    'align': '',
    'va': 'baseline'
}

THEME['maketitle'] = {
    'title_color': THEME['title']['color'],
    'author_size': 20,
    'date_color': standard_text_color,
    'subtitle_color': shaded_text_color,
    'lead_author_color': 'Green',
    'meeting_color': standard_text_color,
    'affiliation_color': shaded_text_color,
    'affiliation_size': 17
}

THEME['box'] = {
    'color': lead_color,
    'linewidth': 0,
    'background_color': '#ebebf9',
    'shadow': True
}

THEME['cite'] = {
    'color': shaded_text_color,
}

THEME['itemize'] = {
    'item_color':lead_color,
    'text_color':standard_text_color,
}

THEME['line'] = {
    'color': lead_color,
}

THEME['rectangle'] = {
    'color': lead_color,
    'edgecolor': lead_color
}

THEME['circle'] = {
    'color': lead_color,
    'edgecolor': lead_color
}

THEME['tableofcontents'] = {
    'width': '90%',
    'height': None,
    'x': 'center',
    'y': 'center',
    'section_yoffset': 50,
    'subsection_xoffset': 10,
    'subsection_yoffset': 10,
    'section_style': 'round',
    'subsection_style': 'round',
    'section_decoration_color': lead_color,
    'section_decoration_size': 13,
    'section_number_color': 'white',
    'section_text_color': lead_color,
    'subsection_text_color': standard_text_color,
    'subsection_decoration_color': shaded_text_color,
    'subsection_decoration_size': 5,
    'hidden_opacity': 0.2
}

THEME['link'] = {
    'fill':lead_color
}


######################### Define the headerbar #####################################
from beampy.document import document
from beampy.modules.svg import rectangle, circle
from beampy.modules.text import text
from beampy.modules.core import group
from beampy.modules.toc import get_visibles_indices
from beampy.functions import convert_unit
from beampy.geometry import distribute

def create_header_bar():

    if len(document._TOC) == 0:
        bluerect = rectangle(x=0, y=0, height=28*1.6,
                             color=lead_color, edgecolor=lead_color)
        bluerect.first()
        # BUG Change the position of the title as we don't have the header bar
        print('No table of content, their is a bug to set the position of the title dynamically in BeamerFrankfurt Theme')
        print('''Please add in your file after doc = document
        doc._theme['title']['y'] -= 35
        doc._theme['title']['reserved_y'] = '1.8cm'
        ''')
        
    else:
        rtop = rectangle(x=0, y=0, height=35, color='black', edgecolor='black')
        bluerect = rectangle(x=0, y=rtop.bottom+0, height=28*1.6,
                             color=lead_color, edgecolor=lead_color)
        bluerect.first()
        
        cpt_title = 0
        cur_toc = document._slides[document._curentslide].TOCposition
        visibles_toc_pos = get_visibles_indices(document._curentslide,
                                                currentsection=True)
        last_pos = document._TOC.index(cur_toc)
        last_level1_pos = 0
        
        for i, toc in enumerate(document._TOC):
            if toc['level'] == 0:
                cpt_title += 1
            if toc['level'] == 1:
                if i in visibles_toc_pos and i <= last_pos:
                    last_level1_pos = i
        
        group_width = None
        groups = [] # store group with toc title and subtitle circle
        elems = []
        for i, toc in enumerate(document._TOC):
            if i in visibles_toc_pos and i <= last_pos:
                selected_opacity = 1
            else:
                selected_opacity = 0.5
        
            if i == last_level1_pos:
                circle_color = 'white'
            else:
                circle_color = 'black'
        
            if toc['slide'] <= document._global_counter['slide']:
                slidelink = '#%i-0' % (toc['slide'])
            else:
                slidelink = '#%i-0' % (document._global_counter['slide'])
        
            if toc['level'] == 0:
                if len(elems) > 0:
                    g = group(elems, x=0, y=5, width=group_width)
                    groups += [g]
                    elems = []
                
                t1 = text(r'\href{%s}{%s}' % (slidelink, toc['title']), x=0,
                          y=0, size=10, color='white',
                          opacity=selected_opacity, width=group_width)
                elems += [t1]
                t2 = None
                
            if toc['level'] == 1:
                if t2 is None:
                    xt = 2
                else:
                    xt = t2.right+2
                    
                t2 = circle(x=xt, y=t1.top+15, color=circle_color,
                            edgecolor='white', opacity=selected_opacity)
                elems += [t2]
                
        if len(elems) > 0:
            g = group(elems, x=0, y=0, width=group_width)
            groups += [ g ]
        
        # Compute the horizontal position for groups
        # The first element at the same x than the title
        groups[0].positionner.update_x(THEME['title']['x'])
        # groups[0].positionner.update_y((rtop.height-groups[0].height)/2)
        # The last element with the same margin as the first element 
        groups[-1].positionner.update_x(document._width-(groups[-1].width+THEME['title']['x']).value)
        groups[-1].positionner.update_y(groups[0].top+0)
        #Compute the available width
        available_width = document._width - (groups[-1].width+THEME['title']['x']).value
        
        for e in groups[1:-1]:
            e.positionner.update_y(groups[0].top+0)
            if e.width.value is None or e.height.value is None:
                e.width.run_render()
                
        if len(groups) > 2:
            distribute(groups[1:-1], 'hspace', available_width,
                       offset=(groups[0].width+THEME['title']['x']).value)
            
# Register the layour function
THEME['slide']['layout'] = create_header_bar


######## FOR THE TITLE PAGE #############
import datetime
from beampy.utils import box
from beampy.functions import color_text
import sys

def theme_maketitle(titlein, author = [], affiliation = None, meeting = None, lead_author = None, date=None ):
    """
        Function to create the presentation title slide
    """

    # get_command_line(maketitle)
    # Check function arguments from THEME
    args = THEME['maketitle']

    if lead_author is not None and len(author) > lead_author:
        print('Color author: %s in %s' % (author[lead_author],
                                          args['lead_author_color']))
        
        author[lead_author] = color_text(author[lead_author],
                                         args['lead_author_color'])
        
    author_string = '\hspace{0.7cm} '.join(author)

    if date in ('Today', 'today', 'now'):
        date = datetime.datetime.now().strftime("%d/%m/%Y")

    if isinstance(affiliation, list):
        affiliation = r'\\'.join(affiliation)
        
    with group(y="center"):

        with box(width='85%', y=0, auto_height_margin=20, background_color=lead_color) as tg:
            text(titlein, color=args['title_color'],
                 size=args['title_size'], align='center',
                 y=0, x='center', width='90%')

        if len(author) > 0:
            text(author_string, width='80%', y=tg.bottom+"1.5cm",
                 color=args['author_color'], size=args['author_size'],
                 align='center')

        if affiliation is not None:
            text(affiliation, width='90%', y="+1cm",
                 color=args['affiliation_color'], size=args['affiliation_size'],
                 align='center')

        if meeting is not None:
            text(meeting, width='90%', y="+1cm",
                 color=args['meeting_color'], size=args['subtitle_size'],
                 align='center')

        if date is not None:
            text(date, width=750, y="+1cm", color=args['date_color'],
                 size=args['date_size'])

THEME['maketitle']['template'] = theme_maketitle
