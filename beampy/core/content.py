#!/usr/bin/env python3

"""
Beampy content module is used to define the content object. This object
store svg or html or js content, it's size, create an id for the content and
cached status.
"""
import sys
import hashlib
import logging
import json
import inspect
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
        self._data_id = None
        self._width = width
        self._height = height

        self.create_id()

    def create_id(self):
        """Create the id for this content
        
        It must be valid in XML documents. A stand-alone SVG document uses XML 1.0 syntax, which specifies that valid IDs only include 
        designated characters (letters, digits, and a few punctuation marks), and do not start with a digit, a full stop (.) character,
        or a hyphen-minus (-) character.
        """

        if self.args_for_id is not None:
            for arg in self.args_for_id:
                if inspect.isclass(arg):
                    print('WARNING: you add an object in args_for_id, this will result as a dirent id for each new objects')

        to_hash = f'{self.content} {self._width} {self._height} {self.type} {self.args_for_id}'
        tid = hashlib.md5(to_hash.encode('utf8')).hexdigest()[:10]
        # Add a 'B' to ensure XML validity

        self.id = 'B'+tid

        assert self.id is not None, f'The id should not be None: {to_hash}'

    def load_from_store(self):
        """Load the data content from the one in storel
        """
        st_content = Store.get_content(self.id)
        self.data = st_content.data
        self.width = st_content.width
        self.height = st_content.height

    @property
    def data(self):
        if Store.is_data(self._data_id):
            return Store.get_data(self._data_id)
        else:
            print('No data for this content in store ! %s' % self._data_id)
            print(self.name)

        return None

    @data.setter
    def data(self, new_data):
        to_hash = f'{new_data}'
        self._data_id = hashlib.md5(to_hash.encode('utf8')).hexdigest()[:10]
        # print(to_hash, self._data_id)

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
        assert width is not None, 'A content must have a fixed width'
        self._width = width
        Store.update_content_size(self, 'width')

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        assert height is not None, 'A content must have a fixed height'
        self._height = height
        Store.update_content_size(self, 'height')

    @property
    def is_cached(self):
        """Check if this content is cached on disk
        """

        if Store.cache() is not None:
            return Store.cache().is_cached(self.id)

        return False

    def load_from_cache(self):
        """Load a content from cache file
        """
        if Store.cache() is not None:
            cache_content = Store.cache().load_from_cache(self.id)
            # Update the content object
            self.content = cache_content["content"]
            self._data_id = cache_content["data_id"]

            # Add the content to the Store if needed
            if not Store.is_content(self.id):
                Store.add_content(self)

            # Update it's width and height
            self.width = cache_content["width"]
            self.height = cache_content["height"]

    def add_to_cache(self):
        """Add the current object to cache files
        """

        if Store.cache() is not None:
            Store.cache().add(self)

    @property
    def json(self):
        """Export content to json
        """
        out = {}
        out["id"] = self.id
        out["content"] = self.content
        out["width"] = self.width
        out["height"] = self.height
        out["data_id"] = self._data_id
        out["data"] = self.data

        return json.dumps(out)

    def __repr__(self):
        out = f'Content {self.id}\n'
        out += f'width: {self.width}, height: {self.height}\n'
        if self._data_id is not None:
            out += f'data (id: {self._data_id}):\n {self.data}'
        else:
            out += f'No data stored'

        return out

    def _repr_html_(self):
        """
        Define an SVG or HTML representation of this content
        to display it in jupyter notebook
        """

        pass
    
