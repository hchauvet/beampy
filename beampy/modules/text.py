# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import (gcs, color_text, getsvgwidth,
                              getsvgheight, small_comment_parser,
                              latex2svg)

from beampy.modules.core import beampy_module
import tempfile
import os

from bs4 import BeautifulSoup
import sys
import hashlib
import logging

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
        Process the text inside the width
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
            \begin{document}
            """

            pretex += '\n'.join(self.extra_packages + document._latex_packages)
            pretex += self.latex_text
            pretex += '\end{document}'
            
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
            svgsoup = parse_dvisvgm_svg( svgsoup )
            
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

            output = str(svgsoup.renderContents())

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
            tmpfile, tmpnam = tempfile.mkstemp(prefix='beampytmp')
            with open( tmpnam + '.svg', 'w' ) as f:
                f.write( tmpsvg )

            text_width =  getsvgwidth(tmpnam + '.svg')
            text_height = getsvgheight(tmpnam + '.svg')

            os.remove(tmpnam + '.svg')

            # print(text_width, text_height)

        #Update positionner with the correct width and height of the final svg
        self.update_size(text_width, text_height)

        #Store the output svg
        logging.debug(type(output))
        self.svgout = output
        #Update the rendered state of the module
        self.rendered = True



def parse_dvisvgm_svg( soup_data ):
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
            uniq_id = "g_"+str( len(document._global_store['glyphs']) )
            new_svg = "<path d='%s' id='%s'/>"%(path_d, uniq_id)
            document._global_store['glyphs'][ hash_id ] = {"old_id": path_id, "d": path_d, "id": uniq_id, 'svg':new_svg}

            
        else:
            data_store = document._global_store['glyphs'][ hash_id ]
            uniq_id = data_store['id']
            
        #Find all the xlink:href to this glyph in the use part of the svg
        for tag in soup_data.find_all('use', { 'xlink:href':'#%s'%(path_id) }):
            #Change the dvisvgm ref to the new uniq_id ref of the glyph
            tag['xlink:href'] = '#%s'%(uniq_id)
                
        
        #Theirs is also definition use in the defs
        for use in defs.find_all('use', {'xlink:href':'#%s'%(path_id)}):
            #store the id of the glyph given by dvisvgm
            u_id = use['id']
            use_id = "g_"+str( len(document._global_store['glyphs']) )
            use['id'] = use_id
            use['xlink:href'] = '#%s'%(uniq_id)
            document._global_store['glyphs'][ use_id ] = {"old_id": u_id,  "id": use_id, 'svg':str(use)}

            #Find all the xlink:href to this glyph in the use part of the svg
            for tag in soup_data.find_all('use', { 'xlink:href':'#%s'%(u_id) }):
                #Change the dvisvgm ref to the new uniq_id ref of the glyph
                tag['xlink:href'] = '#%s'%(use_id)
        
    return soup_data
