# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.modules.figure import figure
from beampy.modules.core import beampy_module
import glob
import re

class animatesvg(beampy_module):

    def __init__(self, files_folder, **kwargs):
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

        #Add type
        self.type = 'animatesvg'

        #Check input args for this module
        self.check_args_from_theme(kwargs)

        if self.width == None:
            self.width = document._width

        #Read all svg files
        svg_files = glob.glob(files_folder+'*.svg')

        #Need to sort using the first digits finded in the name
        svg_files = sorted(svg_files, key=lambda x: int(''.join(re.findall(r'\d+', x))))

        #check how many images we wants
        if self.end == 'end':
            self.end = len(svg_files)

        #Add content
        self.content = svg_files[self.start:self.end]

        #Register the module
        self.register()



    def render( self ):
        """
            Render several images as an animation in html
        """
        #Read all files and store their content
        svgcontent = []
        #Render each figure in a group
        output = []
        fig_args = {"width": self.width, "height": self.height, "x": 0, "y": 0}

        if len(self.content)>0:
            #Test if output format support video
            if document._output_format=='html5':
                for iframe, svgfile in enumerate(self.content):
                    #print iframe
                    img = figure(svgfile, **fig_args)
                    img.positionner = self.positionner
                    img.call_cmd = str(iframe)+'->'+self.call_cmd.strip()
                    img.call_lines = self.call_lines
                    img.run_render()

                    if iframe == 0:
                        self.update_size(img.width, img.height)


                    #parse the svg
                    tmpout = '''<g id="frame_%i">%s</g>'''%(iframe, img.svgout)

                    output += [tmpout]
                    img.delete()




                self.animout = output

            else:
                #Check if pdf_animations is True
                img = figure(self.content[0], **fig_args)
                img.positionner = self.positionner
                img.render()
                self.update_size(img.width, img.height)
                self.svgout = img.svgout
                img.delete()


            #return output

        else:
            print('nothing found')
