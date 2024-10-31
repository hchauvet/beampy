# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage tikz image for beampy
"""
from beampy.core.store import Store
from beampy.core.functions import (gcs,  latex2svg)
from beampy.core.module import beampy_module
from bs4 import BeautifulSoup, SoupStrainer
from beampy.core._svgfunctions import get_viewbox, make_unique_glyphs

class tikz(beampy_module):
    r"""
    Add Tikz/pgf graphic to the slide. 

    Parameters
    ----------

    tikzcmd : string
        String containing the main Tikz commands contained between
        \begin{tikzpicture} and \end{}tikzpicture}.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the Tikz graphic (the default theme set this to
        0). See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the Tikz graphic (the default theme sets this to 0).
        See positioning system of Beampy.

    tikz_header : str or None, optional
        Add extra Tiks/pgf libraries and style (Tiks commands \usetikzlibrary
        and \tickstyle), everything that is included before \begin{document}
        (the default theme sets this to None).

    tex_packages : list of string or None, optional
        Add extra Tex packages that are included using the \usepackages (the
        default theme sets this to None). The list should only contains the name
        of tex packages as strings.

        >>> tex_packages = ['xolors','tikz-3dplot']

    latex_pre_tikzpicture: str or None, optional
        Add extra latex commands that will be added between
        \begin{document} and \begin{tikzpicture} (the default theme
        sets this to None)

        >>> latex_pre_tikzpicture = r'\newcounter{mycounter}\setcounter{mycounter}{10}'

    figure_options : string or None,
        Tikz options added just after: \begin{tikzpicture}[options] (the default
        theme sets this to None).

    figure_anchor : {'top_left' or 'top_right' or 'bottom_left' or 'bottom_right' }, optional
        Anchor of the svg produced by Tikz.

    """

    def __init__(self, tikzcmd, x=None, y=None, width=None, height=None, margin=None, 
                 tikz_header=None, tex_packages=None, latex_pre_tikzpicture=None, figure_options=None,
                 figure_anchor=None, opacity=None, rotate=None, *args, **kwargs):


        # Register the module 
        super().__init__(x, y, width, height, margin, 'svg', **kwargs)

        # Set the argument as attributes of the module
        self.set(opacity=opacity, rotate=rotate, tikz_header=tikz_header, 
                tex_packages=tex_packages, latex_pre_tikzpicture=latex_pre_tikzpicture,
                figure_options=figure_options, figure_anchor=figure_anchor, 
                tikzcmd=tikzcmd)

        # Set the list of argument to exclude from theme default values
        self.theme_exclude_args = ['tikzcmd']
        
        # Update the signature of the __init__ call
        self.update_signature()

        # Load default from theme
        self.apply_theme()

        # Special args for cache id (when do we need to re-run latex render)
        self.args_for_cache_id = [self.figure_options, self.tex_packages, 
                                  self.tikz_header, self.latex_pre_tikzpicture]

        self.add_content(tikzcmd, 'svg')

    def render(self):
        """
            Latex -> dvi -> svg for tikz image
        """


        #latex2svg 
        svgout = latex2svg(self.latex)

        print(self.latex)

        if svgout == '':
            print('Beampy input:')
            print(self.latex)
            raise Exception('Latex Compilation Error, check the input')

        #Parse the svg
        only_svg = SoupStrainer('svg')
        soup = BeautifulSoup(svgout, 'lxml-xml', parse_only=only_svg)

        #Find the width and height
        xinit, yinit, tikz_width, tikz_height = get_viewbox(soup)


        # update the translation and scale
        tex_pt_to_px = 96/72.27
        self.scale = tex_pt_to_px
        # Default is args['figure_anchor'] == top_left
        dx = -xinit
        dy = -yinit
        self.translate = [dx, dy]

        # Update the width and the height of the latex element
        self.width = tikz_width * tex_pt_to_px
        self.height = tikz_height * tex_pt_to_px

        # TODO: translate that to the new system of Beampy 1.0
        """
        if 'bottom' in self.figure_anchor:
            self.positionner.y['anchor'] = 'bottom'

        if 'right' in self.figure_anchor:
            self.positionner.x['anchor'] = 'right'
        """

        soup = make_unique_glyphs(soup)

        # Add the svg to the module content
        self.svgdef = soup.find('g', id='page1').renderContents().decode('utf8', errors='replace')
        self.content_width = tikz_width * tex_pt_to_px
        self.content_height = tikz_height * tex_pt_to_px


    @property
    def latex(self):
        """
        Format the latex string from the input tickzcmd
        """

        # Add the latex preamble (see method below)
        latex = [self.preamble]

        if self.latex_pre_tikzpicture is None:
            pre = ''
        else:
            pre = self.latex_pre_tikzpicture

        latex += [r'\begin{document}',
                 pre]

        # Enclose Tikzfigure options in []
        if self.figure_options is not None:
            tikzoptions = f'[{self.figure_options}]'

        latex += [r'\begin{tikzpicture}'+tikzoptions]
        # replace '\slidewidth'
        tikzcmd = self.tikzcmd.replace(r'\slidewidth',
                                               '%ipt' % (0.75*Store.current_width()))

        latex += [tikzcmd,
                  r'\end{tikzpicture}'
                  r'\end{document}']

        return '\n'.join(latex)


    # TODO: should be improved for the loading of packages like in the text module
    @property
    def preamble(self):
        """
        Create the latex preamble with packages loading
        """

        # Include extra packages for tex
        if self.tex_packages is not None:
            extra_tex_packages = '\n'.join([rf'\usepackage{pkg}' for pkg in self.tex_packages])
        else:
            extra_tex_packages = ''

        #Include extra tikz headers
        if self.tikz_header is not None :
            extra_tex_packages += f'\n{self.tikz_header}'

        pre = [r'\documentclass[tikz,svgnames]{standalone}',
               r"\usepackage[utf8x]{inputenc}",
               extra_tex_packages,
               ]

        pre = '\n'.join(pre)

        return pre

