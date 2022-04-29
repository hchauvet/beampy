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
except Exception as e:
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
        self._theme_exclude_args = ['textin']

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
                                  self.margin, self.align]

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

        tex_pt_to_px = 96/72.27 #  out svg is in px and not in pt
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
                link_theme = Store.get_theme('link')
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

class textOld(beampy_module):
    r"""
    Add text to the current slide. Input text is by default processed using
    Latex and could use Latex syntax.

    Parameters
    ----------

    textin : str, optional
        Text to add. Could contain latex syntax with protected slash either by
        using double slash or by using the python **r** before string.

        >>> text(r'\sqrt{x}')

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the text container (the default is 'center').
        See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the text container (the default is 'auto'). See
        positioning system of Beampy.

    width : int or float or None, optional
       Width of the text container (the default is None, which implies that the
       width is the parent group with).

    size : int, optional
        The font size (the default theme sets this value to 20).

    font : str, optional
        The Tex font (the default theme sets this value to
        'CMR'). **THIS IS NOT YET IMPLEMENTED!**

    color : str, optional
        The text color (the default theme set this value to '#000000'). Color
        could be html hex values or SVG-COLOR-NAMES.

    usetex : bool, optional
        Use latex to render text (the default value is true). Latex render
        could be turned off using `usetex`=False, then the text is rendered as
        svg.

    va : {'','baseline'}, optional
       Vertical text alignment (the default value is '', which implies that the
       alignment reference is the top-left corner of text). When
       `va`='baseline', the base-line of the first text row is computed and
       used as alignment reference (baseline-left).

    extra_packages : list of string, optional
        Add latex packages to render the text, like
        [r'\usepackage{name1}', r'\usepackage{name2}']


    Example
    -------

    >>> text('this is my text', x='20', y='20')

    """

    def __init__(self, textin=None, **kwargs):

        self.type = 'text'
        self.check_args_from_theme(kwargs)
        self.content = textin

        self.svgtext = ''  # To store the svg produced by latex

        # Height of text is None (it need to be computed)
        self.height = None
        # Check width
        if self.width is None:
            self.width = document._slides[gcs()].curwidth

        # Add special args for cache id
        # Text need to be re-rendered from latex if with, color or size are changed
        self.initial_width = self.width
        self.args_for_cache_id = ['initial_width', 'color', 'size', 'align', 'opacity']

        # Initialise the global store on document._content to store letter
        if 'svg_glyphs' not in document._contents:
            document._contents['svg_glyphs'] = {}

        if self.extra_packages != []:
            auto_render = True
        else:
            auto_render = False

        # Register the function to the current slide
        self.register(auto_render=auto_render)

    def process_with(self):
        """
        Process the text inside the with
        """
        source = document._source_code.source(start=self.start_line-1,
                                              stop=-1)
        input_texts = find_strings_in_with(source, 'text')
        self.content = r'\\'.join([r"%s" % t for t in input_texts])
        _log.debug('With text found: from line %i->end' % (self.start_line))
        _log.debug(source)
        _log.debug(self.content)

    def pre_render(self):
        """
        Prepare the latex render of the text
        """

        if self.usetex:
            #Check if a color is defined in args
            if hasattr(self, 'color'):
                textin = color_text( self.content, self.color )
            else:
                textin = self.content

            if 'center' in self.align:
                texalign = r'\centering'
            elif 'right' in self.align:
                texalign = r'\flushright'
            else:
                texalign = ''

            template = r"""\begin{varwidth}{%ipt}
            %s
            \fontsize{%i}{%i}\selectfont %s

            \end{varwidth}"""

            # Matplotlib uses fontsize * 1.25 for spacing
            self.latex_text = template % (self.width.value - (self._margin.left+self._margin.right)*(72.27/96.),
                                          texalign, self.size,
                                          (self.size+self.size*0.1),
                                          textin)
            # fontsize{size}{interlinear_size}
            #96/72.27 pt_to_px for latex

        else:
            self.latex_text = ''

    def local_render(self):
        """Function to render only on text of this module.

        It's slower than writing all texts to one latex file and then
        render it to dvi then svg.
        """

        if self.latex_text != '':
            pretex = r"""
            \documentclass[crop=true]{standalone}
            \usepackage[utf8x]{inputenc}
            \usepackage{fix-cm}
            \usepackage[hypertex]{hyperref}
            \usepackage[svgnames]{xcolor}
            \renewcommand{\familydefault}{\sfdefault}
            \usepackage{varwidth}
            \usepackage{amsmath}
            \usepackage{amsfonts}
            \usepackage{amssymb}
            """

            pretex += '\n'.join(self.extra_packages + document._latex_packages)
            pretex += r'\begin{document}'
            pretex += self.latex_text
            pretex += r'\end{document}'

            #latex2svg
            self.svgtext = latex2svg( pretex )

        else:
            self.svgtext = ''

    #Define the render
    def render(self):
        """
            Text is rendered using latex if self.usetex = True if not use simple svg
        """

        if self.usetex:
            #print(self.svgtext)
            if self.svgtext == '':
                # Run the local render
                self.local_render()

                # If it's still empty their is an error
                if self.svgtext == '':
                    print("Latex Compilation Error")
                    print("Beampy Input:")
                    print(self.content)
                    sys.exit(0)

            #Parse the ouput with beautifullsoup
            soup = BeautifulSoup(self.svgtext, 'xml')
            svgsoup = soup.find('svg')
            #print(soup)

            #Find the width and height
            xinit, yinit, text_width, text_height = svgsoup.get('viewBox').split()
            text_width = float(text_width)
            text_height = float(text_height)


            #Get id of paths element to make a global counter over the entire document
            if 'path' not in document._global_counter:
                document._global_counter['path'] = 0

            #New method with a global glyph store
            svgsoup = self.parse_dvisvgm_svg( svgsoup )

            #Change id in svg defs to use the global id system
            #soup = make_global_svg_defs(soup)

            #svgsoup = soup.find('svg')

            #Find all links to apply the style defined in theme['link']
            links = svgsoup.find_all('a')
            style = ' '.join(['%s:%s;'%(str(key), str(value)) for key, value in list(document._theme['link'].items())])
            for link in links:
                link['style'] = style

            #Use the first <use> in svg to get the y of the first letter
            try:
                uses = svgsoup.find_all('use')
            except:
                print(soup)

            if len(uses) > 0:
                #TODO: need to make a more fine definition of baseline
                baseline = 0
                for use in uses:
                    if use.has_attr('y'):
                        baseline = float(use.get('y'))
                        break

                if baseline == 0:
                    print("No Baseline found in TeX and is put to 0")
                    #print baseline

                #Get the group tag to get the transform matrix to add yoffset
                g = svgsoup.find('g')
                transform_matrix = g.get('transform')


                if getattr(self, 'va', False) and self.va == 'baseline':
                    yoffset = - float(baseline)
                    xoffset = - float(xinit)
                    #for the box plot (see boxed below)
                    oldyinit = yinit
                    yinit = - float(baseline) + float(yinit)
                    baseline = -float(oldyinit) + float(baseline)

                else:
                    yoffset = -float(yinit)
                    xoffset = -float(xinit)
                    #For the box plot
                    baseline = -float(yinit) + float(baseline)
                    yinit = 0



                #print baseline, float(yinit), yoffset
                #newmatrix = 'translate(%s,%0.4f)'%(-float(xoffset),-float(yoffset) )
                tex_pt_to_px = 96/72.27
                newmatrix = 'scale(%0.3f) translate(%0.1f,%0.1f)'%(tex_pt_to_px, xoffset, yoffset)
                g['transform'] = newmatrix
                text_width = text_width * tex_pt_to_px
                text_height = text_height * tex_pt_to_px
                baseline = baseline * tex_pt_to_px
                yinit = yinit * tex_pt_to_px
                g['opacity'] = self.opacity
                #g['viewBox'] = svgsoup.get('viewBox')

            output = svgsoup.renderContents().decode('utf8', errors='replace')

            #Add red box around the text
            if document._text_box:
                boxed = '''<g transform="translate(%0.1f,%0.1f)">
                <line x1="0" y1="0" x2="%i" y2="0" style="stroke: red"/>
                <line x1="%i" y1="0" x2="%i" y2="%i" style="stroke: red"/>
                <line x1="%i" y1="%i" x2="0" y2="%i" style="stroke: red"/>
                <line x1="0" y1="%i" x2="0" y2="0" style="stroke: red"/>
                <line x1="0" y1="%i" x2="%i" y2="%i" style="stroke: green"/>
                </g>'''
                output += boxed%( 0, float(yinit),
                                 text_width,
                                 text_width,text_width,text_height,
                                 text_width,text_height,text_height,
                                 text_height,
                                 baseline,text_width,baseline)

            #print output
        else:
            #Render as svg text
            #print('[WARNING !!!]: Classic text not yet implemented')
            textin = self.content
            style = ''
            if hasattr(self, 'color'):
                style += 'color:%s'%(self.color)

            output = '<text style="%s">%s</text>'%(style, textin.decode('utf-8'))
            tmpsvg = '<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" xmlns:xlink="http://www.w3.org/1999/xlink">%s</svg>'%output

            #Need to create a temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svt', prefix='beampytmp') as f:

                f.write(tmpsvg)
                # update file content to disk

                f.file.flush()
                # Get width and height
                text_width =  getsvgwidth(f.name)
                text_height = getsvgheight(f.name)

            # print(text_width, text_height)

        #Update positionner with the correct width and height of the final svg
        self.update_size(text_width, text_height)
        #Store the output svg
        logging.debug(type(output))
        self.svgout = output
        #Update the rendered state of the module
        self.rendered = True



    def parse_dvisvgm_svg(self, soup_data):
        """
        Function to transform the svg produced by dvisvgm.
        Make a global glyph store to use them as defs in svg
        to reduce the size off the global presentation.

        soup_data: BeautifulSoup parsed svg

        return: soup_data (without the defs part)
        """

        #Check if their is an entry in the global_store for the glyphs
        if 'glyphs' not in document._global_store:
            document._global_store['glyphs'] = {}

        #Extract defs containing glyphs from the svg file
        try:
            defs = soup_data.find_all('defs')[0].extract()
            for path in defs.find_all('path'):
                #store the id of the glyph given by dvisvgm

                path_id = path['id']
                #store the bezier coordinates of the glyph
                path_d = path['d']
                try:
                    hash_id = hashlib.md5(path_d).hexdigest()
                except:
                    hash_id = hashlib.md5(path_d.encode('utf8')).hexdigest()


                #print(hash_id, path_id)

                #check if the glyph is in the store or add it
                if hash_id not in document._global_store['glyphs']:
                    #Add the glyph to the store and create a new uniq id for it
                    uniq_id = "g_"+str(len(document._global_store['glyphs']))
                    new_svg = "<path d='%s' id='%s'/>"%(path_d, uniq_id)
                    document._global_store['glyphs'][ hash_id ] = {"old_id": path_id,
                                                                   "d": path_d,
                                                                   "id": uniq_id,
                                                                   'svg':new_svg}


                else:
                    data_store = document._global_store['glyphs'][ hash_id ]
                    uniq_id = data_store['id']

                #Find all the xlink:href to this glyph in the use part of the svg
                for tag in soup_data.find_all('use', { 'xlink:href':'#%s'%(path_id) }):
                    #Change the dvisvgm ref to the new uniq_id ref of the glyph
                    tag['xlink:href'] = '#%s'%(uniq_id)


                #Theirs is also definition use in the defs
                for use in defs.find_all('use', {'xlink:href':'#%s'%(path_id)}):
                    # print(use)
                    #store the id of the glyph given by dvisvgm
                    u_id = use['id']
                    use_id = "g_"+str( len(document._global_store['glyphs']) )
                    use['id'] = use_id
                    use['xlink:href'] = '#%s'%(uniq_id)
                    document._global_store['glyphs'][ use_id ] = {"old_id": u_id,  "id": use_id, 'svg':str(use)}
                    # print(use, u_id, use_id)

                    #Find all the xlink:href to this glyph in the use part of the svg
                    for tag in soup_data.find_all('use', { 'xlink:href':'#%s'%(u_id) }):
                        #Change the dvisvgm ref to the new uniq_id ref of the glyph
                        tag['xlink:href'] = '#%s'%(use_id)

        except:
            defs = None
            pass


        #Need to check if we have undefined reference
        #(they could be defined in other page of the)
        # We need to exclude <a> tag as html links could include "-" in the xlink:href
        for tag in soup_data.findAll(lambda x: x.name != 'a' and x is not None and x.has_attr('xlink:href')):
            if '-' in tag['xlink:href']:
                print('A svg reference is not defined:')
                print(tag)
                print('This is a bug in multipage of your dvisvgm version (bug fix in dvisvgm version > 2.7.2)')
                print('Run a single render for this text and parse it again! this should fix missings')
                self.local_render()
                self.render()

        return soup_data
