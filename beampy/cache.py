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

    def add_to_cache(self, slide, bp_module):
        """
        Add the element of a given slide to the cache data

        slide: str of slide id, exemple: "slide_1"

        bp_module: neampy_module instance
        """

        if bp_module.type not in ['group']:

            #Add beampy version in data
            if 'version' not in self.data:
                self.data['version'] = self.version

            #Add the slide
            #if slide not in self.data:
            #    self.data[slide] = {}


            #commands that include raw contents (like text, tikz, ...)
            if bp_module.rendered:
                #Set the uniq id from the element['content'] value of the element
                elemid = create_element_id(bp_module, use_args=False, add_slide=False, slide_position=False)
                if elemid != None:
                    self.data[elemid] = {}
                    self.data[elemid]['content'] = bp_module.content
                    self.data[elemid]['width'] = bp_module.positionner.width
                    self.data[elemid]['height'] = bp_module.positionner.height
                    self.data[elemid]['svgout'] = bp_module.svgout
                    self.data[elemid]['htmlout'] = bp_module.htmlout
                    self.data[elemid]['jsout'] = bp_module.jsout

                    #print(element['args'])
                    #print(element.keys())
                    #For commands that includes files, need a filename elements in args
                    try:
                        self.data[elemid]['file_id'] = os.path.getmtime( bp_module.content )
                    except:
                        pass



    def is_cached(self, slide, bp_module):
        """
            Function to check if the given element is in the cache or not
        """
        out = False
        #old test on slide  slide in self.data and
        if bp_module.name not in ['group']:
            elemid = create_element_id(bp_module, use_args=False, add_slide=False, slide_position=False)

            if elemid != None and elemid in self.data:
                cacheelem = self.data[elemid]

                #Content check
                if bp_module.content == cacheelem['content']:
                    out = True

                #If it's from a file check if the file as changed
                if 'file_id' in cacheelem:
                    try:
                        curtime = os.path.getmtime( bp_module.content )
                    except:
                        curtime = None

                    if curtime != cacheelem['file_id']:
                        out = False
                    else:
                        out = True

                #If It's in cache load items from the cache to the object
                if out:
                    for key in ['svgout', 'jsout', 'htmlout']:
                        setattr(bp_module, key, cacheelem[key])

                    #Update the size
                    bp_module.update_size(cacheelem['width'], cacheelem['height'])

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
def create_element_id( bp_mod, use_args=True, use_render=True,
                       use_content=True, add_slide=True, slide_position=True,
                       use_size = True ):
    """
        create a unique id for the element using element['content'] and element['args'].keys() and element['render'].__name__
    """
    from beampy.functions import gcs
    from beampy.document import document

    ct_to_hash = ''

    if add_slide:
        ct_to_hash += gcs()

    if use_args and hasattr(bp_mod, 'args'):
        ct_to_hash += ''.join(['%s:%s'%(k,v) for k,v in bp_mod.args.items()])

    if use_render and bp_mod.name != None:
        ct_to_hash += bp_mod.name

    if use_content and bp_mod.content != None:
        ct_to_hash += str(bp_mod.content)

    if use_size:
        if 'height' in bp_mod.args:
            h = bp_mod.args['height']
        else:
            h = 'None'

        if 'width' in bp_mod.args:
            w = bp_mod.args['width']
        else:
            w = 'None'

        ct_to_hash += '(%s,%s)'%(str(w), str(h))

    if slide_position:
        ct_to_hash += str(len(document._slides[gcs()].element_keys))

    outid = None
    if ct_to_hash != '':
        #print ct_to_hash
        outid = hashlib.md5( ct_to_hash ).hexdigest()

        if outid in document._slides[gcs()].element_keys:
            print("Id for this element already exist!")
            sys.exit(0)
            outid = None
        #print outid

    return outid
