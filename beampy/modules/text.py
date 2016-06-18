# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import (gcs, convert_unit, make_global_svg_defs,
    latex2svg, load_args_from_theme, color_text, add_to_slide,
    check_function_args, get_command_line, getsvgwidth, getsvgheight)

from beampy.modules.core import beampy_module
import tempfile
import os

from bs4 import BeautifulSoup
import re
import time
import sys

class text(beampy_module):

    def __init__(self, textin, **kwargs):
        """
            Function to add a text to the current slide

            Options
            -------

            - x['center']: x coordinate of the image
                           'center': center image relative to document._width
                           '+1cm": place image relative to previous element

            - y['auto']: y coordinate of the image
                         'auto': distribute all slide element on document._height
                         'center': center image relative to document._height (ignore other slide elements)
                         '+3cm': place image relative to previous element

            Exemples
            --------

            text('this is my text', '20', '20')
        """

        self.type = 'text'
        self.check_args_from_theme(kwargs)
        self.content = textin

        #Height of text is None (it need to be computed)
        self.height = None
        #Check width
        if self.width == None:
            self.width = float(document._width)

        #Register the function to the current slide
        self.register()

    #Define the render
    def render(self):
        """
            Text is rendered using latex if self.usetex = True if not use simple svg
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

            #fontsize{size}{interlinear_size}
            pretex = r"""
            \documentclass[crop=True]{standalone}
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
            \begin{varwidth}{%ipt}
            %s
            \fontsize{%i}{%i}\selectfont %s

            \end{varwidth}
            \end{document}
            """%( self.width*(72.27/96.), texalign,
                self.size, (self.size+self.size*0.1),
                textin )
            #96/72.27 pt_to_px for latex

            #latex2svg
            testsvg = latex2svg( pretex )

            if testsvg == '':
                print("Latex Compilation Error")
                print("Beampy Input")
                print(pretex)
                sys.exit(0)

            #Parse the ouput with beautifullsoup
            soup = BeautifulSoup(testsvg, 'xml')
            svgsoup = soup.find('svg')

            #Get id of paths element to make a global counter over the entire document
            if 'path' not in document._global_counter:
                document._global_counter['path'] = 0

            #Create unique_id_ with time
            text_id =  ("%0.2f"%time.time()).split('.')[-1]
            for path in soup.find_all('path'):
                pid = path.get('id')
                new_pid = '%s_%i'%(text_id, document._global_counter['path'])
                testsvg = re.sub(pid,new_pid, testsvg)
                #path['id'] = new_pid //Need to change also the id ine each use elements ... replace (above) is simpler
                document._global_counter['path'] += 1

            #Reparse the svg
            soup = BeautifulSoup(testsvg, 'xml')

            #Change id in svg defs to use the global id system
            soup = make_global_svg_defs(soup)

            svgsoup = soup.find('svg')

            xinit, yinit, text_width, text_height = svgsoup.get('viewBox').split()
            text_width = float(text_width)
            text_height = float(text_height)

            #Find all links to apply the style defined in theme['link']
            links = soup.find_all('a')
            style = ' '.join(['%s:%s;'%(str(key), str(value)) for key, value in document._theme['link'].items()])
            for link in links:
                link['style'] = style

            #Use the first <use> in svg to get the y of the first letter
            try:
                uses = soup.find_all('use')
            except:
                print soup

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
                g = soup.find('g')
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
                #g['viewBox'] = svgsoup.get('viewBox')

            output = svgsoup.renderContents()

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

            print(text_width, text_height)

        #Update positionner with the correct width and height of the final svg
        self.update_size(text_width, text_height)

        #Store the output svg
        self.svgout = output
        #Update the rendered state of the module
        self.rendered = True
