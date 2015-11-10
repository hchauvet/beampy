# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 20:33:18 2015

@author: hugo
"""
from beampy import document
from beampy.functions import gcs

def slide(title= None, doc = document, style=None):
    """
        Function to add a slide to the presentation
    """

    #Add a slide to the global counter
    if 'slide' in doc._global_counter:
        doc._global_counter['slide'] += 1
    else:
        doc._global_counter['slide'] = 0

    out = {'title':title, 'contents':[],
           'num':doc._global_counter['slide']+1,
           'groups': [],
           'style': style}

    document._contents[gcs()] = out

def begingroup(x='center',y='auto', width = None, height = None, background=None):
    """
       start a group
    """

    #check global counter
    if 'group' in document._global_counter:
        document._global_counter['group'] += 1
    else:
        document._global_counter['group'] = 0
        
    args = {'x': str(x), 'y': str(y), 'width': width, 'height': height, 'group_id': document._global_counter['group'], "background": background}
    tmp = {'args': args, 'content_start': len(document._contents[gcs()]['contents'])}

    document._contents[gcs()]['groups'] += [ tmp ]

def endgroup():
    """
        close the current group then computre the height and width of the group
    """

    if len(document._contents[gcs()]['groups']) > 0:
        group = document._contents[gcs()]['groups'][-1]
        group['content_stop'] = len(document._contents[gcs()]['contents'])
    else:
        print('Error no begingroup() defined before')


