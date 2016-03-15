# -*- coding: utf-8 -*-

"""
Part of beampy project

Manage cache system for slides
"""

import os, sys
import cPickle as pkl
import gzip
import copy
import hashlib

class cache_slides():

    def __init__(self, cache_file, document):
        """
            Create a cache_slides object to store cache in the given cache file
        """
        self.file = cache_file
        self.version = document.__version__
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
                self.data['version'] = self.version

            if slide not in self.data:
                self.data[slide] = {}


            #commands that include raw contents (like text, tikz, ...)
            if 'rendered' in element:
                #Set the uniq id from the element['content'] value of the element
                elemid = create_element_id(element, use_args=False, add_slide=False, slide_position=False)
                if elemid != None:
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
            elemid = create_element_id(element, use_args=False, add_slide=False, slide_position=False)

            if elemid != None and elemid in self.data[slide]:
                cacheelem = self.data[slide][elemid]

                if element['type'] not in ['group']:

                    #Content check
                    if element['content'] == cacheelem['content']:
                        out = cacheelem.copy()

                    #If it's from a file check if the file as changed
                    if 'filename' in element['args'] and 'file_id' in cacheelem:
                        curtime = os.path.getmtime( element['args']['filename'] )

                        if curtime != self.data[slide][elemid]['file_id']:
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

#TODO: solve import bug when we try to import this function from beampy.functions...
def create_element_id( elem, use_args=True, use_render=True, use_content=True, add_slide=True, slide_position=True ):
    """
        create a unique id for the element using element['content'] and element['args'].keys() and element['render'].__name__
    """
    from beampy.functions import gcs
    from beampy.document import document
    
    ct_to_hash = ''

    if add_slide:
        ct_to_hash += gcs()

    if use_args and 'args' in elem:
        ct_to_hash += ''.join(['%s:%s'%(k,v) for k,v in elem['args'].items()])

    if use_render and 'render' in elem and elem['render'] != None:
        ct_to_hash += elem['render'].__name__

    if use_content and 'content' in elem:
        ct_to_hash += str(elem['content'])

    if slide_position:
        ct_to_hash += str(len(document._contents[gcs()]['element_keys']))

    outid = None
    if ct_to_hash != '':
        outid = hashlib.md5( ct_to_hash ).hexdigest()

        if outid in document._contents[gcs()]['element_keys']:
            print("Id for this element already exist!")
            sys.exit(0)
            outid = None
        #print outid

    return outid
