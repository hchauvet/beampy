# -*- coding: utf-8 -*-

"""
Part of beampy project

Manage cache system for slides
"""

import os
import cPickle as pkl
import gzip

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

            #Store old_x and y
            self.add_olddata(element)

            if slide not in self.data:
                self.data[slide] = {}


            #commands that include raw contents (like text, tikz, ...)
            if 'rendered' in element:
                elemid = element['id']
                self.data[slide][elemid] = {}
                self.data[slide][elemid]['element'] = element.copy()

                #print(element['args'])
                #print(element.keys())
                #For commands that includes files, need a filename elements in args
                #if 'filename' in element['args']:
                #    self.data[slide][elemid]['file_id'] = os.path.getmtime( element['args']['filename'] )

    def is_cached(self, slide, element):
        """
            Function to check if the given element is in the cache or not
        """
        
        if slide not in self.data:
            out = None

        else:

            if element['id'] not in self.data[slide]:
                out = None

            else:
                #Store old_x and y
                self.add_olddata(element)

                cacheelem = self.data[slide][element['id']]['element']

                if element['type'] not in ['group'] and element['content'] == cacheelem['content']:
                    #print("cool")
                    out = cacheelem

                    #print(cacheelem['args'])

                    #Compare args
                    if not self.compare_args(element['args'], cacheelem['args']):
                        #print(element['args'], cacheelem['args'])
                        out = None

                    #If it's from a file check if the file as changed
                    #if 'filename' in element['args']:
                    #    curtime = os.path.getmtime( element['args']['filename'] )
                    #    if curtime != self.data[slide][element['id']]['file_id']:
                    #        out = None


                    if out != None:
                        out = out
                        out['args']['x'] = out['args']['old_x']
                        out['args']['y'] = out['args']['old_y']
                        out['render'] = out['old_render']
                        #print out.keys()

                else:
                    out = None

        return out


    def compare_args(self, args1, args2):
        """Function to compare to args dict"""

        #Need to remove x and y to compare two args dict since x and y are sometime computed (center, auto, +Xcm)
        args1c = args1.copy()
        args2c = args2.copy()
        args1c.pop('x')
        args1c.pop('y')
        args2c.pop('x')
        args2c.pop('y')

        #For animatesvg we add and "ext" argument when we render
        if ('ext' not in args1c) and ('ext' in args2):
            args1c['ext'] = args2c['ext']

        #If height is None remove it from comparison (None is when size is computed from scale operation, for image, or animatesvg)
        if 'height' in args1c and args1c['height'] == None:
            args1c['height'] = args2c['height']
            
        return args1c == args2c

    def add_olddata(self,element):
        """
            Function to store old x and y (like center auto +xxcm)
            also old render
        """

        #Need to save old_x and old_y (used in cached to check if they had been changed by user)
        element['args']['old_x'] = element['args']['x']
        element['args']['old_y'] = element['args']['y']
        element['old_render'] = element['render']


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
