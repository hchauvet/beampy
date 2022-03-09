# -*- coding: utf-8 -*-

"""
Part of beampy project

Manage cache system for slides
"""
import os
import sys
from pathlib import Path
import json
import gzip
import logging

from beampy.core.store import Store

_log = logging.getLogger(__name__)


class Cache():
    """Manage cache for slide contents in Beampy
    """

    def __init__(self, cache_dir=None, register=True):
        """Create the cache folder and methods to interact with it.
        """

        # Use this dict to save global information on cache
        self.data = {}

        if cache_dir is None:
            cache_dir = create_folder_name()

        self.folder = cache_dir
        self.index_name = 'data.json.gz'
        self.index_fullpath = self.folder/self.index_name

        _log.debug(f'Cache dir: {self.folder}')

        if self.folder.exists():
            self.data = self.read()
            # Restore glyphs to store
            if 'glyphs' in self.data:
                Store.load_all_glyphs(self.data['glyphs'])
        else:
            self.folder.mkdir(parents=True)
            _log.debug('create cache dir')

        # Do we need to erase cache due to a change in beampy version
        if len(self.data) > 0 and self.data['version'] != Store._version:
            print('Reset cache because beampy version changed')
            self.data = {}
            self.remove_files()

        # Set the version in cache data
        self.data['version'] = Store._version

        if register:
            Store._cache = self

    def read(self):
        """Read the cache common information file on disk.
        """
        dataout = {}
        if self.index_fullpath.is_file():
            with gzip.open(self.index_fullpath, 'rb') as f:
                dataout = json.loads(f.read().decode('utf8'))
        else:
            _log.debug('Unable to load cache file %s' % str(self.index_fullpath))

        return dataout

    def save(self):
        """Save the data common dict on disk
        """

        # Add glyph to data
        self.export_glyphs()

        with gzip.open(self.index_fullpath, 'wb') as f:
            f.write(json.dumps(self.data).encode('utf-8'))

    def export_glyphs(self):
        """Export glyphs from Latex (dvisvgm) located in Store to the cache data
        """

        self.data['glyphs'] = Store.get_all_glyphs()

    def is_cached(self, file_id: str) -> bool:
        """Test if a given file_id is cached
        """

        if (self.folder/f'{file_id}.json.gz').is_file():
            return True

        return False

    def add(self, content: object):
        """Add a content (beampy.core.content.Content object) to a file.

        We split content oject into two parts:
        - The content
        - The data
        """

        # Need to transform content object to a dictionnary

        # The content
        ct = {}
        ct["id"] = content.id
        ct["type"] = content.type
        ct["name"] = content.name
        ct["content"] = content.content
        ct["width"] = content.width
        ct["height"] = content.height
        ct["data_id"] = content._data_id

        # The data
        data = content.data

        if not self.is_cached(content.id):
            self.write_file(content.id, ct)
        else:
            raise Exception("File already exist for %s" % str(content))

        if not self.is_cached(ct["data_id"]):
            self.write_file(ct["data_id"], data)

        fname = self.folder/f'{content.id}.zip'
        _log.debug(f"Write {fname} to cache")

    def load_from_cache(self, content_id: str) -> dict:
        """Load content and it's data from cached file with the given content_id.

        Return a dictionnary width Content informations (id, content, width,
        height, data_id)
        """

        content = self.read_file(content_id)

        # Check if we need to load data or if they are already in the Store.
        if not Store.is_data(content["data_id"]):
            tmp_data = self.read_file(content["data_id"])
            Store.add_data(tmp_data, content["data_id"])

        return content

    def write_file(self, filename, content):
        """Write a file to cache folder
        """

        with gzip.open(self.folder/f'{filename}.json.gz', 'wb') as f:
            f.write(json.dumps(content).encode('utf-8'))

    def read_file(self, filename):
        """Read a content pikles from file
        """
        output = None
        fname = self.folder/f'{filename}.json.gz'
        if fname.is_file():
            with gzip.open(fname, 'rb') as f:
                output = json.loads(f.read().decode('utf8'))
        else:
            raise Exception("Unable to load %s from cache" % filename)

        return output

    def remove_files(self):
        """Remove all files from cache folder
        """

        for f in self.folder.glob('*.json.gz'):
            os.remove(f)


def create_folder_name():
    """Create a folder name for the cache. Depends on how beampy is run. Mostly
    by calling: "python3 my_presentation.py", we use sys.argv[0] to get my_presentation.py
    """

    guess_scriptfilename = Path(sys.argv[0])
    if ('ipykernel' in guess_scriptfilename.name or 'ipython' in guess_scriptfilename.name):
        cache_folder = Path('./').absolute().joinpath('beampy_cache_ipython')
        print(f"Your in a ipython/notebook session I will put the cache in {cache_folder}")
    else:
        scriptname = guess_scriptfilename.name.replace(guess_scriptfilename.suffix, '')
        cache_folder = Path('./').absolute().joinpath(f'.beampy_cache_{scriptname}')

    return cache_folder


def create_global_folder_name():
    """Create a folder for global beampy cache in the home directory of users
    home/.cache folder.

    This global folder is used to store general function of beampy, like result
    of finding external programs, or the latex preamble file
    """

    cache_folder = Path('./').home().joinpath('.cache','beampy_cache')

    return cache_folder
