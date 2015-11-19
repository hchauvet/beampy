# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs, convert_unit
import base64
import os
import cStringIO 
from PIL import Image


def video(videofile, width=None, height=None, x='center',y='auto',
          autoplay=False, control=True):
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
    
    """

    #if no width is given get the default width
    if width == None:
        width = str(document._width)
    else:
        width=str(width)
        
    if height != None:
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
                "width": width, "height": height,
                "autoplay": autoplay, "control": control,
                "ext": ext, 'filename': videofile}

        with open(videofile, 'rb') as fin:
            datain = base64.b64encode( fin.read() )

        #Add video to the document type_nohtml used to remplace video by svg still image when not exported to HTML5
        videout = {'type': 'html', 'type_nohtml': 'svg', 'content': datain, 'args': args,
                   "render": render_video}
            
        document._contents[gcs()]['contents'] += [ videout ]


def render_video(videob64, args):
    """
    Render video (webm) encoded in base64 in svg command
    """


    #Get video size to get the ratio (to estimage the height)
    vidw, vidh = get_video_size(args)
    scale_x = float(convert_unit(args['width']))/float(vidw)
    width = convert_unit(args['width'])
    height = vidh * scale_x 

    if document._output_format=='html5':
        #HTML tag for video 
        output = """<video id='video' width="%spx" %s type="video/%s" src="data:video/%s;base64, %s"/>"""

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
        #Get video image 
        _, imgframe = video_first_image(args)
        imgframe = base64.b64encode( imgframe )
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/jpg;base64, %s" />'%(str(width), str(height), imgframe)
        
    return output, float(width), float(height)
    
    
    
def video_first_image(args):
    """
        Function used to get the first image of a video 
        
        It use FFMPEG to extract one image 
    """
    
    FFMPEG_CMD = document._external_cmd['ffmpeg'] 
    FFMPEG_CMD += ' -loglevel 8 -i %s -f image2 -vframes 1 -'%args['filename']
    

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
    
    size, frame = video_first_image(args)
    
    _, _, width, height = size
    
    return width, height
