# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs, add_to_slide, check_function_args
from beampy.modules.figure import render_figure
from beampy.geometry import positionner
import re
import glob

def animatesvg(files_folder, **kwargs):
    """
        Function to create svg animation from a folder containing svg files

        - files_folder: Folder containing svg like "./my_folder/"

        - x['center']: x coordinate of the image
                       'center': center image relative to document._width
                       '+1cm": place image relative to previous element

        - y['auto']: y coordinate of the image
                     'auto': distribute all slide element on document._height
                     'center': center image relative to document._height (ignore other slide elements)
                     '+3cm': place image relative to previous element

        - start[0]: svg image number to start the sequence
        - end['end']: svg image number to stop the sequence
        - width[None]: Width of the figure (None = slide width)
        - fps[25]: animation framerate
        - autoplay[False]: autoplay animation when slide is displayed

    """

    #Check input args for this module
    args = check_function_args(animatesvg, kwargs)

    if args['width'] == None:
        args['width'] = str(document._width)

    #Read all svg files
    svg_files = glob.glob(files_folder+'*.svg')

    #Need to sort using the first digits finded in the name
    svg_files = sorted(svg_files, key=lambda x: int(''.join(re.findall(r'\d+', x))))

    #check how many images we wants
    if args['end'] == 'end':
        args['end'] = len(svg_files)

    svg_files = svg_files[args['start']:args['end']]

    svgcontent = []
    for svgf in svg_files:
        with open(svgf,'r') as f:
            svgcontent += [f.read()]

    animout = {'type': 'animatesvg', 'content': svgcontent, 'args': args,
               "render": render_animatesvg,
               'positionner': positionner(args['x'], args['y'], args['width'], None)}

    return add_to_slide( animout )


def render_animatesvg( ct ):

    anime = ct['content']
    args = ct['args']

    #Render each figure in a group
    args['ext'] = 'svg'
    output = []

    if len(anime)>0:
        #Test if output format support video
        if document._output_format=='html5':
            for iframe, svg in enumerate(anime):
                tmpout = render_figure( {'content':svg, 'args':args,
                                                'positionner':ct['positionner']} )
                #parse the svg
                tmpout = '<g id="frame_%i">'%iframe + tmpout + '</g>'

                output += [tmpout]
        else:
            #Check if pdf_animations is True
            output = render_figure({'content':anime[0], 'args':args,
                                               'positionner':ct['positionner']})
            if document._pdf_animations:
                #Convert svg to pdf if we want to use them in animategraphics in latex

                #Remove the output from the svg slide (it will be rendered later in latex)
                output = ''


        return output

    else:
        print('nothing found')
