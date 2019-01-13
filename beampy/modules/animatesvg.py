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
    """
    Create svg animation from a folder containing svg files (or any files that
    figure function can handle) or a list of matplotlib figures.

    Parameters
    ----------

    files_in : str or list of matplotlib figures or list of file names
        List of figures to animate. List could be generated using a string
        containing UNIX willcard like '/my/folder/*.svg', or using a list of
        file names or matplotlib figure object.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the animation (the default theme sets this to
        'center'). See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the animation (the default theme sets this to
        'auto'). See positioning system of Beampy.

    start : integer, optional
        Start position of the image sequence (the default theme sets this to
        0).

    end : int or 'end', optional
        End position of the image sequence (the default theme sets this to
        'end', which implies that the animation end at the last item of the
        files_in ).

    width : int or float or None, optional
        Width of the figure (the default is None, which implies that the width
        is width of the image).

    fps : int, optional
        Animation frame-rate (the default theme sets this to 25).

    autoplay : boolean, optional
        Automatically start the animation when the slide is shown on screen
        (the default theme sets this to False).

    """

    def __init__(self, files_in, **kwargs):


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
        if isinstance(files_in, str):
            svg_files = glob.glob(files_in)

            # Need to sort using the first digits finded in the name
            svg_files = sorted(svg_files, key=lambda x: int(''.join(re.findall(r'\d+', x))))

        # If the input is a list of names or mpl figures or other compatible with figure
        elif isinstance(files_in, list):
            svg_files = files_in

            if input_width is None:
                width_inch, height_inch = files_in[0].get_size_inches()
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

    def render(self):
        """
            Render several images as an animation in html
        """
        # Read all files and store their content
        svgcontent = []
        # Render each figure in a group
        output = []
        fig_args = {"width": self.width.value,
                    "height": self.height.value,
                    "x": 0, "y": 0}

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
