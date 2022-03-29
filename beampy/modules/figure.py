# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 19:05:18 2015

@author: hugo
"""

from beampy.core.store import Store
from beampy.core.functions import (convert_unit, optimize_svg, gcs, convert_pdf_to_svg,
                                   convert_eps_to_svg,
                                   guess_file_type)
from beampy.core._svgfunctions import (get_svg_size, get_viewbox, make_global_svg_defs, apply_style_to_all_images)
from beampy.core.module import beampy_module
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO, StringIO
import hashlib
import base64
import tempfile
import os
import sys
from pathlib import Path
from urllib.parse import quote
# Try to import bokeh
try:
    import bokeh
    print('found bokeh version %s' % bokeh.__version__)
    from bokeh.embed import components
except:
    pass


class figure(beampy_module):
    """
    Include a figure to the current slide. Figure formats could be (**svg**,
    **pdf**, **png**, **jpeg**, **gif**, **matplotib figure**, 
    and **bokeh figure**)

    Parameters
    ----------

    content : str or matplotlib.figure or bokeh.figure
        Figure input source. To load file, `content` is the path to the file.
        For matplotlib and bokeh, `content` is the python object figure of
        either matplotlib or bokeh.

    ext : {'svg','jpeg','png','pdf', 'gif', 'bokeh','matplotlib'} or None, optional 
       Image format defined as string (the default value is None,
       which implies that the image format is guessed from file or
       python object name.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the figure (the default is 'center').

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the figure (the default is 'auto', which implies
        equal blank width between 'auto' positioned elements)

    width : int or float or None, optional
        Width of the figure (the default is None, which implies that the width
        is width of the image).

    height : int or float or None, optional
        Height of the figure (the default is None, which implies that the width
        is width of the image).

    optimize : boolean, optional
        Use the svg optimizer to reduce it's size
    """

    def __init__(self, content, x=None, y=None, width=None, height=None,
                 margin=None, ext=None, optimize=None, resize_raster=None,
                 *args, **kwargs):

        # Check content type
        ext = find_content_ext(content, ext)

        modtype = 'svg'
        if ext == 'bokeh':
            modtype = 'html'
            if width is None:
                width = int(content.plot_width)
            if height is None:
                height = int(content.plot_height)

        elif ext == 'matplotlib':
            width_inch, height_inch = content.get_size_inches()
            if width is None:
                width = convert_unit("%fin"%(width_inch))
            if height is None:
                height = convert_unit("%fin"%(height_inch))
        else:
            # Default with for static figure included in beampy
            if width is None and height is None:
                width = '95%'

        # Register the module
        super().__init__(x, y, width, height, margin, modtype, **kwargs)

        # Add arguments as attributes
        self.set(content=content, ext=ext, optimize=optimize,
                 resize_raster=resize_raster)

        # Update the signature
        self.update_signature(content, self.x, self.y, self.width, self.height,
                              self.margin, ext=ext, optimize=optimize,
                              resize_raster=resize_raster, *args, **kwargs)

        # Apply theme default for None value and set arguments as attrs
        self.apply_theme(exclude=['ext', 'optimize', 'resize_raster'])

        if optimize is None:
            self.optimize = Store.get_layout()._optimize_svg

        if resize_raster is None:
            self.resize_raster = Store.get_layout()._resize_raster

        # Special args for cache id
        self.args_for_cache_id = [width,
                                  ext,
                                  self.optimize,
                                  self.resize_raster]

        # Some special for cache depends on type
        if ext == 'bokeh':
            self.cache = False

        elif ext == 'matplotlib':
            # import close to force the closing of the input figure
            from matplotlib.pyplot import close
            close(content)

            # Generate the figure (in binary format as jpg) from the canvas
            # and hash the jpg file
            with BytesIO() as tmpb:
                content.canvas.print_jpg(tmpb)
                tmpb.seek(0)
                md5t = hashlib.md5( tmpb.read() ).hexdigest()

            self.args_for_cache_id += [md5t]

        else:
            # For files add the timestamp of file in cache

            # Add file timestamp to an arguments for caching
            fdate = str(os.path.getmtime(content))
            self.args_for_cache_id += [fdate]

        # Add the content this will run the render method if needed
        self.add_content(content, modtype)

    def render(self):
        """
            function to render figures to svg or html
        """

        #  Ani content that can be reduced to svg (pdf, eps, matplotlib)
        if self.ext in ('svg', 'pdf', 'eps', 'matplotlib'):
            #  Convert pdf to svg
            if self.ext == 'pdf':
                figurein = convert_pdf_to_svg(self.content)
            elif self.ext == 'eps':
                figurein = convert_eps_to_svg(self.content)

            #  Convert matplotlib figure to svg
            elif self.ext == 'matplotlib':

                #Store mpl svg to a stringIO object
                with StringIO() as tmpf:
                    self.content.savefig(tmpf, bbox_inches='tight', format='svg')
                    tmpf.seek(0) #go to the biginig of the file

                    #store tmpf content as string in figurein variable
                    figurein = tmpf.read().encode('utf-8')

            #  General case for svg format
            else:
                # Check if a filename is given for a svg file or directly read
                # the content value
                if os.path.isfile(self.content):
                    with open(self.content) as f:
                        figurein = f.read()
                else:
                    figurein = self.content

            # test if we need to optimise the svg
            if self.optimize:
                figurein = optimize_svg(figurein)

            soup = BeautifulSoup(figurein, 'xml')

            #Change id in svg defs to use the global id system
            soup = make_global_svg_defs(soup)

            #Optimize the size of embeded svg images !
            if self.resize_raster:
                imgs = soup.findAll('image')
                if imgs:
                    for img in imgs:
                        #True width and height of embed svg image
                        width, height = int( float(img['width']) ) , int( float(img['height']) )
                        img_ratio = height/float(width)
                        b64content = img['xlink:href']

                        try:
                            in_img =  BytesIO(base64.b64decode(b64content.split(';base64,')[1]))
                            tmp_img = Image.open(in_img)
                            # TODO: let user set the lower limit
                            out_img = resize_raster_image(tmp_img, max_width=max(self.width.value, 512))
                            out_b64 = base64.b64encode(out_img.read()).decode('utf8')

                            #replace the resized image into the svg
                            img['xlink:href'] = 'data:image/%s;base64, %s'%(tmp_img.format.lower(), out_b64)
                        except Exception as e:
                            print('Unable to reduce the image size')
                            print(e)


            #  Get the size of the svg
            svgwidth, svgheight = get_svg_size(soup)

            # BS4 get the svg tag content without <svg> and </svg>
            svgtag = soup.find('svg')
            tmpfig = svgtag.renderContents().decode('utf8')

            # Scale the figure according to the given width
            requested_width = self.width.value
            requested_height = self.height.value

            assert requested_width != 'scale' and requested_height != 'scale', "width and height could not be BOTH set to 'scale'"

            scale = 1
            if requested_width not in [None, 'scale'] and requested_height in [None, 'scale']:
                # SCALE OK need to keep the original viewBox !!!
                scale = (requested_width/svgwidth)
                figure_height = svgheight * scale
                figure_width = requested_width

            # Scale the figure according to the given height
            if requested_height not in [None, 'scale'] and requested_width in [None, 'scale']:
                scale = requested_height/svgheight
                figure_height = requested_height
                figure_width = svgwidth * scale

            # Dont scale the figure let the user fix the width height
            if requested_height not in [None, 'scale'] and requested_width not in [None, 'scale']:
                figure_height = requested_width
                figure_width = requested_height       
            else:
                # Apply the scaling to the final svg
                # Scaling is applied directly to figure width heigh
                # This perform better in webkit engine than do scaling at the rendering time
                # self.scale = scale
                pass

            self.width = figure_width
            self.height = figure_height

            # Add the final content to the module
            # Use <image tag with data URI, DO NOT LET Firefox or Chrome do the scaling 
            # this could end with terrible display calculation time
            soup = apply_style_to_all_images(soup, 'image-rendering: -webkit-optimize-contrast;') # for chrome blurry scale < 1.0
            svgin = str(soup)
            # protect some special char for uri
            # https://codepen.io/tigt/post/optimizing-svgs-in-data-uris
            svgin = svgin.replace('"', "'")
            svgin = quote(svgin, safe=' =:/')


            svginimg = (f'<image x="0" y="0" width="{figure_width}" '
                        f'height="{figure_height}" '
                        'preserveAspectRatio="none" '
                        'image-rendering="optimizeQuality" '
                        f'xlink:href="data:image/svg+xml;charset=utf8,{svgin}" '
                        f'/>')

            # The sodipodi link is for inkscape, as it's unable to open data:image/svg+xml 
            # correctly f'sodipodi:absref="{Path(self.content).absolute()}" ' but this is 
            # not perfectly rendered 
            # An alternative for inkscape directly import the raw svg structure in a group
            svgaltimg = (f'<g transform="scale({scale})">'
                         f'{tmpfig} '
                         '</g>')

            self.svgdef = svginimg
            self.svgaltdef = svgaltimg
            self.content_width = figure_width
            self.content_height = figure_height

        #Bokeh images
        if self.ext == 'bokeh':

            # Change the sizing mode (need scale_both) to adapt size of the figure
            self.content.sizing_mode = 'scale_both'
            # Run the bokeh components function to separate figure html div and js script
            figscript, figdiv = components(self.content,
                                           wrap_script=False)

            # Transform figscript to givea function name load_bokehjs
            tmp = figscript.splitlines()
            goodscript = '\n'.join( ['["load_bokeh"] = function() {'] + tmp[1:-1] + ['};\n'] )

            #Add the htmldiv to htmlout
            requested_width = self.width.value
            requested_height = self.height.value

            # TODO: do scaling also for bokeh figure
            assert requested_width in [None, 'scale'], "For Bokeh figure width could not bet None or 'scale'"
            assert requested_height in [None, 'scale'], "For Bokeh figure height could not bet None or 'scale'"

            htmlout = (f"<div id='bk_resizer' width='{requested_width}px' "
                       f"height='{requested_height}px' "
                       f"style='width: {requested_width}px; height: {requested_height}px; "
                       "transform-origin: left top 0px;'> "
                       f"{figdiv} </div>")

            # Set the html to the beampy_module
            self.html = htmlout
            self.content_width = requested_width
            self.content_height = requested_height

            #Add the script to scriptout
            self.jsout = goodscript

        #For the other format
        if self.ext in ('png', 'jpeg', 'gif'):
            #Open image with PIL to compute size
            tmp_img = Image.open(self.content)
            _,_,tmpwidth,tmpheight = tmp_img.getbbox()

            # Scale the figure according to the given width
            requested_width = self.width.value
            requested_height = self.height.value

            if requested_width not in [None, 'scale'] and requested_height in [None, 'scale']:
                # SCALE OK need to keep the original viewBox !!!
                scale = requested_width/float(tmpwidth)
                figure_height = float(tmpheight) * scale
                figure_width = requested_width

            # Scale the figure according to the given height
            if requested_height not in [None, 'scale'] and requested_width in [None, 'scale']:
                scale = requested_height/float(tmpheight)
                figure_height = requested_height
                figure_width = float(tmpwidth) * scale

            # Dont scale the figure let the user fix the width height
            if requested_height not in [None, 'scale'] and requested_width not in [None, 'scale']:
                figure_height = requested_height
                figure_width = requested_width

            if self.resize_raster:
                #Rescale figure to the good size (to improve size and display speed)
                if self.ext == 'gif':
                    print('Gif are not resized, the original size is taken!')
                    with open(self.content, "rb") as f:
                        figurein = base64.b64encode(f.read()).decode('utf8')
                else:
                    # TODO: let the user select the min size 512 of raster resizing
                    out_img = resize_raster_image(tmp_img, max_width=max(figure_width, 512))
                    figurein = base64.b64encode(out_img.read()).decode('utf8')
                    out_img.close()
            else:
                with open(self.content, "rb") as f:
                    figurein = base64.b64encode(f.read()).decode('utf8')

            tmp_img.close()

            b64format = {'gif': 'data:image/gif;base64',
                         'jpeg': 'data:image/jpg;base64',
                         'png': 'data:image/png;base64'}

            outformat = b64format[self.ext]
            output = (f'<image x="0" y="0" width="{figure_width}" '
                      f'height="{figure_height}" '
                      
                      f'xlink:href="{outformat}, {figurein}" />')

            # Add the final svg to svgout
            self.svgdef = output

            # Update the final size of the figure
            self.width = figure_width
            self.height = figure_height
            self.content_width = figure_width
            self.content_height = figure_height


def resize_raster_image(PILImage, max_width=None, jpegqual=96):
    """
    Function to reduce the size of a given image keeping it's aspect ratio
    """

    if max_width == None:
        max_width = Store.get_layout()._width

    img_w, img_h = PILImage.size
    img_ratio = img_h/float(img_w)

    if (img_w > Store.get_layout()._width):
        print('Image resized from (%ix%i)px to (%ix%i)px'%(img_w, img_h, max_width, max_width*img_ratio))
        width = int(max_width)
        height = int(max_width * img_ratio)
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


def find_content_ext(content, ext=None) -> str:
    """Check the type of incoming content and return it's type (extension)

    Parameters:
    -----------

    - content, object or string:
        The incomming content of the figure could be file given by a string, or
        a matplotlib or boheh object.

    - ext: string or None:
        The given extension
    """

    # Check if the given filename is a string
    if isinstance(content, str):
        # Check extension
        ext = guess_file_type(content, ext)
    else:
        # Check kind of objects that are passed to filename
        # Bokeh plot
        if "bokeh" in str(type(content)):
            ext = 'bokeh'

        # Mathplotlib figure
        if "matplotlib" in str(type(content)):
            ext = "matplotlib"

    if ext is None:
        print("figure format can't be guessed.")
        sys.exit(1)

    return ext
