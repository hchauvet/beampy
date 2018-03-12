# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import (gcs,  latex2svg)
from beampy.modules.core import beampy_module
from bs4 import BeautifulSoup


class tikz(beampy_module):

    def __init__(self, tikzcmd, **kwargs):
        """
        Function to render tikz commands to svg

        options:
        --------
        - tikz_header: allow to add extra tikslibraries and style, everything that
                       is included befor \begin{document}

                       exp:
                       tikz_header = "\\usetikzlibrary{shapes.geometric}
                                     % Vector Styles
                                     \tikzstyle{load}   = [ultra thick,-latex]
                                     \tikzstyle{stress} = [-latex]
                                     \tikzstyle{dim}    = [latex-latex]
                                     \tikzstyle{axis}   = [-latex,black!55]
                                     "
        - tex_packages: Add extra \\usepackages in tex document.
                        Need to be a list of string

                        expl:
                        tex_packages = ['xolors','tikz-3dplot']

        - figure_options: options for \begin{tikzfigure}[options]

        - figure_anchor ['top_left']: set the anchor of tikz output svg 'top_left', 'bottom_left', 'top_right', bottom_right'
        """

        self.type = 'svg'
        self.content = tikzcmd
        self.check_args_from_theme(kwargs)

        #Special args for cache id (when do we need to re-run latex render)
        self.args_for_cache_id = ['figure_options','tex_packages','tikz_header']

        self.register()


    def render(self):
        """
            Latex -> dvi -> svg for tikz image
        """

        tikzcommands = self.content
        #args = ct['args']

        tex_pt_to_px = 96/72.27

        #replace '\slidewidth'

        tiktikzcommands = tikzcommands.replace( r'\slidewidth','%ipt'%(0.75*document._slides[gcs()].curwidth))

        #Include extrac packages for tex
        if getattr(self, 'tex_packages', False):
            extra_tex_packages = '\n'.join(['\\usepackages{%s}'%pkg for pkg in self.tex_packages])
        else:
            extra_tex_packages = ''

        #Include extra tikz headers
        if getattr(self, 'tikz_header', False):
            extra_tex_packages += '\n%s'%(self.tikz_header)

        #Tikzfigure options in []
        if getattr(self,'figure_options', False):
            tikz_fig_opts = '['+self.figure_options+']'
        else:
            tikz_fig_opts = ''

        # Render to a dvi file
        pretex = """
        \\documentclass[tikz,svgnames]{standalone}
        \\usepackage[utf8x]{inputenc}

        %s

        \\begin{document}
            \\begin{tikzpicture}%s
            %s
            \\end{tikzpicture}
        \\end{document}
        """%(extra_tex_packages,tikz_fig_opts,tikzcommands)

        #latex2svg
        svgout = latex2svg(pretex)

        if svgout != '':

            #Parse the svg
            soup = BeautifulSoup(svgout, 'xml')

            #Find the width and height
            svgsoup = soup.find('svg')
            g = soup.find('g')

            xinit, yinit, tikz_width, tikz_height = svgsoup.get('viewBox').split()
            tikz_width = float(tikz_width) * tex_pt_to_px
            tikz_height = float(tikz_height) * tex_pt_to_px

            print(tikz_width, tikz_height)

            # Default is args['figure_anchor'] == top_left
            dx = -float(xinit)
            dy = -float(yinit)

            if 'bottom' in self.figure_anchor:
                dy = -float(yinit) - tikz_height

            if 'right' in self.figure_anchor:
                dx = -float(xinit)-tikz_width

            newmatrix = 'scale(%0.3f) translate(%0.1f,%0.1f)'%(tex_pt_to_px, dx, dy)
            g['transform'] = newmatrix

            output = svgsoup.renderContents()

        else:
            output = ''
            tikz_height = 0
            tikz_width = 0


        self.update_size(tikz_width, tikz_height)
        self.svgout = output
        self.rendered = True

