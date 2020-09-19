# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import (gcs, color_text, getsvgwidth,
                              getsvgheight, small_comment_parser,
                              latex2svg, apply_to_all)

from beampy.modules.core import beampy_module
import tempfile
import os

from bs4 import BeautifulSoup
import sys
import hashlib
import logging
from itertools import groupby
from fontTools.ttLib import TTFont
import io
import base64
import uuid # To create unique id for glyphs


class text(beampy_module):
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

    nofont : bool, optional
        Render texts as paths rather than svg text. When True this
        ensure that texts glyphs are rendered properly on all
        devices. The default value is False, so that latex glyphs are
        rendered as svg texts.

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

        # Add special args for cache id Text need to be re-rendered
        # from latex if with, color or size are changed
        self.initial_width = self.width
        self.args_for_cache_id = ['initial_width', 'color', 'size',
                                  'align', 'opacity', 'nofont']


        # Init global store keys if not already created 
        if 'css_fonts' not in document._global_store:
            document._global_store['css_fonts'] = {}

        if 'svg_glyphs' not in document._global_store:
            document._global_store['svg_glyphs'] = {}
            
        if self.attrtocache is None:
            self.attrtocache = []

        if self.nofont:
            self.attrtocache += ['svg_glyphsids']
        else:
            self.attrtocache += ['css_fontsids']

        self.svg_glyphsids = []
        self.css_fontsids = []

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
        source = document._source_code.source(start=self.start_line,
                                              stop=self.stop_line)
        input_texts = small_comment_parser(source)

        self.content = r'\\'.join([r"%s" % t for t in input_texts])

    def pre_render(self):
        """
        Prepare the latex render of the text 
        """


        if self.usetex:
            # Check if a color is defined in args
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
            self.latex_text = template % (self.width.value*(72.27/96.),
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
            if self.nofont:
                options = ['-n', '-a', '--linkmark=none']
            else:
                options = ['-a', '--font-format=woff2,ah',
                           '--no-style', '--no-merge',
                           '--linkmark=none']
                
            self.svgtext = latex2svg(pretex, dvisvgmoptions=options)

        else:
            self.svgtext = ''

    # Define the render
    def render(self):
        """
        Text is rendered using latex if self.usetex = True if not
        use simple svg.

        When using latex, several processing pathway are possible:
        1. Using latex to produce dvi and then use dvisvgm to produce svg
        2. Using XeLatex to produce xdv and then use dvisvgm to produce svg

        The dvisvgm processor could render text as real font (only
        render correctly with web browser) or as paths (compatible
        with every svg display engine)
        """

        if self.usetex:

            if self.svgtext == '':
                # Run the local render
                self.local_render()

                # If it's still empty their is an error
                if self.svgtext == '':
                    print("Latex Compilation Error")

            self.soup = BeautifulSoup(self.svgtext, 'xml')
            svgsoup = self.soup.find('svg')

            # Find the width and height
            xinit, yinit, text_width, text_height = svgsoup.get('viewBox').split()
            text_width = float(text_width)
            text_height = float(text_height)
            xinit = float(xinit)
            yinit = float(yinit)

            # Get id of paths element to make a global counter over the entire document
            if 'path' not in document._global_counter:
                document._global_counter['path'] = 0

            if not self.nofont:
                # Parse css fonts and store them in a global store
                fonts = self.parse_dvisvg_svg(svgsoup)

                # Read those fonts and use fonttools to use them
                ttfonts = convert_svg_fonts(fonts)

                # Process dvisvgm svg to merge text tags correctly.
                self.merge_texts(svgsoup, ttfonts)

                # Find links to apply theme style
                self.change_link_style(svgsoup)

                # find the base line
                baseline = self.find_baseline(svgsoup)
            else:
                # New method with a global glyph store
                svgsoup = self.parse_dvisvgm_svg_nofont(svgsoup)

                # Find all links to apply the style defined in theme['link']
                self.change_link_style_nofont(svgsoup)

                # Find the baseline
                baseline = self.find_baseline_nofont(svgsoup)

            # Definition of the scale and translate to account for
            # xinit, yinit and font scaling of latex.

            if baseline == 0:
                print("No Baseline found in TeX and is put to 0")

            # Get the group tag where transform matrix will be set
            g = svgsoup.find('g')

            if getattr(self, 'va', False) and self.va == 'baseline':
                yoffset = -baseline
                xoffset = -xinit
                oldyinit = yinit  # for the box plot (see boxed below)
                yinit = -baseline + yinit
                baseline = -oldyinit + baseline

            else:
                yoffset = -yinit
                xoffset = -xinit
                # For the box plot
                baseline = -yinit + baseline
                yinit = 0

            tex_pt_to_px = 96/72.27
            newmatrix = 'scale(%0.3f) translate(%0.1f,%0.1f)' % (tex_pt_to_px,
                                                                 xoffset,
                                                                 yoffset)
            g['transform'] = newmatrix
            text_width = text_width * tex_pt_to_px
            text_height = text_height * tex_pt_to_px
            baseline = baseline * tex_pt_to_px
            yinit = yinit * tex_pt_to_px
            g['opacity'] = self.opacity

            output = svgsoup.renderContents().decode('utf8', errors='replace')

            # Add red box around the text
            if document._text_box:
                boxed = '''<g transform="translate(%0.1f,%0.1f)">
                <line x1="0" y1="0" x2="%i" y2="0" style="stroke: red"/>
                <line x1="%i" y1="0" x2="%i" y2="%i" style="stroke: red"/>
                <line x1="%i" y1="%i" x2="0" y2="%i" style="stroke: red"/>
                <line x1="0" y1="%i" x2="0" y2="0" style="stroke: red"/>
                <line x1="0" y1="%i" x2="%i" y2="%i" style="stroke: green"/>
                </g>'''
                output += boxed % (0, float(yinit),
                                   text_width,
                                   text_width, text_width, text_height,
                                   text_width, text_height, text_height,
                                   text_height,
                                   baseline, text_width, baseline)

        else:
            # Render as svg text
            # print('[WARNING !!!]: Classic text not yet implemented')
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
                text_width = getsvgwidth(f.name)
                text_height = getsvgheight(f.name)

            # print(text_width, text_height)

        #Update positionner with the correct width and height of the final svg
        self.update_size(text_width, text_height)
        #Store the output svg
        logging.debug(type(output))
        self.svgout = output
        #Update the rendered state of the module
        self.rendered = True

    def parse_dvisvg_svg(self, svgsoup):
        """
        Function to parse dvisvgm svg when glyphs are rendered as svg
        texts. First extract fonts in <style> in svg generated by
        dvisvgm (it contains base64 encoded font and their css name)
        and check if they are already defined in the presentation
        otherwise add them to the global css style.
        """

        style = svgsoup.find('style')

        stylep = style.string.strip()
        fonts = ['@font-face{'+f.strip() for f in stylep.split('@font-face{') if f != '']

        # remove style from main svg
        style.decompose()

        # Loop over font and store them if their are unknown.
        for font in fonts:
            try:
                font_id = hashlib.md5(font).hexdigest()
            except Exception as e:
                font_id = hashlib.md5(font.encode('utf8')).hexdigest()

            # fname = font.split('font-family:')[-1].split(';')[0]
            # print(font_id, fname)

            if font_id not in document._global_store['css_fonts']:
                document._global_store['css_fonts'][font_id] = font

            self.css_fontsids += [font_id]

        return fonts

    def merge_texts(self, svgsoup, fonts, min_dist=4):
        """
        Merge text glyphs inside svg tspan tag. The insertion of
        whitespace is based on a minimum distance between chars define by
        "min_dist" argument. The latex text should be transform with
        "--no-merge and --no-style" options in dvisvgm, these produce a
        text svg tag for each glyph of the text.

        The function process the input svg as follow:
        1. find all texts and group them by font (size and family and style)
           and style and fill
        2. Merge text of same words and add a whitespace between words.
        3. Create the new svg (using id for text and using the first text
           as an anchor to replace it the source svg)

        This function directly modify the svgsoup object and return
        nothing.

        Parameters
        ----------

        - svgsoup: beautifulsoup object,
            The input svg parsed using beautifulsoup
        - fonts: dictionary of font objects,
            The fonts used in the svg. Those fonts should be processed
            using fonttools (see function convert_svg_fonts).
        - min_dist: int optional,
            The threshold to add a whitespace between words (the default value is 4).
        """
        g = svgsoup.find('g')
        idt = 1
        for tag in g.find_all():
            tag['id'] = idt
            idt += 1

        texts = svgsoup.find_all('text')

        # Filter to group svg tag with the same parent
        def fontgroup(item):
            return str(item.parent.get('id'))

        # Filter to group tag with the same style (to make tspan inside text)
        def stylegroup(item):
            key = []
            for k in ['font-family', 'font-size', 'fill', 'style']:
                if item.has_attr(k):
                    key += [item.get(k)]

            return '|'.join(key)

        groupitems = []
        groupkeys = []
        for k, g in groupby(texts, fontgroup):
            groupkeys += [k]
            groupitems += [list(g)]

        keepids = []
        for g in groupitems:
            # Find the tag in the tree and replace it with the new one
            T = svgsoup.find(lambda a: a.get('id') == g[0].get('id'))
            keepids += [g[0].get('id')]

            # Group over style fill
            tspans = []
            for tk, th in groupby(g, stylegroup):
                gtexts = list(th)
                tx, ty, tc = merge_char(gtexts, fonts, min_dist)
                nspan = self.soup.new_tag('tspan')
                nspan.string = tc
                nspan['x'] = ','.join([str(x) for x in tx])
                nspan['y'] = ','.join([str(y) for y in ty])
                for attr in gtexts[0].attrs:
                    if attr not in ['id', 'x', 'y']:
                        nspan[attr] = gtexts[0][attr]

                tspans += [nspan]

            # Some cleaning
            T.clear()
            # Parent text should not have fill or style property
            for k in ['fill', 'style', 'font-size', 'font-family']:
                if T.has_attr(k):
                    del T[k]

            for tspan in tspans:
                T.append(tspan)

        # Remove all unused texts
        for t in svgsoup.find_all(lambda a: a.name == 'text' and a.get('id') not in keepids):
            t.decompose()

        # Remove all ids
        for t in svgsoup.find_all():
            del t['id']

    def find_baseline(self, svgsoup):
        """
        Find the baseline of the text. The baseline is defined by the "y"
        coordinate encounter in text node.
        """

        texts = svgsoup.find_all('text')

        baseline = 0
        for text in texts:
            if text.has_attr('y'):
                baseline = float(text.get('y'))
                break

        return baseline

    def change_link_style(self, svgsoup):
        """
        Change the style of link inside the svg to the style defined in
        the Beampy theme.
        """

        links = svgsoup.find_all('a')
        new_style = ' '.join(['%s:%s;'%(str(key), str(value)) for key, value in list(document._theme['link'].items())])
        for link in links:
            link['style'] = new_style

            # Need to override local properties
            for tag in ['fill', 'stroke', 'stroke-width']:
                for child in link.find_all(lambda t: t.has_attr(tag)):
                    child[tag] = 'inherit'

    def change_link_style_nofont(self, svgsoup):
        """
        Change link style according to the style defined in Beampy
        theme when text are transformed to path.
        """

        links = svgsoup.find_all('a')
        style = ' '.join(['%s:%s;'%(str(key), str(value)) for key, value in list(document._theme['link'].items())])
        for link in links:
            link['style'] = style

    def find_baseline_nofont(self, svgsoup):
        """
        Find the text baseline when texts are rendered as paths. The
        baseline is defined as the first "y" value encountered in use
        tags.
        """

        uses = svgsoup.find_all('use')

        baseline = 0
        for use in uses:
            if use.has_attr('y'):
                baseline = float(use.get('y'))
                break

        return baseline

    def parse_dvisvgm_svg_nofont(self, soup_data):
        """
        Function to transform the svg produced by dvisvgm.
        Make a global glyph store to use them as defs in svg
        to reduce the size off the global presentation.

        soup_data: BeautifulSoup parsed svg

        return: soup_data (without the defs part)
        """

        if 'svg_glyphs' not in document._global_store:
            document._global_store['svg_glyphs'] = {}

        # Extract defs containing glyphs from the svg file
        defs = soup_data.find_all('defs')[0].extract()

        for path in defs.find_all('path'):
            # store the id of the glyph given by dvisvgm

            path_id = path['id']
            # store the bezier coordinates of the glyph
            path_d = path['d']
            try:
                hash_id = hashlib.md5(path_d).hexdigest()
            except:
                hash_id = hashlib.md5(path_d.encode('utf8')).hexdigest()

            # check if the glyph is in the store or add it
            if hash_id not in document._global_store['svg_glyphs']:
                # Add the glyph to the store and create a new uniq id for it
                idt = str(uuid.uuid4())[:8]
                uniq_id = "g_"+idt
                new_svg = "<path d='%s' id='%s'/>" % (path_d, uniq_id)
                document._global_store['svg_glyphs'][hash_id] = {"old_id": path_id,
                                                                 "d": path_d,
                                                                 "id": uniq_id,
                                                                 'svg': new_svg}

            else:
                data_store = document._global_store['svg_glyphs'][hash_id]
                uniq_id = data_store['id']

            self.svg_glyphsids += [uniq_id]

            # Find all the xlink:href to this glyph in the use part of the svg
            for tag in soup_data.find_all('use', {'xlink:href':'#%s'%(path_id)}):
                # Change the dvisvgm ref to the new uniq_id ref of the glyph
                tag['xlink:href'] = '#%s' % (uniq_id)

            # Theirs is also definition use in the defs
            for use in defs.find_all('use', {'xlink:href':'#%s'%(path_id)}):
                # print(use)
                # store the id of the glyph given by dvisvgm
                u_id = use['id']
                use_id = "g_"+str(uuid.uuid4())[:8]
                use['id'] = use_id
                use['xlink:href'] = '#%s' % (uniq_id)
                document._global_store['svg_glyphs'][use_id] = {"old_id": u_id, "id": use_id,
                                                                'svg': str(use)}
                # print(use, u_id, use_id)
                self.svg_glyphsids += [use_id]

                # Find all the xlink:href to this glyph in the use part of the svg
                for tag in soup_data.find_all('use', {'xlink:href': '#%s' % (u_id)}):
                    # Change the dvisvgm ref to the new uniq_id ref of the glyph
                    tag['xlink:href'] = '#%s' % (use_id)


        # Need to check if we have undefined reference
        # (they could be defined in other page of the)
        #  We need to exclude <a> tag as html links could include "-" in the xlink:href
        for tag in soup_data.findAll(lambda x: x.name != 'a' and x is not None and x.has_attr('xlink:href')):
            if '-' in tag['xlink:href']:
                print('A svg reference is not defined:')
                print(tag)
                print('This is a bug in multipage of your dvisvgm version (bug fix in dvisvgm version > 2.7.2)')
                print('Run a single render for this text and parse it again! this should fix missings')
                self.local_render()
                self.render()

        return soup_data


def decode_font(b64font):
    """
    Decode base64 encoded font and use FontTools to parse them
    """

    b64decode = base64.b64decode(b64font)
    fontF = io.BytesIO(b64decode)
    
    return TTFont(fontF)


def convert_svg_fonts(fonts_list):
    '''
    Parse list of base64 font contained in the svg file produced by dvisvgm
    '''

    fonts = {}
    for f in fonts_list:
        fname = f.split('font-family:')[-1].split(';')[0]
        f64 = f.split('base64,')[-1].split(')')[0]

        fonts[fname] = decode_font(f64)

    return fonts


def get_glyph_width(glyph, ttfont, fontsize):
    """
    Get the width of a given glyph using fonttools.
    
    Refs
    ----

    https://github.com/lynneyun/Tutorials/blob/master/FontTools%20%26%20DrawBot/Navigating%20TTFs%20with%20fontTools.ipynb

    https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
    """
    gset = ttfont.getGlyphSet()
    cmap = ttfont.getBestCmap()
    units_per_em = float(ttfont['head'].unitsPerEm)

    if ord(glyph) in cmap and cmap[ord(glyph)] in gset:
        w = gset[cmap[ord(glyph)]].width
    else:
        w = gset['.notdef'].width

    # width in the unit of the pointsize (in svg it is given in px)
    w *= fontsize/units_per_em

    # Convert to pixel
    # pt2px = 1/0.75
    # w *= pt2px
    
    return w


def merge_char(text_items, fonts, dxmin=4):
    '''
    Merge words for a list of text svg tags based and add a whitespace
    where needed.
    '''

    x = float(text_items[0].get('x'))
    y = float(text_items[0].get('y'))
    allx = [x]
    ally = [y]
    fontsize = float(text_items[0].get('font-size'))
    font = text_items[0].get('font-family')
    c = text_items[0].text
    w = get_glyph_width(c, fonts[font], fontsize)
    for text in text_items[1:]:
        xn = float(text.get('x'))
        yn = float(text.get('y'))
        dx = (xn-(x+w))
        # print(dx,  text.text)
        # Add a spece
        if abs(dx) > dxmin:
            c += ' '
            allx += [allx[-1]+w, round(xn, 3)]
            ally += [round(yn, 3), round(yn, 3)]
        else:
            allx += [round(xn, 3)]
            ally += [round(yn, 3)]

        c += text.text

        x = xn
        w = get_glyph_width(text.text, fonts[font], fontsize)

    return allx, ally, c


def force_nofont():
    """
    Force all text in a presentation to be rendered as paths
    """
    def nofont(e):
        e.nofont = True
        e.rendered = False

    apply_to_all(element_type='text',
                 function=nofont)


def restore_nofont():
    """
    Restore nofont property as it is defined in args
    """

    def restore(e):
        e.nofont = e.args['nofont']
        e.rendered = False

    apply_to_all(element_type='text',
                 function=restore)



