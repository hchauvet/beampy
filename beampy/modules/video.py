# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs, convert_unit, add_to_slide, check_function_args
from beampy.geometry import positionner
import base64
import os
import cStringIO
from PIL import Image


def video(videofile, **kwargs):
    """
    Add video in webm/ogg/mp4 format

    arguments
    ---------

    width = None -> document._width
    heigh = None -> document._height

    x ['center']: x position
    y ['auto']: y position

    autoplay [False]: To launch video when slide appears

    control [True]: Display video control bar

    still_image_time [0]: extract the still image for pdf export at the given still_image_time in second
    """

    #Check function args
    args = check_function_args(video, kwargs)

    #if no width is given get the default width
    if args['width'] == None:
        args['width'] = str(document._width)

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
        args['ext'] = ext
        args['filename'] = videofile

        #Add video to the document type_nohtml used to remplace video by svg still image when not exported to HTML5
        videout = {'type': 'html', 'type_nohtml': 'svg', 'content': '', 'args': args,
                   "render": render_video,
                   'filename': videofile}

        return add_to_slide( videout, x=args['x'], y=args['y'], width=args['width'], height=None  )


def render_video( ct ):
    """
    Render video (webm) encoded in base64 in svg command
    """

    #Read file and convert data to base64
    with open(ct['filename'], 'rb') as fin:
        videob64 = base64.b64encode( fin.read() )

    args = ct['args']
    #Get video image
    size, imgframe = video_image(args)
    #Get video size to get the ratio (to estimage the height)
    _, _, vidw, vidh = size
    scale_x = ct['positionner'].width/float(vidw)
    width = ct['positionner'].width
    height = vidh * scale_x


    if document._output_format=='html5':
        #HTML tag for video
        output = """<video id='video' width="%spx" %s><source type="video/%s" src="data:video/%s;base64, %s"></video>"""

        #Check if we need autoplay
        otherargs = ''
        if args['autoplay'] == True:
            otherargs += ' autoplay'

        if args['control'] == True:
            otherargs += ' controls="controls"'
        else:
            #Add click event to run video
            otherargs += ' onclick="this.paused?this.play():this.pause();"'

        output = output%(width, otherargs, args['ext'], args['ext'], videob64)

    else:
        imgframe = base64.b64encode( imgframe )
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/jpg;base64, %s" />'%(str(width), str(height), imgframe)

    ct['positionner'].update_size(width, height)

    return output



def video_image(args):
    """
        Function used to get the first image of a video

        It use FFMPEG to extract one image
    """

    FFMPEG_CMD = document._external_cmd['video_encoder']
    FFMPEG_CMD += ' -loglevel 8 -i %s -f image2 -ss %0.3f -vframes 1 -'%(args['filename'], args['still_image_time'])


    img_out = os.popen(FFMPEG_CMD).read()

    img = cStringIO.StringIO(img_out)

    out = Image.open(img)


    #Get image size
    size = out.getbbox()

    #Save image to string
    outimg = cStringIO.StringIO()
    out.save(outimg, 'JPEG')
    out.close()

    strimg = outimg.getvalue()

    outimg.close()

    #Need to close img at then end
    img.close()

    return size, strimg


def get_video_size(args):
    """
        Get video size by extracting width and height of first frame
    """

    size, frame = video_image(args)

    _, _, width, height = size

    return width, height
