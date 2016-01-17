# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 20:33:18 2015

@author: hugo
"""
from beampy import document
from beampy.functions import gcs
from beampy.modules.title import title as bptitle
from beampy.geometry import positionner

def slide(title= None, doc = document, style=None):
    """
        Function to add a slide to the presentation
    """

    #Add a slide to the global counter
    if 'slide' in doc._global_counter:
        doc._global_counter['slide'] += 1
    else:
        doc._global_counter['slide'] = 0

    #Reset element counter for the slide
    #Add an id to the current element
    document._global_counter['element'] = 0

    out = {'title':title, 'contents':[],
           'num':doc._global_counter['slide']+1,
           'groups': [],
           'style': style}

    document._contents[gcs()] = out

    if title!= None:
        bptitle( title )



def begingroup(x='center', y='auto', width = None, height = None, background=None):
    """
       start a group
    """

    #check global counter
    if 'group' in document._global_counter:
        document._global_counter['group'] += 1
    else:
        document._global_counter['group'] = 0

    if width != None:
        width = width
    if height != None:
        height = height

    #args = {'x': str(x), 'y': str(y), 'width': width, 'height': height, 'group_id': document._global_counter['group'], "background": background}
    args = {'group_id': document._global_counter['group'],
            "background": background}

    tmp = {'args': args, 'id': args['group_id'],
           'content_start': len(document._contents[gcs()]['contents']),
           'positionner': positionner(x, y, width, height)}

    document._contents[gcs()]['groups'] += [ tmp ]

    return tmp['positionner']

def endgroup():
    """
        close the current group then computre the height and width of the group
    """

    if len(document._contents[gcs()]['groups']) > 0:
        group = document._contents[gcs()]['groups'][-1]
        group['content_stop'] = len(document._contents[gcs()]['contents'])

        #Add the group id to all the elements in this group
        for elem in document._contents[gcs()]['contents'][group['content_start']:group['content_stop']]:
            #if 'group_id' in elem:
            #    elem['group_id'] += [ group['id'] ]
            #else:
            elem['group_id'] = group['id']

    else:
        print('Error no begingroup() defined before')
