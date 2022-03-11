# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:28:59 2015
@author: hugo
"""

import sys
from distutils.spawn import find_executable
from beampy.core.theme import Theme
from beampy.core.cache import Cache
from beampy.core.store import Store

# Auto change path
import os
import glob
import inspect
from time import time
from pathlib import Path

bppath = Path(os.path.dirname(__file__))
bppath = str(bppath.parent)  + '/'
basename = os.path.basename(__file__)
script_file_name = os.path.basename(sys.argv[0]).split('.')[0]

try:
    from IPython import get_ipython
    from IPython.display import display
    _IPY_ = get_ipython()
    if _IPY_ is None:
        _IPY_ == False
except:
    _IPY_ = False

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
        
        self._IPY_ = _IPY_

        # Loop over frames
        if not _IPY_:
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
                if Path(guess_filename).is_file():
                    with open(guess_filename, 'r') as f:
                        self.python_code = f.readlines()
                    self.source = self.return_filesource
                else:
                    _log.info('Unable to open file %s as source file' % guess_filename)
                    self.source = self.return_nonesource
        else:
            # Ipython case
            self.source = self.return_ipythonsource
            self._IPYsource = ''
            self.join_char = '\n'

            # Register the events to ipython
            load_ipython_extension(_IPY_)


        
    def return_filesource(self, start=0, stop=-1):
        return ''.join(self.python_code[start:stop])

    def return_ipythonsource(self, start=0, stop=-1):
        """
        Return the last '_iXX' of the globals() dict
        """
        
        return '\n'.join(self._IPYsource.split('\n')[start:stop])

    def return_nonesource(self):
        return ''

    def return_stdin(self):
        return self.stdin


class document():
    """
       Define the layout of slides and global options for beampy
    """

    
    def __init__(self, width=None, height=None, optimize=None, cache=True, resize_raster=True, theme=None, 
                 quiet=False, latex_packages=None, source_filename=None, auto_register=True, **kwargs):
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
            - theme: Define the path to your personal THEME dictionnaryXS
        """

        if latex_packages is None:
            latex_packages = []

        if quiet:
            self._quiet = True
            sys.stdout = open(os.devnull, 'w')
        else:
            self._quiet = False

        
        self.source_filename = source_filename
        
        
        # Load the Theme
        self._theme = Theme(theme)

        # Store extra latex packages globally
        self._latex_packages = latex_packages
        
        # Load document options from THEME
        self.set_options(kwargs)

        # Load external tools
        self.link_external_programs()

        # Add this document to the layout in the store
        if auto_register:
            Store.add_layout(self)

        # Load the source code of the current presentation
        self._source_code = SourceManager(source_filename)

    def set_options(self, input_dict):
        # Get document option from THEME
        default_options = Store.theme('document')

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

        self.options = good_values

    def link_external_programs(self):
        # Function to link [if THEME['document']['external'] = 'auto'
        # and check external if programs exist

        #Loop over options
        missing = False
        self._external_cmd = dict()
        for progname, cmd in self.options['external_app'].items():
            if cmd == 'auto':

                #Special case of video_encoder (ffmpeg or avconv)
                if progname == 'video_encoder':
                    find_ffmpeg = find_executable('ffmpeg')
                    find_avconv = find_executable('avconv')
                    if find_ffmpeg is not None:
                        self._external_cmd[progname] = find_ffmpeg
                    elif find_avconv is not None:
                        self._external_cmd[progname] = find_avconv
                    else:
                        missing = True
                else:
                    find_app = find_executable(progname)
                    if find_app is not None:
                        self._external_cmd[progname] = find_app
                    else:
                        missing = True

            else:
                self._external_cmd[progname] = cmd

            if missing:
                if progname == 'video':
                    name = 'ffmpeg or avconv'
                else:
                    name = progname

                print('Missing external tool: %s, please install it before running Beampy'%name)
                #sys.exit(1)

        outprint = '\n'.join(['%s:%s'%(k, v) for k, v in self._external_cmd.items()])
        print('Linked external programs\n%s'%outprint)

    def IPYupdate_source(self, info):
        """
        Trigger event from Ipython to update the source of the current cell
        """
        
        # Add an empty new line at the end
        self._source_code._IPYsource = info.raw_cell + '\n'

    def __repr__(self):
        output = 'Document class infos:\n %s'

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

    

def load_ipython_extension(ip):
    """
    Add and event callback to ipython 
    https://ipython.readthedocs.io/en/stable/config/callbacks.html
    """

    ip.events.register('pre_run_cell', Store.get_layout().IPYupdate_source)