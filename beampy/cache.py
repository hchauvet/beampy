# -*- coding: utf-8 -*-

"""
Part of beampy project

Manage cache system for slides
"""

import os, sys

try:
    import cPickle as pkl
except:
    #compatibility with python 3.x
    import pickle as pkl

import gzip
import copy
import hashlib
import tempfile
import glob
import logging
_log = logging.getLogger(__name__)

class cache_slides():

    def __init__(self, cache_dir, document):
        """
            Create a cache_slides object to store cache in the given cache folder
        """
        self.folder = cache_dir
        self.version = document.__version__
        self.global_store = document._global_store
        self.data = {} #Cache data are stored in a dict

        self.data_file = 'data.pklz'
        
        #Try to read cache
        if os.path.isdir(self.folder):
            if os.path.exists(self.folder+'/'+self.data_file):
                with gzip.open(self.folder+'/'+self.data_file, 'rb') as f:
                    self.data = pkl.load(f)
                
        else:
            os.mkdir(self.folder)

        if 'version' not in self.data or self.data['version'] != self.version:
            print('Cache file from an other beampy version!')
            self.data = {}
            self.remove_files()
            
        #check if we the optimize svg option is enabled
        elif 'optimize' not in self.data or self.data['optimize'] != document._optimize_svg:
            print('Reset cache du to optimize')
            self.data = {}
            self.remove_files()
            
        else:
            #Restore glyphs definitions
            if 'glyphs' in self.data:
                document._global_store['glyphs'] = self.data['glyphs']
                
            
            
        #Add beampy version in data
        self.data['version'] = self.version
        self.data['optimize'] = document._optimize_svg
        
    def remove_files(self):
        for f in glob.glob(self.folder+'/*.pklz'):
            os.remove(f)
            
    def clear(self):

        if os.path.isdir(self.folder):
            os.removedirs(self.folder)

        self.data = {}

    def add_to_cache(self, slide, bp_module):
        """
        Add the element of a given slide to the cache data

        slide: str of slide id, exemple: "slide_1"

        bp_module: neampy_module instance
        """

        if bp_module.type not in ['group']:

            #commands that include raw contents (like text, tikz, ...)
            if bp_module.rendered:
                #Set the uniq id from the element['content'] value of the element
                elemid = create_element_id(bp_module, use_args=False, add_slide=False, slide_position=False)
                
                if elemid is not None:
                    
                    self.data[elemid] = {}
                    
                    #don't pickle matplotlib figure We don't need to store content in cache
                    #if "matplotlib" not in str(type(bp_module)):
                    #    self.data[elemid]['content'] = bp_module.content
                        
                    self.data[elemid]['width'] = bp_module.positionner.width.value
                    self.data[elemid]['height'] = bp_module.positionner.height.value
                    
                    if bp_module.svgout is not None:
                        #create a temp filename
                        svgoutname = tempfile.mktemp(prefix='svgout_', dir='')
                        self.data[elemid]['svgout'] = svgoutname
                        #save the file 
                        self.write_file_cache(svgoutname, bp_module.svgout)
                        
                    if bp_module.htmlout is not None:
                        htmloutname = tempfile.mktemp(prefix='htmlout_', dir='')
                        self.data[elemid]['htmlout'] = htmloutname
                        self.write_file_cache(htmloutname, bp_module.htmlout)
                        
                    if bp_module.jsout is not None:
                        jsoutname = tempfile.mktemp(prefix='jsout_', dir='')
                        self.data[elemid]['jsout'] = jsoutname
                        self.write_file_cache(jsoutname, bp_module.jsout)

                    #print(element['args'])
                    #print(element.keys())
                    #For commands that includes files, need a filename elements in args
                    try:
                        self.data[elemid]['file_id'] = os.path.getmtime( bp_module.content )
                    except:
                        pass

    def add_file(self, filename, content):
        """
        Function to add to the cache a file with it's content. It used to
        store required javascript libraries for instance.
        """

        file_id = hash(filename)
        self.data[file_id] = {'filename': filename}
        self.write_file_cache(filename, content)

    def get_cached_file(self, filename):
        """
        Try to get a given filename from cache 
        """

        file_id = hash(filename)
        if file_id in self.data:
            output_content = self.read_file_cache(filename)
        else:
            print('File %s is not cached' % filename)
            output_content = ''

        return output_content

    def is_file_cached(self, filename):
        """
        Check if a file with a given filename is in cache directory
        """
        out = False
        file_id = hash(filename)

        if file_id in self.data:
            out = True

        return out
    
    def is_cached(self, slide, bp_module):
        """
            Function to check if the given element is in the cache or not
        """
        out = False
        #old test on slide  slide in self.data and
        if bp_module.name not in ['group']:
            elemid = create_element_id(bp_module, use_args=False, add_slide=False, slide_position=False)

            #print(bp_module.name,":",elemid)
            if elemid is not None and elemid in self.data:
                cacheelem = self.data[elemid]
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
                        if key in cacheelem:
                            content = self.read_file_cache(cacheelem[key])
                            setattr(bp_module, key, content)

                    #Update the size
                    bp_module.update_size(cacheelem['width'], cacheelem['height'])

        return out

    def write_cache(self):
        """
            Export cache data to a pickle file
        """

        #Check if their is some glyphs in the global_store
        if 'glyphs' in self.global_store:
            self.data['glyphs'] = self.global_store['glyphs']
            
        with gzip.open(self.folder+'/'+self.data_file, 'wb') as f:
            pkl.dump(self.data, f, protocol=2)
            
            
    def write_file_cache(self, filename, content):
        
        with gzip.open(self.folder+'/'+filename+'.pklz', 'wb') as f:
            try:
                f.write(content.encode('utf-8'))
            except Exception as e:
                # Py 2 compatibility
                f.write(content)

    def read_file_cache(self, filename):
        output = None
        
        with gzip.open(self.folder+'/'+filename+'.pklz', 'rb') as f:
            try:
                output = f.read().decode('utf-8')
            except Exception as e:
                # Python 2 compatibility
                output = f.read()
            
        return output
        
#TODO: solve import bug when we try to import this function from beampy.functions...
def create_element_id(bp_mod, use_args=True, use_render=True,
                      use_content=True, add_slide=True, slide_position=True,
                      use_size = False):
    
    from beampy.document import document

    ct_to_hash = ''
    _log.debug('Create id for %s on slide %s' % (str(bp_mod.name), bp_mod.slide_id))
    
    if add_slide:
        ct_to_hash += bp_mod.slide_id

    if use_args and hasattr(bp_mod, 'args'):
        ct_to_hash += ''.join(['%s:%s'%(k,v) for k,v in bp_mod.args.items()])

    if use_render and bp_mod.name is not None:
        ct_to_hash += bp_mod.name

    if use_content and bp_mod.content is not None:
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
        ct_to_hash += str(len(document._slides[bp_mod.slide_id].element_keys))

    if bp_mod.args_for_cache_id is not None:
        for key in bp_mod.args_for_cache_id:
            try:
                tmp = getattr(bp_mod, key)
                ct_to_hash += str(tmp)
            except:
                print('No parameters %s for cache id for %s'%(key, bp_mod.name))

    outid = None
    if ct_to_hash != '':
        #print ct_to_hash
        try:
            outid = hashlib.md5( ct_to_hash.encode('utf-8') ).hexdigest()
        except:
            # for python 2
            outid = hashlib.md5( ct_to_hash ).hexdigest()

        if outid in document._slides[bp_mod.slide_id].element_keys:
            print("Id for this element already exist!")
            sys.exit(0)
            outid = None

    return outid
