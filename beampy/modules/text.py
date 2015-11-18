# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo

Class to manage text for beampy
"""
from beampy import document
from beampy.functions import gcs, convert_unit, make_global_svg_defs, latex2svg, load_args_from_theme, color_text
from bs4 import BeautifulSoup
import re
import time
import sys 

def text( textin, x='center', y='auto', width=None, color="", size="",
         align='', font="", usetex = True):

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

    if width == None:
        width = str(document._width)
    else:
        width = str(width)

    args = {"x":str(x), "y": str(y) ,"font": font, "width": width,
            "font-size": size, "color": color, 'align':align, 'usetex': usetex }

    #Load theme properties
    load_args_from_theme('text', args)

    textout = {'type': 'text', 'content': textin, 'args': args,
               "render": render_text}

    #Add text to the document
    document._contents[gcs()]['contents'] += [ textout ]



def render_text( textin, args, usetex=True):
    """
        Function to render the text using latex

        latex -> dvi -> dvi2svgm -> svg

        Use the svg output for the text in the frame
    """

    #Check if their is width in args or if we need to use the default width
    if "width" in args:
        w = float(convert_unit(str(args['width'])))
    else:
        w = float(document._width)

    if usetex:

        #Check if a color is defined in args
        if 'color' in args:
            textin = color_text( textin, args['color'] )

        if 'center' in args['align']:
            texalign = r'\centering'
        else:
            texalign = ''

        #fontsize{size}{interlinear_size}
        pretex = r"""
        \documentclass[crop=True]{standalone}
        \usepackage[utf8x]{inputenc}
        \usepackage{fix-cm}
        \usepackage{hyperref}
        \usepackage[svgnames]{xcolor}
        \renewcommand{\familydefault}{\sfdefault}
        \usepackage{varwidth}
        \usepackage{amsmath}
        \usepackage{amsfonts}
        \usepackage{amssymb}
        \special{html}
        \begin{document}
        \begin{varwidth}{%ipt}
        %s
        \fontsize{%i}{%i}\selectfont %s

        \end{varwidth}
        \end{document}
        """%(w*(72.27/96.),texalign,args['font-size'],(args['font-size']+args['font-size']*0.1),textin)
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
                print("Baseline one TeX error and is put to 0")
                #print baseline

            #Get the group tag to get the transform matrix to add yoffset
            g = soup.find('g')
            transform_matrix = g.get('transform')


            if 'va' in args and args['va'] == 'baseline':
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
        args['x'] = convert_unit(args['x'])
        args['y'] = convert_unit(args['y'])
        args = ' '.join( [str(arg)+"='"+str(val)+"'" for arg, val in args.iteritems()] )
        output = "<text %s>%s</text>"%(args, textin.decode('utf-8'))
        #TODO: Need to fix the estimation of te width
        #print("[WARNING!!!] Width of classic svg text can't be estimated")
        text_width = 0
        text_height = 0

    return output, text_width, text_height
