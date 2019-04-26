# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:28:59 2015
@author: hugo
"""
from beampy.statics.default_theme import THEME
import sys
from distutils.spawn import find_executable
from beampy.cache import cache_slides
from beampy import __version__ as bpversion
# Auto change path
import os
import glob
import inspect
from time import time

bppath = os.path.dirname(__file__) + '/'
basename = os.path.basename(__file__)
script_file_name = os.path.basename(sys.argv[0]).split('.')[0]

import logging
_log = logging.getLogger(__name__)


class SourceManager(object):
    """
    SourceManager allows to read source file of the script and
    return it as a string.

    Python scripts could be run from different cases:

    1) Script run from a file: find the file name

    2) Interactive session in a classic Python shell
       -> redirect stdin

    3) Ipython: use the "In" variables stored in
       globals dict

    Example
    =======

    Source = SourceManager()

    # To get the source code
    str_source = Source.source()

    # To get line 3 to 10 of the source
    src_lines = Source.source(3,10)

    """

    def __init__(self, filename=None):
        """
        If filename is given, use this name to find the frame in the stack
        """
        
        # Loop over frames
        all_frames = inspect.stack()
        cframe = None
        for f in all_frames:

            # If a filename is given check if we find it in the stack
            if filename is not None:
                if filename in f[1]:
                    cframe = f[0]
                    break

            # Or check if we find module and if this module come from a .py file
            if  '<module>' in f[3]:
                _log.debug(f)
                # Test if the source of the module is a file
                if '.py' in f[1]:
                    cframe = f[0]
                    break
                
        if cframe is None:
            _log.info('No .py found in the stack... some modules will not work properly')
            for f in all_frames:
                _log.debug(f)
            
            cframe = all_frames[-1][0]
            
        #cframe = inspect.stack()[-1][0]
        # cur_frame = inspect.currentframe().f_code
        cur_frame = cframe.f_code
        
        guess_filename = cur_frame.co_filename
        self.python_code = None
        _log.debug(guess_filename)
        
        # Default
        self.source = self.return_nonesource
        self.join_char = ''

        if guess_filename == '':
            guess_filename = sys.argv[0]

        # Is the script launch from python ./my_file.py
        if '.py' in guess_filename:
            with open(guess_filename, 'r') as f:
                self.python_code = f.readlines()
            self.source = self.return_filesource
            
        # Ipython case
        if '<ipython-input-' in guess_filename or 'In' in globals():
            self.source = self.return_ipythonsource
            self.join_char = '\n'

        # Need to record the stdin
        if 'stdin' in guess_filename:
            print("todo")

    def return_filesource(self, start=0, stop=-1):
        return ''.join(self.python_code[start:stop])

    def return_ipythonsource(self, start=0, stop=-1):
        return '\n'.join(In[-1].split('\n')[start:stop])

    def return_nonesource(self):
        return ''

    def return_stdin(self):
        return self.stdin


class document():

    """
       Main function to define the document style etc...
    """

    __version__ = bpversion
    # Global variables to sotre data
    _contents = {}
    _slides = {}
    _curentslide = None
    _global_counter = {}
    _width = 0
    _height = 0
    _guide = False
    _text_box = False
    _optimize_svg = True
    _output_format = 'html5'
    _theme = THEME
    _cache = None
    _pdf_animations = False
    _resize_raster = True
    _source_code = []  # Store the source code of the input script
    _rendered = False  # Store the state of the entire document (allow multiformat output)

    # Store data that need to be globally loaded in html like raster
    # contents images, video, etc...  Format of an entry in the list:
    # {'type': 'svg (or html)', 'content': the data to be loaded}
    _global_store = {}

    # Define path to external commands (see default THEME file)
    _external_cmd = {}

    # Define quiet state for docuement
    _quiet = False

    # Store extra latex packages globally
    _latex_packages = []

    # The TOC format should be TOC = ['title':'Subsublevel title', level:1]
    _TOC = []

    # REMOVE globals=globals(), locals=locals() they are useless
    
    def __init__(self, quiet=False, latex_packages=None, source_filename=None, **kwargs):
        """
  
          Create document to store slides
            options (see THEME)
            -------
            - width[800]: with of slides
            - height[600]: height of slides
            - guide[False]: Draw guide lines on slides to test alignements
            - text_box[False]: Draw box on slide elements to test width and height detection of elements (usefull to debug placement)
            - optimize[True]: Optimize svg using scour python script. This reduce the size but increase compilation time
            - cache[True]: Use cache system to not compile slides each times if nothing changed!
            - resize_raster[True]: Resize raster images (inside svg and for jpeg/png figures)
            - theme: Define the path to your personal THEME dictionnary
        """

        if latex_packages is None:
            latex_packages = []

        if quiet:
            document._quiet = True
            sys.stdout = open(os.devnull, 'w')

        # reset if their is old variables
        self.reset()
        
        # A document is a dictionnary that contains all the slides
        self.data = self._contents
        
        # To store different counters
        self.global_counter = self._global_counter

        self.source_filename = source_filename
        
        # Check if we want to load a new theme
        if 'theme' in kwargs:
            theme = kwargs['theme']

            # Check if it's a python file which is given or a name of themes (stored in beampy/themes)
            themelist = []
            if '.py' in theme:
                themename = theme.split('.')[0]
            else:
                available_themes = glob.glob(bppath + 'themes/*_theme.py')

                if theme in '|'.join(available_themes):
                    #print((available_themes, theme))
                    themename = 'beampy.themes.'+theme+'_theme'
                    themelist = [theme+'_theme']

                    #print(themename)
                else:
                    themename = None
            try :
                new_theme = self.dict_deep_update( document._theme, __import__( themename, fromlist=themelist ).THEME )
                self.theme =  new_theme
                self.theme_name = themename
                document._theme = new_theme

            except ImportError:
                self.theme_name = 'default'
                print("No slide theme '" + theme + "', returning to default theme.")

        # Store extra latex packages globally
        document._latex_packages = latex_packages
        
        # Load document options from THEME
        self.set_options(kwargs)

        # Load external tools
        self.link_external_programs()

        # Load the source code of the current presentation
        self.get_source_code(source_filename)


        # Output the storage of slide etc... in debug logger
        _log.debug('Document class before adding slides')
        _log.debug('From classmethod (class not instantiated)')
        _log.debug(document.print_variables())
        
        # Print the header message
        print("="*20 + " BEAMPY START " + "="*20)

    def set_options(self, input_dict):
        # Get document option from THEME
        default_options = self._theme['document']
        if 'theme' in input_dict:
            default_options['theme'] = input_dict['theme']

        good_values = {}
        for key, value in input_dict.items():
            if key in default_options:
                good_values[key] = value
            else:
                print('%s is not a valid argument for document'%key)
                print('valid arguments')
                print(default_options)
                sys.exit(1)

        # Update default if not in input
        for key, value in default_options.items():
            if key not in good_values:
                good_values[key] = value

        # Set size etc...
        document._width = good_values['width']
        document._curwidth = float(document._width)
        document._height = good_values['height']
        document._curheight = float(document._height)
        
        document._guide = good_values['guide']
        document._text_box = good_values['text_box']
        document._cache = good_values['cache']
        document._optimize_svg = good_values['optimize']
        document._resize_raster = good_values['resize_raster']
        document._output_format = good_values['format']
        
        if not document._cache:
            document._cache = None
        else:
            if self.source_filename is not None:
                cache_file = './.beampy_cache_%s' % (self.source_filename)
            else:
                cache_file = './.beampy_cache_%s' % (script_file_name)
                
            print("\nChache file to %s" % (cache_file))
            document._cache = cache_slides(cache_file, self)

        self.options = good_values

    def reset(self):
        document._contents = {}
        document._slides = {}
        document._global_counter = {}
        document._width = 0
        document._height = 0
        document._guide = False
        document._text_box = False
        document._theme = THEME
        document._cache = None
        document._external_cmd = {}
        document._resize_raster = True
        document._output_format = 'html5'
        document._TOC = []

        document._global_store = {}
        document._external_cmd = {}
        document._latex_packages = []

        
    def dict_deep_update(self, original, update):

        """
        Recursively update a dict.
        Subdict's won't be overwritten but also updated.
        from http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression/44512#44512
        """

        for key, value in original.items():
            if not key in update:
                update[key] = value
            elif isinstance(value, dict) and isinstance(update[key], dict):
                self.dict_deep_update(value, update[key])
        return update

    def link_external_programs(self):
        # Function to link [if THEME['document']['external'] = 'auto'
        # and check external if programs exist

        #Loop over options
        missing = False
        for progname, cmd in self.options['external_app'].items():
            if cmd == 'auto':

                #Special case of video_encoder (ffmpeg or avconv)
                if progname == 'video_encoder':
                    find_ffmpeg = find_executable('ffmpeg')
                    find_avconv = find_executable('avconv')
                    if find_ffmpeg is not None:
                        document._external_cmd[progname] = find_ffmpeg
                    elif find_avconv is not None:
                        document._external_cmd[progname] = find_avconv
                    else:
                        missing = True
                else:
                    find_app = find_executable(progname)
                    if find_app is not None:
                        document._external_cmd[progname] = find_app
                    else:
                        missing = True

            else:
                document._external_cmd[progname] = cmd

            if missing:
                if progname == 'video':
                    name = 'ffmpeg or avconv'
                else:
                    name = progname

                print('Missing external tool: %s, please install it before running Beampy'%name)
                #sys.exit(1)

        outprint = '\n'.join(['%s:%s'%(k, v) for k, v in document._external_cmd.items()])
        print('Linked external programs\n%s'%outprint)

    def get_source_code(self, sourcefilename=None):
        document._source_code = SourceManager(sourcefilename)


    def __repr__(self):
        output = '''
        Document class infos:
        %s
        '''

        allvars = vars(self)
        private = ''
        other = ''
        
        for k in allvars:
            fmt = '%s: %s\n' % (k, str(allvars[k]))
            if k.startswith('_'):
                private += fmt
            else:
                other += fmt
                
        return output % (private+'\n\n'+other)

    
    @classmethod
    def print_variables(cls):
        """
        Print information on the document class and the content of its
        private data and methods.
        """
        
        # Calling cls.__repr__(cls) works for python 3.x but not for
        # python 2.7
        
        output = '''Document class infos:
        %s
        '''

        allvars = vars(cls)
        private = ''
        other = ''
        
        for k in allvars:
            fmt = '%s: %s\n' % (k, str(allvars[k]))
            if k.startswith('_'):
                private += fmt
            else:
                other += fmt
                
        return output % (private+'\n\n'+other)
    
def section(title):
    """
    Function to add a section in the TOC.

    Parameters
    ----------

    title : str,
        The title of the section.
    """

    islide = 0
    if 'slide' in document._global_counter:
        islide = document._global_counter['slide'] + 1
        
    document._TOC.append({'title': title, 'level': 0,
                          'slide': islide, 'id':hash(time())})


def subsection(title):
    """
    Function to add a subsection in the TOC.

    Parameters
    ----------

    title : str,
        The title of the subsection.
    """
    
    islide = 0
    if 'slide' in document._global_counter:
        islide = document._global_counter['slide'] + 1
        
    document._TOC.append({'title': title, 'level': 1,
                          'slide': islide, 'id':hash(time())})
    
def subsubsection(title):
    """
    Function to add a subsubsection in the TOC.

    Parameters
    ----------

    title : str,
        The title of the subsubsection.
    """

    islide = 0
    if 'slide' in document._global_counter:
        islide = document._global_counter['slide'] + 1
        
    document._TOC.append({'title': title, 'level': 2,
                          'slide': islide, 'id':hash(time())})

    
