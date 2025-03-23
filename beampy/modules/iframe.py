# coding: utf-8

"""
Beampy module to include iframe in svg using svg ForeignObject
"""
from beampy.core.store import Store
from beampy.core.module import beampy_module

import logging
_log = logging.getLogger(__name__)

class iframe(beampy_module):
    """
    Include iframe in Beampy.

    """

    def __init__(self, iframe_content, x=None, y=None, width=None, height=None, margin=None,
                 opacity=None, *args, **kwargs):

        # Register the module
        super().__init__(x, y, width, height, margin, 'svg', **kwargs)

        # Set the other arguments as atributes
        self.set(content=iframe_content, opacity=opacity)

        # Set the list of arguments to exclude for theme defaults lookup
        self.text_exclude_args = ['content']

        # Update the signature of the __init__ call
        self.update_signature()

        # Load default from theme
        self.apply_theme()

        if self.width.value is None:
            self.width = Store.current_width()
        if self.height.value is None:
            self.height = Store.current_height()

        # Register the module
        # Make a kind of svg content to create a unique ID
        svgc = f'<iframe src="{self.content}"></iframe>'
        self.add_content(svgc, 'svg')


    def render(self):
        """
        Render the iframe as an svg ForeignObject
        """

        svgout = '''<foreignObject x="0" y="0" width="{width}" height="{width}">
        <div xmlns="http://www.w3.org/1999/xhtml">
        <iframe src="{source}" style="width:{width}px;height:{height}px"></iframe>
        </div></foreignObject>'''


        svgout = svgout.format(width=self.width.value,
                               height=self.height.value,
                               source=self.content)


        self.svgdef = svgout
        self.content_width = self.width.value
        self.content_height = self.width.value
