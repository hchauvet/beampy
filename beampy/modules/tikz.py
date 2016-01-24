# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import (gcs, convert_unit, latex2svg, add_to_slide,
                             check_function_args)
from beampy.geometry import positionner
import glob
import os
from bs4 import BeautifulSoup


def tikz(tikscommands, **kwargs):
    """
        Function to render tikz commands to svg

        options:
        --------
        - tikz_header: allow to add extra tikslibraries and style, everything that
                       is included befor \begin{document}

                       exp:
                       tikz_header = " \usetikzlibrary{shapes.geometric}
                                     % Vector Styles
                                     \tikzstyle{load}   = [ultra thick,-latex]
                                     \tikzstyle{stress} = [-latex]
                                     \tikzstyle{dim}    = [latex-latex]
                                     \tikzstyle{axis}   = [-latex,black!55]
                                     "
        - tex_packages: Add extra \usepackages in tex document.
                        Need to be a list of string

                        expl:
                        tex_packages = ['xolors','tikz-3dplot']

        - figure_options: options for \begin{tikzfigure}[options]

        - figure_anchor ['top_left']: set the anchor of tikz output svg 'top_left', 'bottom_left', 'top_right', bottom_right'
    """

    args = check_function_args(tikz, kwargs)

    textout = {'type': 'tikz', 'content': tikscommands,
               'args': args,
               'positionner': positionner(args['x'], args['y'], None, None),
               "render": render_tikz}


    return add_to_slide( textout )

def render_tikz( ct ):
    """
    Latex -> dvi -> svg for tikz image
    """

    tikzcommands = ct['content']
    args = ct['args']

    tex_pt_to_px = 96/72.27

    #replace '\slidewidth'
    tiktikzcommands = tikzcommands.replace( r'\slidewidth','%ipt'%0.75*document._width)

    #Include extrac packages for tex
    if args['tex_packages']:
        extra_tex_packages = '\n'.join(['\\usepackages{%s}'%pkg for pkg in args['tex_packages']])
    else:
        extra_tex_packages = ''

    #Include extra tikz headers
    if args['tikz_header']:
        extra_tex_packages += '\n' + args['tikz_header']

    #Tikzfigure options in []
    if args['figure_options']:
        tikz_fig_opts = '['+args['figure_options']+']'
    else:
        tikz_fig_opts = ''

    #Render to a dvi file
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

        #Change svg id with global ids
        #soup = make_global_svg_defs(soup)

        #Find the width and height
        svgsoup = soup.find('svg')
        g = soup.find('g')

        xinit, yinit, tikz_width, tikz_height = svgsoup.get('viewBox').split()
        tikz_width = float(tikz_width)
        tikz_height = float(tikz_height)

        #Default is args['figure_anchor'] == top_left
        dx = -float(xinit)
        dy = -float(yinit)

        if 'bottom' in args['figure_anchor']:
            dy = -float(yinit) - tikz_height

        if 'right' in args['figure_anchor']:
            dx = -float(xinit)-tikz_width

        newmatrix = 'scale(%0.3f) translate(%0.1f,%0.1f)'%(tex_pt_to_px, dx, dy)
        g['transform'] = newmatrix

        output = svgsoup.renderContents()

    else:
        #print(tex_msg)
        output = ''
        tikz_height = 0
        tikz_width = 0

    ct['positionner'].update_size(tikz_width, tikz_height)
    return output
