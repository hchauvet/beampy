# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs, convert_unit
import base64


def video(videofile, width=None, height=None, x='center',y='auto',
          fps=25, autoplay=False):
    """
    Add video in webm format

    width and height must be specified !

    width = None -> document._width
    heigh = None -> document._height
    """

    #if no width is given get the default width
    if width == None:
        print("Warning: no video width given!")
        width = str(document._width)
    else:
        width=str(width)
        
    if height == None:
        print("Warning: no video height given!")
        height = str(document._height)
    else:
        width = str(width)

    #check extension
    ext = None
    if '.webm' in videofile.lower():
        ext = 'webm'
    elif '.ogg' in videofile.lower():
        ext = 'ogg'
    elif '.mp4' in videofile.lower():
        ext = 'mp4'
    else:
        print('Video need to be in webm/ogg/mp4(h.264) format!')

    if ext != None:
        args = {"x":str(x), "y": str(y) ,
                "width": str(width), "height": str(height),
                "fps": fps, "autoplay": autoplay,
                "ext": ext}

        with open(videofile, 'rb') as fin:
            datain = base64.b64encode( fin.read() )

        #Add video to the document
        videout = {'type': 'html', 'content': datain, 'args': args,
                   "render": render_video}

        document._contents[gcs()]['contents'] += [ videout ]


def render_video(videob64, args):
    """
    Render video (webm) encoded in base64 in svg command
    """


    #TODO: Try to get the video real size to keep aspect ratio

    output = """<video width="%spx" %s controls="controls" type="video/%s" src="data:video/%s;base64, %s"/>"""

    otherargs = ''
    width = convert_unit(args['width'])
    height = convert_unit(args['height'])

    if args['autoplay'] == True:
        otherargs += ' autoplay'

    output = output%(width, otherargs, args['ext'], args['ext'], videob64)

    return output, float(width), float(height)
