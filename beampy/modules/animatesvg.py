# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.modules.figure import figure
from beampy.modules.core import beampy_module
from beampy.functions import convert_unit, gcs

import glob
import re
import sys


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

        # Add type
        self.type = 'animatesvg'

        # Check input args for this module
        self.check_args_from_theme(kwargs)

        # Cache is useless because we call figure function which handle the cache for each figures
        self.cache = False

        slide = document._slides[gcs()]

        # Add +1 to counter
        self.anim_num = slide.cpt_anim
        slide.cpt_anim += 1

        input_width = self.width # Save the input width for mpl figures
        if self.width is None:
            self.width = slide.curwidth

        # Read all files from a given wildcard
        if isinstance(files_folder, str):
            svg_files = glob.glob(files_folder)

            # Need to sort using the first digits finded in the name
            svg_files = sorted(svg_files, key=lambda x: int(''.join(re.findall(r'\d+', x))))

        # If the input is a list of names or mpl figures or other compatible with figure
        elif isinstance(files_folder, list):
            svg_files = files_folder

            if input_width is None:
                width_inch, height_inch = files_folder[0].get_size_inches()
                self.width = convert_unit("%fin"%(width_inch))
                
        else:
            print('Unknown input type for files_folder')
            sys.exit(0)
                
        # check how many images we wants
        if self.end == 'end':
            self.end = len(svg_files)

        # Add content
        self.content = svg_files[self.start:self.end]

        # Register the module
        self.register()

    def render( self ):
        """
            Render several images as an animation in html
        """
        # Read all files and store their content
        svgcontent = []
        # Render each figure in a group
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

                    # parse the svg
                    tmpout = '''<g id="frame_%i">%s</g>'''%(iframe, img.svgout)

                    output += [tmpout]
                    img.delete()

                self.animout = output
            else:
                # Check if pdf_animations is True
                img = figure(self.content[0], **fig_args)
                img.positionner = self.positionner
                img.render()
                self.update_size(img.width, img.height)
                self.svgout = img.svgout
                img.delete()

            # return output
            # Update the rendered state of the module
            self.rendered = True
            
        else:
            print('nothing found')
