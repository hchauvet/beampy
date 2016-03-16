# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""

from beampy import document
from beampy.functions import (gcs, convert_unit, optimize_svg,
 make_global_svg_defs, getsvgwidth, getsvgheight, convert_pdf_to_svg,
 add_to_slide, check_function_args)
from beampy.geometry import positionner
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import base64
import tempfile
import os
import sys
#Try to import bokeh
try:
    from bokeh.embed import components
except:
    pass

def figure(filename, ext=None, **kwargs):
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
https://duckduckgo.com/?q=feder+inra&t=ffab
        - height[None]: Image heigt

        - ext[None]: Image format, if None, format is guessed from filename.

    """

    args = check_function_args(figure, kwargs)

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

            if '.pdf' in filename.lower():
                ext = 'pdf'

    else:
        if "bokeh" in str(type(filename)):
            ext = 'bokeh'

    ######################################


    if ext == None:
        print("figure format can't be guessed from file name")
        sys.exit(1)

    #Bokeh image
    elif ext == 'bokeh':
        #print('I got a bokeh figure')
        figscript, figdiv = components(filename, wrap_script=False)

        #Todo get width and height from a bokeh figure
        if args['width'] == None:
            args['width'] = '%ipx'%filename.plot_width
        if args['height'] == None:
            args['height'] = '%ipx'%filename.plot_height

        #Transform figscript to givea function name load_bokehjs
        tmp = figscript.splitlines()
        goodscript = '\n'.join( ['["load_bokeh"] = function() {'] + tmp[1:-1] + ['};\n'] )
        args['ext'] = ext
        args['script']=goodscript

        figout = {'type': 'html',
                  'content': figdiv,
                  'args': args,
                  'render': render_figure}

        return add_to_slide( figout, args['x'], args['y'], args['width'], args['height'] )


    #Other filetype images
    else:

        if args['width'] == None:
            args['width'] = document._width

        args['ext']=ext
        args['filename']=filename

        figout = {'type': 'figure', 'content': filename, 'args': args,
                  "render": render_figure}

        return add_to_slide( figout, args['x'], args['y'], args['width'], args['height'] )


def render_figure( ct ):

    """
        function to render figures
    """

    #read args in the dict
    args = ct['args']

    #Svg // pdf render
    if args['ext'] in ('svg', 'pdf') :

        #Convert pdf to svg
        if args['ext'] == 'pdf' :
            figurein = convert_pdf_to_svg( args['filename'] )
        else:
            #Check if a filename is given for a svg file or directly read the content value
            if 'filename' in args:
                with open(args['filename']) as f:
                    figurein = f.read()
            else:
                figurein = ct['content']

        #test if we need to optimise the svg
        if document._optimize_svg:
            figurein = optimize_svg(figurein)

        soup = BeautifulSoup(figurein, 'xml')

        #Change id in svg defs to use the global id system
        soup = make_global_svg_defs(soup)

        #Optimize the size of embeded svg images !
        if document._resize_raster:
            imgs = soup.findAll('image')
            if imgs:
                for img in imgs:
                    #True width and height of embed svg image
                    width, height = int( float(img['width']) ) , int( float(img['height']) )
                    img_ratio = height/float(width)
                    b64content = img['xlink:href']

                    try:
                        in_img =  BytesIO( base64.b64decode(b64content.split(';base64,')[1]) )
                        tmp_img = Image.open(in_img)
                        #print(tmp_img)
                        out_img = resize_raster_image( tmp_img )
                        out_b64 = base64.b64encode( out_img.read() )

                        #replace the resized image into the svg
                        img['xlink:href'] = 'data:image/%s;base64, %s'%(tmp_img.format.lower(), out_b64)
                    except:
                        print('Unable to reduce the image size')
                        pass

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
        scale_x = ct['positionner'].width/float(svgwidth)
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
        figure_width = ct['positionner'].width

    #Bokeh images
    if args['ext'] == 'bokeh':
        figurein = ct['content']
        figure_height = ct['positionner'].height
        figure_width =  ct['positionner'].width
        output = """%s"""%figurein


    #For the other format
    if args['ext'] in ['png', 'jpeg']:
        #Open image with PIL to compute size
        tmp_img = Image.open(args['filename'])
        _,_,tmpwidth,tmpheight = tmp_img.getbbox()
        scale_x = ct['positionner'].width/float(tmpwidth)
        figure_height = float(tmpheight) * scale_x
        figure_width = ct['positionner'].width

        if document._resize_raster:
            #Rescale figure to the good size (to improve size and display speed)
            out_img = resize_raster_image(tmp_img)
            figurein = base64.b64encode(out_img.read())
            out_img.close()
        else:
            with open( args['filename'], "r") as f:
                figurein = base64.b64encode(f.read())

        tmp_img.close()

    if args['ext'] == 'png':
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/png;base64, %s" />'%(figure_width, figure_height, figurein)

    if args['ext'] == 'jpeg':
        output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/jpg;base64, %s" />'%(figure_width, figure_height, figurein)

    ct['positionner'].update_size(figure_width, figure_height)

    return output


def resize_raster_image(PILImage, max_width=document._width, jpegqual=95):
    """
    Function to reduce the size of a given image keeping it's aspect ratio
    """
    img_w, img_h = PILImage.size
    img_ratio = img_h/float(img_w)

    if (img_w > document._width):
        print('Image resized from (%ix%i)px to (%ix%i)px'%(img_w, img_h, document._width, document._width*img_ratio))
        width = int(document._width)
        height = int(document._width * img_ratio)
        tmp_resized = PILImage.resize((width, height), Image.ANTIALIAS )
    else:
        tmp_resized = PILImage


    #Test if it's an RGBA that the A band contains info (like in PNG transparency) if not convert to RGB
    if tmp_resized.mode == 'RGBA':
        Amin, Amax = tmp_resized.getextrema()[-1]
        #If the band limits are equal -> no need for this alpha layer
        if Amin == Amax:
            print('Remove useless Alpha layer')
            tmp_resized = tmp_resized.convert(mode='RGB')

    #Save to stringIO
    out_img = BytesIO()
    tmp_resized.save( out_img, PILImage.format, quality=jpegqual, optimize=True )
    out_img.seek(0)

    return  out_img
