# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:48:01 2015

@author: hugo
"""

from beampy.commands import document
from beampy.functions import render_texts
import json
try:
    from cStringIO import StringIO
except:
    from io import StringIO

import sys
import os
import time
import io

import logging
_log = logging.getLogger(__name__)

# Get the beampy folder
curdir = os.path.dirname(__file__) + '/'


def save_layout():
    for islide in range(document._global_counter['slide']+1):
        slide = document._slides["slide_%i" % islide]
        slide.build_layout()


def reset_module_rendered_flag():
    for slide in document._slides:
        # document._slides[slide].svgout = []
        # document._slides[slide].svglayers = {}
        # document._slides[slide].htmlout = {}
        document._slides[slide].reset_rendered()

        for ct in document._slides[slide].contents:
            document._slides[slide].contents[ct].reset_outputs()
            # document._slides[slide].contents[ct].rendered = False
            # document._slides[slide].contents[ct].exported = False
            # document._slides[slide].contents[ct].svgout = None
            # document._slides[slide].contents[ct].htmlout = None



def save(output_file=None, format=None):
    """
        Function to render the document to html

    """

    _log.debug('Document at the begining of save method')
    _log.debug(document.print_variables())
    
    if document._quiet:
        sys.stdout = open(os.devnull, 'w')

    texp = time.time()
    bname = os.path.basename(output_file)
    bdir = output_file.replace(bname,'')

    if document._rendered:
        document._rendered = False
        reset_module_rendered_flag()

    file_ext = os.path.splitext(output_file)[-1]

    if 'html' in file_ext or format == 'html5':
        document._output_format = 'html5'
        render_texts()
        save_layout()
        output = html5_export()

    elif 'svg' in file_ext or format == "svg":
        document._output_format = 'svg'
        render_texts()
        save_layout()
        output = svg_export(bdir+'/tmp')
        output_file = None

    elif 'pdf' in file_ext or format == 'pdf':
        document._output_format = 'pdf'
        render_texts()
        save_layout()
        output = pdf_export(output_file)

        output_file = None

    if output_file is not None:
        with open(output_file, 'w') as f:
            # old py2 .encode('utf8')
            try:
                # Python 3 way to write output
                f.write(output)
            except Exception as e:
                print('Encode output as utf-8, for python2 compatibility')
                f.write(output.encode('utf8', 'replace'))

    # write cache file
    if document._cache is not None:
        document._cache.write_cache()

    # Set rendered flag to true for the whole document
    document._rendered = True

    print("="*20 + " BEAMPY END (%0.3f seconds) "%(time.time()-texp)+"="*20)


def pdf_export(name_out):

    # External tools cmd
    inkscapecmd = document._external_cmd['inkscape']
    pdfjoincmd = document._external_cmd['pdfjoin']

    # use inkscape to translate svg to pdf
    svgcmd = inkscapecmd+" --without-gui  --file='%s' --export-pdf='%s' -d=300"
    bdir = os.path.dirname(name_out)

    print('Render svg slides')
    aa = svg_export(bdir+'/tmp')

    print('Convert svg to pdf with inkscape')
    output_svg_names = []
    for islide in range(document._global_counter['slide']+1):
        print('slide %i'%islide)
        for layer in range(document._slides['slide_%i'%islide].num_layers + 1):
            print('layer %i'%layer)
            #Use inkscape to render svg to pdf
            res = os.popen(svgcmd%(bdir+'/tmp/slide_%i-%i.svg'%(islide, layer),
                                   bdir+'/tmp/slide_%i-%i.pdf'%(islide, layer))
                          )
            res.close()

            output_svg_names += ['slide_%i-%i'%(islide, layer)]

    #join all pdf
    res = os.popen(pdfjoincmd+' %s -o %s'%(' '.join(['"'+bdir+'/tmp/%s.pdf"'%sname for sname in output_svg_names]), name_out))
    output = res.read()

    res.close()
    msg = "Saved to %s"%name_out
    #os.system('rm -rf %s'%(bdir+'/tmp/slide_*'))

    return msg


def svg_export(dir_name, quiet=False):
    # Export evry slides in svg inside a given folder

    if quiet:
        sys.stdout = open(os.devnull, 'w')

    try:
        os.mkdir(dir_name)
    except:
        pass

    if dir_name[-1] != '/':
        dir_name += '/'

    for islide in range(document._global_counter['slide']+1):
        print("Export slide %i"%islide)

        slide = document._slides["slide_%i"%islide]

        # Render the slide
        slide.newrender()

        # The global svg glyphs need also to be added to the html5 page
        if 'glyphs' in document._global_store:
            # OLD .decode('utf-8',errors='replace') after the join for py2
            glyphs_svg = '<defs>%s</defs>' % (
                ''.join([glyph['svg'] for glyph in document._global_store['glyphs'].values()]))
        else:
            glyphs_svg = ''

        # join all svg defs (old .decode('utf-8', errors='replace') after the join for py2)
        def_svg = '<defs>%s</defs>'%(''.join(slide.svgdefout))
        for layer in range(slide.num_layers + 1):

            # save the list of rendered svg to a new dict as a string
            tmp = slide.svgheader + glyphs_svg + def_svg

            # Join all the svg contents (old .decode('utf-8', errors='replace') for py2)
            if layer in slide.svglayers:
                tmp += slide.svglayers[layer]
            else:
                tmp += '' #empty slide (when no svg are defined on slides)

            # Add the svgfooter
            tmp += slide.svgfooter

            with io.open(dir_name+'slide_%i-%i.svg'%(islide, layer), 'w', encoding='utf8') as f:
                try:
                    f.write(tmp)
                except Exception as e:
                    # For python 2
                    f.write(tmp.decode('utf8', 'replace'))

    return "saved to "+dir_name


def html5_export():

    with open(curdir+'statics/jquery.js','r') as f:
        jquery = f.read()

    with open(curdir+'statics/header_V2.html','r') as f:
        output = f.read()%jquery

    # Add the style
    htmltheme = document._theme['document']['html']
    output += """
    <!-- Default Style -->
    <style>
      * { margin: 0; padding: 0;
        -moz-box-sizing: border-box; -webkit-box-sizing: border-box;
        box-sizing: border-box; outline: none; border: none;
        }

      body {
        width: """+str(document._width)+"""px;
        height: """+str(document._height)+"""px;
        margin-left: -"""+str(int(document._width/2))+"""px; margin-top: -"""+str(int(document._height/2))+"""px;
        position: absolute; top: 50%; left: 50%;
        overflow: hidden;
        display: none;
        background-color: #ffffff;

      }

      section {
        position: absolute;
        width: 100%; height: 100%;
      }


      html { background-color: """+str(htmltheme['background_color'])+""";
        height: 100%;
        width: 100%;
      }

      video {
        visibility: hidden;
      }


      body.loaded { display: block;}
    </style>

    """
    # Loop over slides in the document
    # If we directly want to charge the content in pure html
    tmpout = {}
    tmpscript = {}
    global_store = ''
    for islide in range(document._global_counter['slide']+1):

        tnow = time.time()

        slide_id = "slide_%i"%islide
        tmpout[slide_id] = {}
        slide = document._slides[slide_id]

        # Render the slide
        slide.newrender()

        # Add a small peace of svg that will be used to get the data from the global store
        tmpout[slide_id]['svg'] = [] # Init the store for the differents layers
        #tmpout[slide_id]['layers_nums'] = max(slide.svglayers)
        tmpout[slide_id]['layers_nums'] = slide.num_layers
        tmpout[slide_id]['svg_header'] = slide.svgheader
        tmpout[slide_id]['svg_footer'] = slide.svgfooter

        # save the list of rendered svg to a new dict as a string that is loaded globally in the html
        # tmp = ''.join(slide.svgout).decode('utf-8', errors='replace')
        # OLD .decode('utf-8', errors='replace') after join for py2
        modulessvgdefs = ''.join(slide.svgdefout)
        global_store += "<svg><defs>" + modulessvgdefs

        for layer in range(slide.num_layers+1):
            print('write layer %i'%layer)
            # Export svg defs to the global store
            if layer in slide.svglayers:
                # OLD .decode('utf-8', errors='replace') for py2
                layer_content = slide.svglayers[layer]
            else:
                layer_content = '' #create an empty content (usefull when only html are present in one slide)

            global_store += "<g id='slide_{i}-{layer}'>{content}</g>".format(i=islide, layer=layer, content=layer_content)
            # Create an svg use for the given layer
            tmpout[slide_id]['svg'] += ['<use xlink:href="#slide_{i}-{layer}"/>'.format(i=islide, layer=layer)]

        global_store += '</defs></svg>'
        
        if slide.animout is not None:
            tmpout[slide_id]['svganimates'] = {}
            headers = []
            for ianim, data in enumerate(slide.animout):
                headers += [data['header']]
                data.pop('header')
                tmpout[slide_id]['svganimates'][data['anim_num']] = data

            # Add cached images to global_store
            # old comparision headers != []
            if headers:
                # OLD .decode('utf-8', errors='replace') after join for py2
                tmp = ''.join(headers)
                global_store += "<svg>%s</svg>"%(tmp)

        if slide.scriptout is not None:
            tmpscript['slide_%i'%islide] = ''.join(slide.scriptout)
            
        if slide.htmlout is not None:
            for layer in slide.htmlout:
                global_store += '<div id="html_store_slide_%i-%i">%s</div>'%(islide, layer,
                                                                             ''.join(slide.htmlout[layer]))

        print("Done in %0.3f seconds"%(time.time()-tnow))

        
    # Create a json file of all slides output (refs to store)
    jsonfile = StringIO()
    json.dump(tmpout,jsonfile, indent=None)
    jsonfile.seek(0)

    # The global svg glyphs need also to be added to the html5 page
    if 'glyphs' in document._global_store:
        glyphs_svg='<svg id="glyph_store"><defs>%s</defs></svg>'%( ''.join( [ glyph['svg'] for glyph in document._global_store['glyphs'].values() ] ) )
        output += glyphs_svg

    # Add the svg content
    try:
        output += "".join( global_store )
    except Exception as e:
        #Python 2 backcompatibility
        output += "".join( global_store ).decode('utf8')
    
    
    # Create store divs for each slides
    output += '<script> slides = eval( ( %s ) );</script>'%jsonfile.read()


    # Javascript output
    # format: scripts_slide[slide_i]['function_name'] = function() { ... }
    if tmpscript != {}:
        bokeh_required = False
        output += '\n <script> scripts_slide = {}; //dict with scrip function for slides \n'
        for slide in tmpscript:
            output += '\nscripts_slide["%s"] = {};\n scripts_slide["%s"]%s; \n'%(slide, slide, tmpscript[slide])
            if 'bokeh' in tmpscript[slide].lower():
                bokeh_required = True
                
        output += '</script>\n'

        if bokeh_required:
            cssbk, jsbk = get_bokeh_includes()
            output += cssbk + jsbk
            output
            
    with open(curdir+'statics/footer_V2.html', 'r') as f:
        output += f.read()

    return output


def check_content_type_change(slide, nothtml=True):
    """
        Function to change type of some slide contents (like for video html -> svg ) when render is changer from html5 to another
    """

    for ct in slide['contents']:
        if nothtml:
            if 'type_nohtml' in ct:
                print('done')
                ct['original_type'] = copy(ct['type'])
                ct['type'] = ct['type_nohtml']
        else:
            if 'original_type' in ct:
                ct['type'] = ct['original_type']


def display_matplotlib(slide_id, show=False):
    """
        Display the given slide in a matplotlib figure
    """
    import matplotlib
    matplotlib.use('agg')
    
    from matplotlib import pyplot
    from PIL import Image
    from numpy import asarray

    if document._quiet:
        sys.stdout = open(os.devnull, 'w')

    # Set document format to svg
    oldformat = document._output_format
    document._output_format = 'svg'

    
    slide = document._slides[slide_id]
    render_texts([slide.contents[eid] for eid in slide.element_keys if slide.contents[eid].type == 'text'])
    slide.build_layout()
    
    # Render the slide
    slide.newrender()

    svgout = slide.svgheader

    # Export glyphs
    if 'glyphs' in document._global_store:
        glyphs_svg = '<defs>%s</defs>' % (''.join([glyph['svg'] for glyph in document._global_store['glyphs'].values()]))
        # old .decode('utf-8', errors='replace') for py2
        svgout += glyphs_svg

    # join all svg defs (old .decode('utf-8', errors='replace') after join for py2)
    try:
        svgout += '<defs>%s</defs>' % (''.join(slide.svgdefout))
    except Exception as e:
        # For py 2
        svgout += '<defs>%s</defs>' % (''.join(slide.svgdefout)).decode('utf-8', errors='replace')

    for layer in range(slide.num_layers + 1):
        # Join all the svg contents (old .decode('utf-8', errors='replace') for py2)
        if layer in slide.svglayers:
            svgout += slide.svglayers[layer]

    # Add the svgfooter
    svgout += slide.svgfooter

    # Write it to a file
    tmpname = './.%s' % slide_id
    with io.open(tmpname+'.svg', 'w') as f:
        f.write(svgout)

    # Reset document format to oldformat
    reset_module_rendered_flag()
    document._output_format = oldformat

    # Change it a png
    inkscapecmd = document._external_cmd['inkscape']
    # use inkscape to translate svg to pdf
    svgcmd = inkscapecmd+" --without-gui  --file='%s' --export-png='%s' -b='white' -d=300"
    res = os.popen(svgcmd % (tmpname+'.svg', tmpname+'.png'))
    tmp = res.read()
    res.close()
    
    img = asarray(Image.open(tmpname+'.png'))

    # Remove files
    os.unlink(tmpname+'.svg')
    os.unlink(tmpname+'.png')

    pyplot.figure(dpi=300)
    pyplot.imshow(img)
    # pyplot.axis('off')
    pyplot.xticks([])
    pyplot.yticks([])
    pyplot.tight_layout()

    if show:
        pyplot.show()



def get_bokeh_includes():
    """
    Function to get bokeh dependencies (style and javascript) from their CDN
    
    Return string with <style>bokeh_css</style><script>bokeh js</script>
    """

    from bokeh.resources import CDN
    try:
        # Python 2
        from urllib2 import URLError
        from urllib2 import urlopen 
    except:
        from urllib.error import URLError
        from urllib.request import urlopen
        

    css_out = '<style>'
    for cssurl in CDN.css_files:
        cssname = cssurl[cssurl.rfind("/") + 1:]
        # Test if the css is stored in cache
        if document._cache is not None and document._cache.is_file_cached(cssname):
            csst = document._cache.get_cached_file(cssname)
            css_out += csst.decode('utf8', errors='replace') + '\n'
        else:
            try:
                print('Download %s' % cssurl)
                response = urlopen(cssurl, timeout=5)
                csst = response.read()
                if document._cache is not None:
                    document._cache.add_file(cssname, csst)
                # Don't forget to add a newline !
                css_out += csst.decode('utf8', errors='replace') + '\n'

            except URLError as e:
                print('Error in download: %s' % e)

    css_out += '</style>'

    js_out = '<script>'
    for jsurl in CDN.js_files:
        jsname = jsurl[jsurl.rfind("/") + 1:]
        if document._cache is not None and document._cache.is_file_cached(jsname):
            jst = document._cache.get_cached_file(jsname)
            js_out += jst.decode('utf8', errors='replace') + '\n'
        else:
            try:
                print('Download %s' % jsurl)
                response = urlopen(jsurl, timeout=5)
                jst = response.read()
                if document._cache is not None:
                    document._cache.add_file(jsname, jst)
                js_out += jst.decode('utf8', errors='replace') + '\n'
            except URLError as e:
                print('Error in download: %s' % e)

    js_out += '</script>'

    return css_out, js_out
