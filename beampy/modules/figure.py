# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""

from beampy import document
from beampy.functions import gcs, convert_unit, optimize_svg, make_global_svg_defs, getsvgwidth, getsvgheight
from bs4 import BeautifulSoup
from PIL import Image
import base64
import tempfile
import os
#Try to import bokeh
try:
    from bokeh.embed import components
except:
    pass

def figure(filename,x='center',y='auto', width=None, height=None, ext=None):
    """
        Add figure to current slide
        Accepted format: [svg, png, jpeg, bokeh figure]

        - x['center']: x coordinate of the image
                       'center': center image relative to document._width
                       '+1cm": place image relative to previous element

        - y['auto']: y coordinate of the image
                     'auto': distribute all slide element on document._height
                     'center': center image relative to document._height (ignore other slide elements)
                     '+3cm': place image relative to previous element

        - width[None]: Image width, if None: width = document._width

        - height[None]: Image heigt

        - ext[None]: Image format, if None, format is guessed from filename.

    """
    #Check if the given filename is a string
    if type(filename) == type(''):
        #Check extension
        if ext == None:
            if '.svg' in filename.lower():
                ext = 'svg'

            if '.png' in filename.lower():
                ext = 'png'

            if ( '.jpeg' in filename.lower() ) or ( '.jpg' in filename.lower() ):
                ext = 'jpeg'
    else:
        if "bokeh" in str(type(filename)):
            ext = 'bokeh'

    ######################################


    if ext == None:
        print("figure format can't be guessed from file name")

    #Bokeh image
    elif ext == 'bokeh':
        #print('I got a bokeh figure')
        figscript, figdiv = components(filename, wrap_script=False)

        #Todo get width and height from a bokeh figure
        if width == None:
            width = '%ipx'%filename.plot_width
        if height == None:
            height = '%ipx'%filename.plot_height

        #Transform figscript to givea function name load_bokehjs
        tmp = figscript.splitlines()
        goodscript = '\n'.join( ['["load_bokeh"] = function() {'] + tmp[1:-1] + ['};\n'] )
        args = {"x":str(x), "y": str(y) , "width": str(width), "height": str(height),
                "ext": ext,  'script':goodscript}

        figout = {'type': 'html', 'content': figdiv, 'args': args,
                  'render': render_figure}

        document._contents[gcs()]['contents'] += [ figout ]


    #Other filetype images
    else:

        if width == None:
            width = str(document._width)
        else:
            width = str(width)
            
        if height != None:
            height = str(height)

        args = {"x":str(x), "y": str(y) , "width": width, "height": height,
                "ext": ext, 'filename':filename }

        with open(filename,"r") as f:
            figdata = f.read()

        #If it's png/jpeg figure we need to encode them to base64
        if ext != 'svg':
            figdata = base64.encodestring(figdata)

        figout = {'type': 'figure', 'content': figdata, 'args': args,
                  "render": render_figure}

        document._contents[gcs()]['contents'] += [ figout ]


def render_figure( figurein, args ):
    """
        function to render figures
    """

    #For svg figure
    if args['ext'] == 'svg':

        #test if we need to optimise the svg
        if document._optimize_svg:
            figurein = optimize_svg(figurein)

        soup = BeautifulSoup(figurein, 'xml')

        #Change id in svg defs to use the global id system
        soup = make_global_svg_defs(soup)

        svgtag = soup.find('svg')

        svg_viewbox = svgtag.get("viewBox")

        tmph = svgtag.get("height")
        tmpw = svgtag.get("width")
        if tmph == None or tmpw == None:
            fmpf, tmpname = tempfile.mkstemp(prefix="beampytmp")
            with open( tmpname+'.svg', 'w' ) as f:
                f.write(figurein)
                #print figurein
            tmph = getsvgheight( tmpname+'.svg' )
            tmpw = getsvgwidth( tmpname+'.svg' )
            #print tmpw, tmph
            os.remove(tmpname+'.svg')

        
        svgheight = convert_unit( tmph )
        svgwidth = convert_unit( tmpw )

        if svg_viewbox != None:
            svgheight = svg_viewbox.split(' ')[3]
            svgwidth = svg_viewbox.split(' ')[2]

        #SCALE OK need to keep the original viewBox !!!
        scale_x = float(convert_unit(args['width']))/float(svgwidth)
        #print svgwidth, svgheight, scale_x
        #scale_y = float(convert_unit(args['height']))/float(svgheight)
        good_scale = scale_x

        #BS4 get the svg tag content without <svg> and </svg>
        tmpfig = svgtag.renderContents()

        #print tmpfig[:100]

        #Add the correct first line and last
        #tmphead = '<g  transform="matrix(%s,0,0,%s,%s,%s)" viewBox="%s">'%(str(good_scale), str(good_scale), convert_unit(args['x']), convert_unit(args['y']), svg_viewbox))
        tmphead = '\n<g transform="scale(%0.5f)">'%(good_scale)
        output = tmphead + tmpfig + '</g>\n'

        figure_height = float(svgheight)*good_scale
        figure_width = convert_unit(args['width'])
        
    #Bokeh images
    if args['ext'] == 'bokeh':
        figure_height = float(convert_unit(args['height']))
        output = """%s"""%figurein


    #For the other format
    if args['ext'] not in ['svg','bokeh']:
        #Open image with PIL to compute size
        tmp_img = Image.open(args['filename'])
        _,_,tmpwidth,tmpheight = tmp_img.getbbox()
        tmp_img.close()
        scale_x = float(convert_unit(args['width']))/float(tmpwidth)
        figure_height = float(tmpheight) * scale_x
        figure_width = convert_unit(args['width'])
        
    if args['ext'] == 'png':
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/png;base64, %s" />'%(figure_width, figure_height, figurein)

    if args['ext'] in ['jpg','jpeg']:
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/jpg;base64, %s" />'%(figure_width, figure_height, figurein)
    
    #Save the heigt
    args['height'] = figure_height
    
    return output, float(figure_width), float(figure_height)
