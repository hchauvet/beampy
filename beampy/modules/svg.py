# -*- coding: utf-8 -*-
"""
@author: hugo

Module to write raw svg commands in slides
"""

from beampy.core.document import document
from beampy.core._svgfunctions import inkscape_get_size
from beampy.core.group import group
from beampy.core.module import beampy_module
from beampy.core.geometry import convert_unit
from beampy.core.content import Content

import logging
import tempfile


class svg(beampy_module):
    """
    Insert svg content.

    Parameters
    ----------

    svg_content : string
        Svg elements to add written in svg syntax without svg document tag
        "<svg xmlns...>"

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the svg (the default is 0). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the svg (the default is 0). See positioning
        system of Beampy.

    """

    
    def __init__(self, svg_content, x=None, y=None, width=None, height=None,
                 margin=None, inkscape_size=True, *args, **kwargs):

        # inti the module
        super().__init__(x, y, width, height, margin, 'svg')

        # Update the signature
        self.update_signature()

        # add arguments as attributes
        self.set(svg_content=svg_content, inkscape_size=inkscape_size)

        # apply theme to None
        self.theme_exclude_args = ['inkscape_size']
        self.apply_theme()

        # Register the module
        self.add_content(svg_content, 'svg')

    def render(self):
        """
            The render of an svg part
        """

        #Need to create a temp file
        if self.inkscape_size:
            logging.debug('Run inkscape to get svg size')
            # Need to get the height and width of the svg command
            tmpsvg = ('<svg xmlns="http://www.w3.org/2000/svg" version="1.2" '
                      'baseProfile="tiny" '
                      'xmlns:xlink="http://www.w3.org/1999/xlink">'
                      f'{self.svg_content} </svg>')

            # Use NamedTemporaryFile, that automatically remove the file on close by default
            with tempfile.NamedTemporaryFile(mode='w', prefix='beampytmp', suffix='.svg') as f:
                f.write(tmpsvg)

                # Need to flush the file to make it's content updated on disk
                f.file.flush()
                
                # Get the dimension of the svg using inkscape
                svg_width, svg_height = inkscape_get_size(f.name)
                # update beampy module width/height
                self.width = svg_width
                self.height = svg_height
        else:
            svg_width = self.width.value
            svg_height = self.height.value

        # Set the svg to beampy module
        self.svgdef = self.svg_content

        # Update the final width/height of the content
        self.content_width = svg_width
        self.content_height = svg_height


        #Set rendered flag to true (needed for the cache)
        self.rendered = True

