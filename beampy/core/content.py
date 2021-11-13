#!/usr/bin/env python3

"""
Beampy content module is used to define the content object. This object
store svg or html or js content, it's size, create an id for the content and
cached status.
"""
import sys
import hashlib
import logging
from beampy.core.store import Store
_log = logging.getLogger(__name__)

class Content():

    def __init__(self, content, content_type, width, height, name,
                 args_for_id = None):
        """Content, store a beampy content, create it's id and store it's size.

        Parameters
        ----------

        content, str:
            The svg, html, or javascript content

        content_type, str in ['svg', 'html', 'js', 'svggroup']:
            The type of the content

        Attributes:
        -----------

        """

        assert content_type in ['svg', 'html', 'js']
        self.type = content_type
        self.content = content
        self.name = name
        self.id = None
        self.args_for_id = args_for_id

        # Attribute of the original content
        self._dataid = None
        self._width = width
        self._height = height

        self.create_id()

    def create_id(self):
        """Create the id for this content
        """
        to_hash = f'{self.content} {self._width} {self._height} {self.type} {self.args_for_id}'
        tid = hashlib.md5(to_hash.encode('utf8')).hexdigest()[:10]

        self.id = tid

    def load_from_store(self):
        """Load the data content from the one in store
        """
        st_content = Store.get_content(self.id)
        self.data = st_content.data
        self.width = st_content.width
        self.height = st_content.height

    @property
    def data(self):
        if self._data_id is not None and Store.is_data(self._data_id):
            return Store.get_data(self._data_id)
        else:
            print('No data for this content in store ! %s' % self._data_id)

        return None

    @data.setter
    def data(self, new_data):
        to_hash = f'{new_data}'
        self._data_id = hashlib.md5(to_hash.encode('utf8')).hexdigest()[:10]

        if not Store.is_data(self._data_id):
            Store.add_data(new_data, self._data_id)

        if Store.is_content(self.id):
            Store.update_content_data_id(self.id, self._data_id)
        else:
            Store.add_content(self)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width
        Store.update_content_size(self)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height
        Store.update_content_size(self)

    def is_cached(self):
        pass

    def __repr__(self):
        out = f'Content {self.id}\n'
        out += f'width: {self.width}, height: {self.height}\n'
        out += f'data (id: {self._data_id}):\n {self.data}'

        return out
