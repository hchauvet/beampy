#!/usr/bin/env python3

"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy

Some interesting references:
Matplotlib handling of Tex
- https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/texmanager.py
- https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/dviread.py

Latex Font
- https://tug.org/FontCatalogue/

"""

from beampy.core.store import Store
from beampy.core.cache import create_global_folder_name
from beampy.core.functions import (gcs, color_text, 
                                   latex2svg, process_latex_header,
                                   find_strings_in_with)

from beampy.core._svgfunctions import (get_viewbox, get_baseline)

from beampy.core.module import beampy_module
import tempfile

from bs4 import SoupStrainer, BeautifulSoup
import sys

import logging
_log = logging.getLogger(__name__)

try:
    from xxhash import xxh3_64 as hashfunction
except Exception:
    _log.debug('Beampy is faster using xxhash librabry, pip install xxhash')
    from hashlib import md5 as hashfunction


# MAP font with latex font name and package and extra commands needed to use
# them.
LATEX_FONT = {
    'serif': {"name": "cmr",
              'package': None,
              'extra': None},
    'sans-serif': {"name": "cmss",
                   'package': None,
                   'extra': None},
    'monospace': {"name": "cmtt",
                  'package': "type1ec",
                  'extra': None},
    'helvetica': {"name": "phv",
                   'package': "helvet",
                   'extra': None},
    'avant garde': {"name": "pag",
                    'package': "avant",
                    'extra': None},
    'new century schoolbook': {'name': 'pnc',
                               'package': None,
                               'extra': r'\renewcommand{\rmdefault}{pnc}'},
    'times': {"name": "ptm",
              'package': 'mathptmx',
              'extra': None},
    'palatino': {"name": "ppl",
                 'package': 'mathpazo',
                 'extra': None},
    'zapf chancery': {"name": "pzc",
                     'package': 'chancery',
                      'extra': None},
    'charter': {"name": "pch",
                'package': 'charter',
                'extra': None},
    'courier': {"name": "pcr",
                'package': 'courier',
                'extra': None},
    'computer modern roman': {"name": "cmr",
                              'package': 'type1ec',
                              'extra': None},
    'computer modern sans serif': {"name": "cmss",
                                   'package': 'type1ec',
                                   'extra': None},
    'computer modern typewriter': {"name": "cmtt",
                                   'package': 'type1ec',
                                   'extra': None},
    'cursive': {'name': 'pzc', 'package': 'chancery',
                'extra': None}
}


class text(beampy_module):

    def __init__(self, textin=None, x=None, y=None, width=None, height=None,
                 margin=None, size=None, font=None, color=None, opacity=None, 
                 rotate=None, usetex=None, va=None, align=None, extra_packages=None,
                 cache_latex_preamble=True, *args, **kwargs):

        # Register the module
        super().__init__(x, y, width, height, margin, 'svg', **kwargs)

        # Set the arguments as attributes
        self.set(opacity=opacity, rotate=rotate, size=size, font=font, usetex=usetex, va=va,
                 extra_packages=extra_packages, textin=textin, color=color,
                 align=align, cache_latex_preamble=cache_latex_preamble)

        # Set the list of arguments to exclude for theme defaults lookup
        self.theme_exclude_args = ['textin']

        # Update the signature of the __init__ call
        self.update_signature()

        # Load default from theme
        self.apply_theme()

        # TODO: Parse the incomming text to add decoration or special commands

        # Some compatibility with beampy v < 1.0
        if self.font == 'CMR':
            self.font = 'sans-serif'

        # for Tex
        self._packages = []
        self.load_default_packages()
        self.font2tex()

        # Add agrs to check for id
        self.args_for_cache_id = [self.font, self.color, self.size, self.va,
                                  margin, self.align]

        if textin is not None:
            # Add the content this will run the render method if needed
            self.add_content(textin, 'svg')

    def render(self):
        """Transform the latex to svg and clean the output svg. Make svg id unique and
        grab svg size.
        """

        #  Transform latex -> svg
        if self.cache_latex_preamble:
            preamble_file = self.cache_preamble(self.preamble)
            svgtex = latex2svg(self.latex, cached_preamble=preamble_file)
        else:
            svgtex = latex2svg(self.latex)

        if svgtex == '':
            print('Beampy input:')
            print(self.latex)
            raise Exception('Latex Compilation Error, check the input')

        #  Clean the produced svg
        only_svg = SoupStrainer('svg')
        soup = BeautifulSoup(svgtex, 'lxml-xml', parse_only=only_svg)

        #  update path id and store them in the Store
        soup = self.make_unique_glyphs(soup)

        #  apply beampy theme to link
        soup = self.update_link_style(soup)

        #  get the viewbox
        xbox, ybox, text_width, text_height = get_viewbox(soup)

        #  we will remove the viewbox so we have to translate the use tags.
        #  by the starting point of the viewbox
        xoffset = -xbox
        yoffset = -ybox
        if self.va == 'baseline':
            #  get the baseline
            baseline = get_baseline(soup)
            yoffset = -float(baseline)

        tex_pt_to_px = 96 / 72.27 #  out svg is in px and not in pt
        self.scale = tex_pt_to_px
        self.translate = [xoffset, yoffset]

        #  Extract the use group
        use_group = soup.find('g', id='page1')

        # Text height and width are redefined by the latex renderer
        # need to update the one of the module
        self.width = text_width * tex_pt_to_px
        self.height = text_height * tex_pt_to_px

        # Add the final content to the module
        self.svgdef = use_group.renderContents().decode('utf8', errors='replace')
        self.content_width = text_width * tex_pt_to_px
        self.content_height = text_height * tex_pt_to_px

    def make_unique_glyphs(self, svgsoup: object) -> object:
        """Process the svg (parsed with BeautifulSoup) to ensure unique id for
        glyphs path.
        Glyphs are stored in the Store with a unique id based on their
        vectorized path hash.

        Parameter:
        ----------

        Return:
        -------

        The modified svgsoup object, with updated glyph ids in svg "use" and
        "defs".
        """

        # Find the defs tag of the svg
        defs_soup = svgsoup.find('defs')
        if defs_soup is not None:
            for path in defs_soup.find_all('path'):
                old_id = path['id']
                uid = hashfunction(path['d'].encode('utf8')).hexdigest()

                if Store.is_glyph(uid):
                    # Update the new_path_id from the Store
                    new_path_id = Store.get_glyph(uid)['id']
                else:
                    # Create a new id for this new glyph in Store
                    new_path_id = f'g_{len(Store._glyphs)}'
                    # Replace the id in the svg path tag
                    path['id'] = new_path_id
                    nglyph = {'id': new_path_id,
                              'dvisvgm_id': old_id,
                              'svg': str(path),
                              'uid': uid}

                    Store.add_glyph(nglyph)

                # in defs, they could be "use" tag that reuse a path and define
                # a new id to it with different arguments.
                for usedef in defs_soup.find_all('use', {'xlink:href': f'#{old_id}'}):
                    old_use_id = usedef['id']
                    use_uid = hashfunction(str(usedef).encode('utf8')).hexdigest()

                    if Store.is_glyph(use_uid):
                        # Get the new id from Store
                        new_use_id = Store.get_glyph(use_uid)['id']
                    else:
                        # Create the new use id
                        new_use_id = f'g_{len(Store._glyphs)}'
                        # Update reference for before storing the svg tag in Store
                        usedef['id'] = new_use_id
                        usedef['xlink:href'] = f'#{new_path_id}'
                        nuse = {'id': new_use_id,
                                'uid': use_uid,
                                'dvisvgm_id': old_use_id,
                                'svg': str(usedef)}

                        Store.add_glyph(nuse)

                    # Find all use (not in defs tag) that refer to this use tag
                    # id and update their link to the new id
                    for use in svgsoup.find_all('use', {'xlink:href': f'#{old_use_id}'}):
                        use['xlink:href'] = f'#{new_use_id}'

                # find all use that reference this path
                # and replace the reference by the new uniqueid
                for use in svgsoup.find_all('use', {'xlink:href': f'#{old_id}'}):
                    use['xlink:href'] = f'#{new_path_id}'

        return svgsoup

    def update_link_style(self, svgsoup: object) -> object:
        """Update the style attribute of "a" tag in the svg with the style
        defined in beampy theme.
        """

        links = svgsoup.find_all('a')
        if links is not None:
            for link in links:
                link_theme = Store.theme('link')
                new_style = ' '.join([f'{k}:{v};' for k, v in list(link_theme.items())])
                link['style'] = new_style

        return svgsoup

    @property
    def latex(self):
        """Return the latex formated of the module textin
        """

        # Cache the preamble if needed

        if hasattr(self, 'color'):
            textin = color_text(self.textin, self.color)
        else:
            textin = self.textin

        texalign = ''
        if 'center' in self.align:
            texalign = r'\centering'
        if 'right' in self.align:
            texalign = r'\flushright'

        if self.cache_latex_preamble:
            latex = []
        else:
            latex = [self.preamble]

        latex += [self._latex_font_extra,
                 r'\begin{document}',
                 r'\begin{varwidth}{%0.2fpt}' % (self.width.value*(72.27/96)),
                 texalign,
                 r'\fontsize{%i}{%i}' % (self.size,
                                        (self.size+self.size*0.1)),
                 r'\fontfamily{%s}\selectfont' % self._latex_font_name,
                 r'%s' % textin,
                 r'\end{varwidth}',
                 r'\end{document}'
                 ]

        return '\n'.join(latex)


    @property
    def preamble(self):
        """Get the latex preamble
        """

        pre = [r'\documentclass[crop=true]{standalone}',
               self.packages,
               ]

        pre = '\n'.join(pre)

        return pre

    def cache_preamble(self, preamble: str):
        """Manage latex caching of preamble
        """
        preamble_cache_file = ''

        #  hash the preamble
        prehash = hashfunction(preamble.encode('utf8')).hexdigest()

        #  Get the global cache path
        cache_path = create_global_folder_name()
        #  Create it if needed
        cache_path.mkdir(parents=True, exist_ok=True)

        preamble_cache_file = cache_path / f'header_{prehash}.fmt'

        if preamble_cache_file.is_file():
            _log.debug('Use latex header from cache')

        else:
            _log.debug('Render the latex header')
            process_latex_header(cache_path / f'header_{prehash}.tex',
                                 preamble)

        return preamble_cache_file

    @property
    def packages(self):
        latex_packages = []
        for p in self._packages:
            option = f"[{p['option']}]" if p['option'] is not None else ""
            latex_packages += [r'\usepackage%s{%s}' % (option, p['name'])]

        return '\n'.join(latex_packages)

    def add_package(self, newpackage):
        """Add a new package for this text, the new package could be given as:

        - a string: only the package name (without options)
        - a dictionnary: {"name": "package name", "option": "option1, option2"}
        - a list or tuple: ("package name", "option1, option2")
        """

        if isinstance(newpackage, str):
            self._packages += [{"name": newpackage, "option": None}]
        elif isinstance(newpackage, (list, tuple)):
            assert len(newpackage) == 2, "list or tuple should be of length 2 ('name', 'option1, option2')"
            self._packages += [{"name": newpackage[0], "option": newpackage[1]}]
        elif isinstance(newpackage, dict):
            assert 'name' in newpackage, "Dict should contain at least a 'name' key"
            if 'option' in newpackage:
                opt = newpackage['option']
            else:
                opt = None
            self._packages += [{'name': newpackages['name'], 'option': opt}]
        else:
            raise ValueError("Package format is unknown")

    def load_default_packages(self):
        """Load a list of default packages
        """
        pkg_list = [
            ('inputenc', 'utf8'),
            ('hyperref', 'hypertex'),
            ('xcolor', 'svgnames'),
            'varwidth',
            'textcomp',
            'type1cm'
        ]

        for p in pkg_list:
            self.add_package(p)

    def font2tex(self):
        """Convert given font name to a Tex compatible one and add the required packages
        """

        if self.font.lower() in LATEX_FONT:
            tmp_font = LATEX_FONT[self.font.lower()]

            if tmp_font['package'] is not None:
                self.add_package(tmp_font['package'])

            self._latex_font_extra = ''
            if tmp_font['extra'] is not None:
                self._latex_font_extra = tmp_font['extra']

            self._latex_font_name = tmp_font['name']

        else:
            raise KeyError("No such font available fonts:\n %s " % '\n'.join(LATEX_FONT.keys()))

    def process_with(self):
        """
        Parse the text enclosed contain in the with statement.
        with text():
            "bla bla bla bla"

            '''this is a cool thing
            do you think'''

            'yeahhhhhhh'
        """
        
        source = Store.get_layout()._source_code.source(start=self.start_line-1)
        input_texts = find_strings_in_with(source, 'text')
        self.textin = '\n'.join([t for t in input_texts])
        self.add_content(self.textin, self.type)