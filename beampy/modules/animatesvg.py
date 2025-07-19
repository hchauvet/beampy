# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy.core.document import document
from beampy.core.module import beampy_module
from beampy.modules.figure import figure
from beampy.core import Store
import glob
import re
import sys
from copy import copy

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

    def __init__(self, files_in, x=None, y=None, width=None, height=None,
                 margin=None, start=0, end='end', fps=None, autoplay=None,
                 *args, **kwargs):


        modtype = 'svg'
        # Register the module
        super().__init__(x, y, width, height, margin, modtype, **kwargs)

        # Add set some arguments as attributes
        self.set(files_in=files_in, start=start, end=end, fps=fps,
                 autoplay=autoplay)

        # Add type
        # self.type = 'animatesvg'

        # Update the signature
        self.update_signature(width=width, height=height)

        # Check input args for this module
        self.apply_theme()

        slide = Store.get_current_slide()

        # Add +1 to counter
        self.anim_num = slide.cpt_anim
        slide.cpt_anim += 1

        input_width = self.width # Save the input width for mpl figures
        if self.width is None:
            self.width = slide.curwidth

        # Read all files from a given wildcard
        if isinstance(files_in, str):
            self.files_in = glob.glob(files_in)

            # Need to sort using the first digits finded in the name
            self.files_in = sorted(self.files_in, key=lambda x: int(''.join(re.findall(r'\d+', x))))

        # If the input is a list of names or mpl figures or other compatible with figure
        elif isinstance(files_in, list):
            self.files_in = files_in

            if input_width is None:
                width_inch, height_inch = self.files_in[0].get_size_inches()
                self.width = "%fin"%(width_inch)
        else:
            print('Unknown input type for files_folder')
            sys.exit(0)

        # check how many images we wants
        if self.end == 'end':
            self.end = len(self.files_in)

        # Add content
        self.files_in = self.files_in[self.start:self.end]
        self.add_content(self.files_in, modtype)

    def render(self):
        """
            Render several images as an animation in html
        """
        # Read all files and store their content
        svgcontent = []
        # Render each figure in a group
        output = []
        output_svgdefs = []
        fig_args = {"width": self.width.value,
                    "height": self.height.value,
                    "x": 0, "y": 0,
                    "add_to_slide": False,
                    "add_to_group": False}

        _width = None
        _height = None
        if len(self.files_in)>0:
            #Test if output format support video
            if document._output_format=='html5':
                for iframe, svgfile in enumerate(self.files_in):
                    img = figure(svgfile, **fig_args)
                    img.call_cmd = str(iframe)+'->'+self.call_cmd.strip()
                    img.call_lines = self.call_lines
                    img.run_render()
                    img.compute_position()

                    # parse the svg
                    tmpout = '''<g id="frame_%i">%s</g>'''%(iframe, img.svguse)

                    output += [tmpout]
                    output_svgdefs += [img.svgdef]

                    if _width is None:
                        _width = img.width.value
                    if _height is None:
                       _height = img.height.value

                    img.delete()

                self.animout = output
                self.svgdef = '\n'.join(output_svgdefs)

                # Add the animou to content data to be able to get it from cache
                self.add_content_data('animout', self.animout)

            else:
                # Check if pdf_animations is True
                img = figure(self.files_in[0], **fig_args)
                img.x = copy(self.x)
                img.y = copy(self.y)

                img.render()
                self.update_size(img.width.value, img.height.value)
                self.svgdef = img.svgdef
                self.svgaltdef = img.svgaltdef
                img.delete()

            # return output
            if self.height.value is None:
                self.height = _height
            self.content_width = _width
            self.content_height = _height


        else:
            print('No image animation to render')

    def post_render(self):
        """
        We use the post-render function, to set back the
        animout data to the module when it's loaded from Store
        """

        if 'animout' in self.data:
            self.animout = self.data['animout']
