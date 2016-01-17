# -*- coding: utf-8 -*-

"""
Part of beampy project

Manage cache system for slides
"""

import os
import cPickle as pkl
import gzip
import copy
from beampy.document import document

class cache_slides():

    def __init__(self, cache_file):
        """
            Create a cache_slides object to store cache in the given cache file
        """
        self.file = cache_file

        self.data = {} #Cache data are stored in a dict

        #Try to read cache
        if os.path.exists(self.file):
            with gzip.open(self.file, 'rb') as f:
                self.data = pkl.load(f)

        if 'version' not in self.data:
            print('Cache file from an other beampy version!')
            self.data = {}

    def clear(self):

        if os.path.exists(self.file):
            os.remove(self.file)

        self.data = {}

    def add_to_cache(self, slide, element):
        """
        Add the element of a given slide to the cache data

        slide: str of slide id, exemple: "slide_1"

        element: dict containing element information and svg or html rendered
        """

        if element['type'] not in ['group']:

            #Add beampy version in data
            if 'version' not in self.data:
                self.data['version'] = document.__version__

            if slide not in self.data:
                self.data[slide] = {}


            #commands that include raw contents (like text, tikz, ...)
            if 'rendered' in element:
                elemid = element['positionner'].id
                self.data[slide][elemid] = {}
                self.data[slide][elemid]['content'] = element['content']
                self.data[slide][elemid]['width'] = element['positionner'].width
                self.data[slide][elemid]['height'] = element['positionner'].height
                self.data[slide][elemid]['rendered'] = element['rendered']

                #print(element['args'])
                #print(element.keys())
                #For commands that includes files, need a filename elements in args
                if 'filename' in element['args']:
                    self.data[slide][elemid]['file_id'] = os.path.getmtime( element['args']['filename'] )



    def is_cached(self, slide, element):
        """
            Function to check if the given element is in the cache or not
        """
        out = None

        if slide in self.data:

            if element['positionner'].id in self.data[slide]:

                cacheelem = self.data[slide][element['positionner'].id]

                if element['type'] not in ['group']:

                    #Content check
                    if element['content'] == cacheelem['content']:
                        out = cacheelem.copy()

                    #If it's from a file check if the file as changed
                    if 'filename' in element['args'] and 'file_id' in cacheelem:
                        curtime = os.path.getmtime( element['args']['filename'] )

                        if curtime != self.data[slide][element['positionner'].id]['file_id']:
                            out = None
                        else:
                            out = cacheelem.copy()

                else:
                    out = None

        return out

    def write_cache(self):
        """
            Export cache data to a pickle file
        """

        """
        for ct in self.data:
            print(ct)
            for elem in self.data[ct]:
                print(elem)
                print(self.data[ct][elem]['element'].keys())
        """

        with gzip.open(self.file, 'wb') as f:
            pkl.dump(self.data, f, protocol=2)
