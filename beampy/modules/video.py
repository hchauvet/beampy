# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy.core.document import document
from pathlib import Path
from beampy.core.module import beampy_module
from beampy.core.functions import gcs
import base64
import os

# Python 3.x
from io import BytesIO as StringIO

from PIL import Image
import sys
import subprocess


class video(beampy_module):



    def __init__(self, videofile, x=None, y=None, width=None, height=None,
                 margin=None, autoplay=None, control=None, loop=None,
                 muted=None, still_image_time=None, embedded=None, **kwargs):

        #  Register the module
        super().__init__(x, y, width, height, margin, 'html', **kwargs)

        # Update the signature
        self.update_signature(videofile, x, y, width, height, margin, autoplay,
                              control, loop, muted, still_image_time, embedded,
                              **kwargs)

        # Add arguments as attributes
        self.set(videofile=Path(videofile), autoplay=autoplay, control=control,
                 loop=loop, muted=muted, embedded=embedded,
                 still_image_time=still_image_time)

        # Apply theme to None value
        self.apply_theme()

        # Do some control on input videofilei
        self.video_extension = self.videofile.suffix.replace('.', '')
        if self.video_extension not in ['webm', 'ogg', 'mp4']:
            raise Exception('Video need to be in webm/ogg/mp4(h.264) format!')

        # Get the datetime of the file
        self.mod_date = str(os.path.getmtime(str(self.videofile)))
        self.args_for_cache_id = [self.mod_date, self.still_image_time,
                                  self.embedded, self.autoplay, self.loop,
                                  self.control, self.muted]

        # Add the content and trigger render if needed
        self.add_content(videofile, 'html')

    def render(self):

        video_size, still_image = self.video_image()


        if self.height.value is None:
            if video_size is not None:
                _, _, vidw, vidh = video_size
                scale_x = self.width.value/float(vidw)
                self.height = vidh * scale_x
            else:
                self.height = self.width.value * 9/16.
                print('unable to get video size apply 16/9 ratio')
                
            print('Auto estimation of video height is buggy!')

        if self.embedded:
            videob64 = base64.b64encode(self.videofile.read_bytes()).decode('utf8')
            videosrc = f'data:video/{self.video_extension};base64, {videob64}'
        else:
            videosrc = str(self.videofile)

        videoargs = []

        if self.autoplay:
            videoargs += ['autoplay']

        if self.control:
            videoargs += ['controls="controls"']
        else:
            videoargs += ['onclicks="this.paused?this.play():this.pause();"']

        if self.loop:
            videoargs += ['loop']

        if self.muted:
            videoargs += ['muted']

        videoargs = ' '.join(videoargs)

        html_video = (f"<video id='video' width='{self.width.value}px' height='{self.height.value}px' "
                      f"{videoargs}>"
                      f"<source type='video/{self.video_extension}' src='{videosrc}'>"
                      "</video>")

        self.html = html_video
        
        self.html_svgalt = (f'<image x="0" y="0" width="{self.width.value}" '
                            f'height="{self.height.value}" '
                            f'xlink:href="data:image/png;base64, {base64.b64encode(still_image).decode("utf8")}" />')

        self.content_width = self.width.value
        self.content_height = self.height.value

    def video_image(self):
        """Get the first image of a video

        It use FFMPEG to extract one image
        """

        FFMPEG_CMD = document._external_cmd['video_encoder']
        FFMPEG_CMD += ' -loglevel 8 -i "%s" -f image2 -ss %s -vframes 1 -; exit 0' % (self.videofile,
                                                                                         self.still_image_time)

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
        out.save(outimg, 'PNG')
        out.close()

        strimg = outimg.getvalue()

        outimg.close()

        #Need to close img at then end
        img.close()

        return size, strimg
