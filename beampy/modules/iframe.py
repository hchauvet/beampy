# coding: utf-8

"""
Beampy module to include iframe in svg using svg ForeignObject
"""
from beampy.document import document
from beampy.functions import gcs
from beampy.modules.core import beampy_module

import logging
_log = logging.getLogger(__name__)

class iframe(beampy_module):
    """
    Include iframe in Beampy.

    """
    
    def __init__(self, iframe_content, **kwargs):

        self.type = 'svg'

        # Update arguments for the module
        self.load_args(kwargs)

        self.content = iframe_content

        # Check that a width/height is given or set the curent width/height
        if self.width is None:
            self.width = document._slides[gcs()].curwidth
            _log.info('Set the width to curwidth: %s' % self.width)
            
        if self.height is None:
            self.height = document._slides[gcs()].curheight
            _log.info('Set the height to curheight: %s' % self.height)
            
        # Register the module
        self.register()

    
    def render(self):
        """
        Render the iframe as an svg ForeignObject
        """

        svgout = '''<foreignObject x="0" y="0" width="{width}" height="{width}">
        <div xmlns="http://www.w3.org/1999/xhtml">
        <iframe src="{source}" style="width:{width}px;height:{height}px"></iframe>
        </div></foreignObject>'''


        svgout = svgout.format(width=self.positionner.width,
                               height=self.positionner.height, source=self.content)


        self.update_size(self.positionner.width, self.positionner.height)
        self.svgout = svgout

        self.rendered = True
