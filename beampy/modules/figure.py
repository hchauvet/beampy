# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""

from beampy import document
from beampy.functions import (convert_unit, optimize_svg, gcs,
 make_global_svg_defs, getsvgwidth, getsvgheight, convert_pdf_to_svg, guess_file_type)

from beampy.modules.core import beampy_module
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO, StringIO
import hashlib
import base64
import tempfile
import os
import sys
#Try to import bokeh
try:
    from bokeh.embed import components
except:
    pass

class figure(beampy_module):

    def __init__(self, content, ext=None, **kwargs):
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

            - width[None]: Image width (None is the size of the image)

            - ext[None]: Image format, if None, format is guessed from filename.

        """

        #The type of the module
        self.type = 'svg'

        #Add the extra args to the module
        self.check_args_from_theme(kwargs)
        self.ext = ext

        #Register the content
        self.content = content

        #Special args for cache id
        self.args_for_cache_id = ['width','ext']

        #Check if the given filename is a string
        if type( self.content ) == type(''):
            #Check extension

            self.ext = guess_file_type( self.content, self.ext )

        else:
        #Check kind of objects that are passed to filename

            #Bokeh plot
            if "bokeh" in str(type(self.content)):
                self.ext = 'bokeh'

            #Mathplotlib figure
            if "matplotlib" in str(type(self.content)):
                self.ext = "matplotlib"

        ######################################

        #Check if the input filename can be treated
        if self.ext == None:
            print("figure format can't be guessed.")
            sys.exit(1)

        #Bokeh image
        elif self.ext == 'bokeh':
            self.type = 'html'

            #Todo get width and height from a bokeh figure
            if self.width is None:
                self.width = int(self.content.plot_width)
            if self.height is None:
                self.height = int(self.content.plot_height)

            #Do not cache this element if it's bokeh plot
            self.cache = False

        #Mpl figure
        elif self.ext == 'matplotlib':

            #import close to force the closing of the input figure
            from matplotlib.pyplot import close
            close(self.content) #close the figure

            #Set figure default width when it was not given as arguement
            if self.width == None:
                width_inch, height_inch = self.content.get_size_inches()
                self.width = convert_unit( "%fin"%(width_inch) )

            #Create a special args to create a unique id for caching

            #Generate the figure (in binary format as jpg) from the canvas
            with BytesIO() as tmpb:
                self.content.canvas.print_jpg(tmpb)
                tmpb.seek(0)
                md5t = hashlib.md5( tmpb.read() ).hexdigest()
                #print(md5t)

            #Add this new arg
            self.args['mpl_fig_hash'] = md5t
            self.mpl_fig_hash = md5t
            self.args_for_cache_id += ['mpl_fig_hash']

        #Other filetype images
        else:

            #Add file timestamp to an arguments for caching
            fdate = str(os.path.getmtime( self.content ))
            self.args['filedate'] = fdate
            self.filedate = fdate
            self.args_for_cache_id += ['filedate']

            if self.width is None:
                self.width = document._slides[gcs()].curwidth


        #Add this module to the current slide + add positionner
        self.register()

    def render(self):
        """
            function to render figures
        """


        #Svg // pdf render
        if self.ext in ('svg', 'pdf', 'matplotlib') :
            #Convert pdf to svg
            if self.ext == 'pdf' :
                figurein = convert_pdf_to_svg( self.content )

            #Convert matplotlib figure to svg
            elif self.ext == 'matplotlib':

                #Store mpl svg to a stringIO object
                with StringIO() as tmpf:
                    self.content.savefig(tmpf, bbox_inches='tight', format='svg')
                    tmpf.seek(0) #go to the biginig of the file

                    #store tmpf content as string in figurein variable
                    figurein = tmpf.read().encode('utf-8')

            #General case for svg format
            else:
                #Check if a filename is given for a svg file or directly read the content value
                if os.path.isfile(self.content):
                    with open(self.content) as f:
                        figurein = f.read()
                else:
                    figurein = self.content

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
            scale_x = self.positionner.width/float(svgwidth)
            #print svgwidth, svgheight, scale_x
            #scale_y = float(convert_unit(args['height']))/float(svgheight)
            good_scale = scale_x

            #BS4 get the svg tag content without <svg> and </svg>
            tmpfig = svgtag.renderContents()

            #Add the correct first line and last
            tmphead = '\n<g transform="scale(%0.5f)">'%(good_scale)
            output = tmphead + tmpfig + '</g>\n'

            figure_height = float(svgheight)*good_scale
            figure_width = self.width

            #Update the final svg size
            self.update_size(figure_width, figure_height)
            #Add the final svg output of the figure
            self.svgout = output

        #Bokeh images
        if self.ext == 'bokeh':

            # Run the bokeh components function to separate figure html div and js script
            figscript, figdiv = components(self.content, wrap_script=False)

            # Transform figscript to givea function name load_bokehjs
            tmp = figscript.splitlines()
            goodscript = '\n'.join( ['["load_bokeh"] = function() {'] + tmp[1:-1] + ['};\n'] )

            #Add the htmldiv to htmlout
            self.htmlout = figdiv
            #Add the script to scriptout
            self.jsout = goodscript

        #For the other format
        if self.ext in ('png', 'jpeg'):
            #Open image with PIL to compute size
            tmp_img = Image.open(self.content)
            _,_,tmpwidth,tmpheight = tmp_img.getbbox()
            scale_x = self.positionner.width/float(tmpwidth)
            figure_height = float(tmpheight) * scale_x
            figure_width = self.positionner.width

            if document._resize_raster:
                #Rescale figure to the good size (to improve size and display speed)
                out_img = resize_raster_image(tmp_img)
                figurein = base64.b64encode(out_img.read())
                out_img.close()
            else:
                with open( self.content, "r") as f:
                    figurein = base64.b64encode(f.read())

            tmp_img.close()

            if self.ext == 'png':
                output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/png;base64, %s" />'%(figure_width, figure_height, figurein)

            if self.ext == 'jpeg':
                output = '<image x="0" y="0" width="%s" height="%s" xlink:href="data:image/jpg;base64, %s" />'%(figure_width, figure_height, figurein)

            #Update the final size of the figure
            self.update_size(figure_width, figure_height)
            #Add the final svg to svgout
            self.svgout = output

        #print self.width, self.height
        #Update the rendered state of the module
        self.rendered = True


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
