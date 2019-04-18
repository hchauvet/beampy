# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.modules.core import beampy_module, gcs
import base64
import os
try:
    # Old python 2
    from cStringIO import StringIO
except:
    # Python 3.x
    from io import BytesIO as StringIO

from PIL import Image
import sys
import subprocess


class video(beampy_module):
    """
    Include a figure to the current slide. Figure formats could be (**svg**,
    **pdf**, **png**, **jpeg**, **matplotib figure**, and **bokeh figure**)

    Parameters
    ----------

    content : str or matplotlib.figure or bokeh.figure
        Figure input source. To load file, `content` is the path to the file.
        For matplotlib and bokeh, `content` is the python object figure of
        either matplotlib or bokeh.

    ext : {'svg','jpeg','png','pdf','bokeh','matplotlib'} or None, optional
       Image format defined as string (the default value is None, which implies
       that the image format is guessed from file or python object name.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the figure (the default is 'center').

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the figure (the default is 'auto', which implies
        equal blank width between 'auto' positioned elements)

    width : int or float or None, optional
        Width of the figure (the default is None, which implies that the width
        is width of the image).

    """

    def __init__(self, videofile, **kwargs):
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

        self.type = 'html'

        # Check function args
        self.check_args_from_theme(kwargs)

        # if no width is given get the default width
        if self.width is None:
            self.width = document._slides[gcs()].curwidth

        # check extension
        self.ext = None
        if '.webm' in videofile.lower():
            self.ext = 'webm'
        elif '.ogg' in videofile.lower() or '.ogv' in videofile.lower():
            self.ext = 'ogg'
        elif '.mp4' in videofile.lower():
            self.ext = 'mp4'
        else:
            print('Video need to be in webm/ogg/mp4(h.264) format!')
            sys.exit(0)

        if self.ext is not None:
            self.content = videofile

        # Special args for cache id
        self.args_for_cache_id = ['width', 'still_image_time', 'embedded']
        # Add the time stamp of the video file
        fdate = str(os.path.getmtime( self.content ))
        self.args['filedate'] = fdate
        self.filedate = fdate
        self.args_for_cache_id += ['filedate']

        #Register the module
        self.register()

    def render( self ):
        """
        Render video (webm) encoded in base64 in svg command

        Render Need to produce an html and an svg
        """

        # Read file and convert data to base64 if embedded option is True (default)
        if self.embedded:
            with open(self.content, 'rb') as fin:
                videob64 = base64.b64encode( fin.read() ).decode('utf8')

        #Get video image
        size, imgframe = self.video_image()
        #Get video size to get the ratio (to estimage the height)
        _, _, vidw, vidh = size
        scale_x = (self.width/float(vidw)).value
        width = self.width

        if self.height.value is None:
            height = vidh * scale_x
            print('Video size might be buggy, estimated height %ipx'%height)
        else:
            height = self.height.value

        #HTML tag for video
        if self.embedded:
            videosrc = 'data:video/{ext};base64, {b64data}'.format(ext=self.ext, b64data=videob64)
        else:
            videosrc = self.content

        output = """<video id='video' width="{width}px" {otherargs}><source type="video/{ext}" src="{src}"></video>"""
            
        #Check if we need autoplay
        otherargs = ''
        if self.autoplay == True:
            otherargs += ' autoplay'

        if self.control == True:
            otherargs += ' controls="controls"'
        else:
            #Add click event to run video
            otherargs += ' onclick="this.paused?this.play():this.pause();"'

        output = output.format(width=width, otherargs=otherargs, ext=self.ext, src=videosrc)
        self.htmlout = output

        imgframe = base64.b64encode(imgframe).decode('utf8')
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/jpg;base64, %s" />'%(str(width), str(height), imgframe)
        self.svgout = output

        self.update_size(width, height)
        #Needed to be used by cache (we need to set the rendered flag to true)
        self.rendered = True

    def video_image(self):
        """
            Function used to get the first image of a video

            It use FFMPEG to extract one image
        """

        FFMPEG_CMD = document._external_cmd['video_encoder']
        FFMPEG_CMD += ' -loglevel 8 -i "%s" -f image2 -ss %0.3f -vframes 1 -; exit 0'%(self.content, self.still_image_time)

        #run_ffmpeg = subprocess.run(str(FFMPEG_CMD), stdout=subprocess.PIPE, shell=True)
        #img_out = run_ffmpeg.stdout
        run_ffmpeg = subprocess.check_output(str(FFMPEG_CMD), shell=True)
        img_out = run_ffmpeg
        #run_ffmeg = os.popen(FFMPEG_CMD)
        #img_out = run_ffmeg.read()

        img = StringIO(img_out)

        out = Image.open(img)

        # Get image size
        size = out.getbbox()

        #Save image to string
        outimg = StringIO()
        out.save(outimg, 'JPEG')
        out.close()

        strimg = outimg.getvalue()

        outimg.close()

        #Need to close img at then end
        img.close()

        return size, strimg
