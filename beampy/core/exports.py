# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:48:01 2015

@author: hugo
"""
from multiprocessing import Pool
from beampy.core.store import Store
from beampy.core._svgfunctions import export_svgdefs
from string import Template
import json

from io import StringIO

import sys
import os
import time
import io

import logging
_log = logging.getLogger(__name__)

from pathlib import Path
# Get the beampy folder
curdir = Path(os.path.dirname(__file__))
curdir = str(curdir.parent.absolute()) + '/'

# Is it python 2 or 3
if (sys.version_info > (3, 0)):
    py3 = True
else:
    py3 = False


def save_layout():
    for islide in range(len(Store)):
        slide = Store.get_slide(f'slide_{islide+1}')
        # TODO: slide.build_layout()


def reset_module_rendered_flag():
    for slide in document._slides:
        document._slides[slide].reset_rendered()

        for ct in document._slides[slide].contents:
            document._slides[slide].contents[ct].reset_outputs()


def save(output_file=None, format=None):
    """
        Function to render the document to html

    """

    document = Store.get_layout()
    _log.debug('Document at the begining of save method')
    #_log.debug(document.print_variables())

    if document._quiet:
        sys.stdout = open(os.devnull, 'w')

    texp = time.time()
    bname = os.path.basename(output_file)
    bdir = output_file.replace(bname,'')

    #if document._rendered:
    #    document._rendered = False
    #    reset_module_rendered_flag()

    file_ext = os.path.splitext(output_file)[-1]

    if 'html' in file_ext or format == 'html5':
        document._output_format = 'html5'
        # TODO: save_layout()
        output = html5_export()

    elif 'svg' in file_ext or format == "svg":
        document._output_format = 'svg'
        # TODO: save_layout()
        output = svg_export(bdir+'/tmp')
        output_file = None

    elif 'pdf' in file_ext or format == 'pdf':
        document._output_format = 'pdf'
        # TODO: save_layout()
        output = pdf_export(output_file)

        output_file = None

    if output_file is not None:
        with open(output_file, 'w') as f:
            # old py2 .encode('utf8')
           if py3:
               # Python 3 way to write output
               f.write(output)
           else:
               print('Encode output as utf-8, for python2 compatibility')
               f.write(output.encode('utf8', 'replace'))

               
               
    # write cache file
    if Store.cache() is not None:
        Store.cache().save()

    # Set rendered flag to true for the whole document
    document._rendered = True

    print("="*20 + " BEAMPY END (%0.3f seconds) "%(time.time()-texp)+"="*20)


def pdf_export(name_out):

    # External tools cmd
    document = Store.get_layout()
    inkscapecmd = document._external_cmd['inkscape']
    pdfjoincmd = document._external_cmd['pdfjoin']

    # use inkscape to translate svg to pdf
    svgcmd = inkscapecmd+" --export-filename='%s' --export-dpi=300 %s"
    bdir = os.path.dirname(name_out)

    print('Render svg slides')
    aa = svg_export(bdir+'/tmp')

    # Create slide names (with layers)
    output_svg_names = []
    for islide in range(len(Store)):
        for layer in range(Store.get_slide(f'slide_{islide+1}').num_layers + 1):
            output_svg_names += ['slide_%i-%i'%(islide, layer)]

    # Convert svg to pdf in a Pool of worker
    print('Convert svg to pdf with inkscape')
    with Pool() as p:
        outcode = p.map(svgtopdf, [f'{bdir}/tmp/{svgf}' for svgf in output_svg_names])

    #join all pdf
    res = os.popen(pdfjoincmd+' %s -o %s'%(' '.join(['"'+bdir+'/tmp/%s.pdf"'%sname for sname in output_svg_names]), name_out))
    output = res.read()

    res.close()
    msg = "Saved to %s"%name_out
    os.system('rm -rf %s'%(bdir+'/tmp/slide_*'))

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

    # The global svg glyphs need also to be added to the html5 page
    # TODO: Optimize to export only glyphs used by this slide        
    glyphs_svg = '<defs id="glyphs_store">'
    glyphs_svg += '\n'.join([Store.get_glyph(g)['svg'] for g in Store._glyphs])
    glyphs_svg += '</defs>'

    for islide in range(len(Store)):
        print("Export slide %i"%islide)

        slide = Store.get_slide(f"slide_{islide+1}")
        
        # Render the slide
        slide.render(add_html_svgalt=True)        

        # Get the svgdefs
        globals_id_svg_defs = []
        tmp_svgdefs, tmp_id = export_svgdefs(slide.modules, globals_id_svg_defs, add_html_svgalt=True)
        
        svgdef = f'<defs>{tmp_svgdefs}</defs>'
            
        for layer in range(slide.num_layers + 1):
            print('write layer %i'%layer)
            # save the list of rendered svg to a new dict as a string
            tmp = '\n'.join((slide.svgheader, 
                             glyphs_svg, 
                             svgdef))

            # Join all the svg contents (old .decode('utf-8', errors='replace') for py2)
            if layer in slide.layers_content:
                tmp += f"\n<g>{slide.layers_content[layer]['svg']}</g>\n"
            else:
                tmp += '' #empty slide (when no svg are defined on slides)

            # Add the svgfooter
            tmp += slide.svgfooter

            with io.open(dir_name+'slide_%i-%i.svg'%(islide, layer), 'w', encoding='utf8') as f:
                f.write(tmp)                

    return "saved to "+dir_name


def html5_export():
    """
    Export all slides and all layers as an html file
    """

    # Read style (use python3 string Template)
    with open(Store._beampy_dir.joinpath('statics', 'beampy.css'), 'r') as f:
        css = Template(f.read())

    # Read jquery
    with open(Store._beampy_dir.joinpath('statics', 'jquery.js'),'r') as f:
        jquery = f.read()

    # read html header
    with open(Store._beampy_dir.joinpath('statics','header_V2.html'),'r') as f:
        html_header = Template(f.read())

    # read html footer
    with open(Store._beampy_dir.joinpath('statics', 'footer_V2.html'), 'r') as f:
        footer = Template(f.read())

    # read beampyjs
    with open(Store._beampy_dir.joinpath('statics', 'beampy.js'), 'r') as f:
        beampyjs = f.read()

    # Fill the template
    document = Store.get_layout()
    htmltheme = document._theme['document']['html']
    css = css.substitute(width = document._width,
                        height = document._height,
                        background_color = htmltheme['background_color'])

    # Add jquery and css to html header
    output = html_header.substitute(jquery = jquery,
                                    css = css)

    # Loop over slides in the document
    # If we directly want to charge the content in pure html
    tmpout = {}
    tmpscript = {}
    html_modules = ''
    # Add glyphs TODO: make an optimizer to remove unusued one comming from
    # cache
    glyphs_store = ('<svg id="glyph_store"><defs>'
                    '{glyphs}'
                    '</defs></svg>')
    glyphs_store = glyphs_store.format(glyphs=''.join([Store.get_glyph(g)['svg'] for g in Store._glyphs]))

    global_store = glyphs_store + '<svg><defs>'
    global_store_id = []
    for islide in range(len(Store)):

        tnow = time.time()

        slide_id = "slide_%i" % (islide)
        tmpout[slide_id] = {}
        slide = Store.get_slide("slide_%i" % (islide+1))

        # Render the slide
        slide.render()

        # Add a small peace of svg that will be used to get the data from the global store
        tmpout[slide_id]['svg'] = [] # Init the store for the differents layers
        #tmpout[slide_id]['layers_nums'] = max(slide.svglayers)
        tmpout[slide_id]['layers_nums'] = slide.num_layers
        tmpout[slide_id]['svg_header'] = slide.svgheader
        tmpout[slide_id]['svg_footer'] = slide.svgfooter

        # save the list of rendered svg to a new dict as a string that is loaded globally in the html
        # tmp = ''.join(slide.svgout).decode('utf-8', errors='replace')
        # OLD .decode('utf-8', errors='replace') after join for py2
        # modulessvgdefs = ''.join(slide.svgdefout)

        # global_store += "<svg><defs>" + modulessvgdefs
        tmp_svgdef, tmp_id = export_svgdefs(slide.modules, global_store_id)
        global_store_id += [tmp_id]
        global_store += tmp_svgdef

        for layer in range(slide.num_layers+1):
            print('write layer %i'%layer)
            # Export svg defs to the global store
            if layer in slide.layers_content:
                # OLD .decode('utf-8', errors='replace') for py2
                svg_layer_content = slide.layers_content[layer]['svg']
                html_layer_content = slide.layers_content[layer]['html']
                if html_layer_content != '':
                    html_modules += ''.join([f'<div id="html_store_slide_{islide}-{layer}"',
                                             'style="position:absolute;top:0px;left:0px;',
                                             'visibility:hidden;width:100%;height:100%;">',
                                             html_layer_content,
                                             '</div>'])
            else:
                svg_layer_content = '' #create an empty content (usefull when only html are present in one slide)

            global_store += f"<g id='slide_{islide}-{layer}'>{svg_layer_content}</g>"

            # Create an svg use for the given layer
            tmpout[slide_id]['svg'] += [f'<use xlink:href="#slide_{islide}-{layer}"/>']


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

        print("Done in %0.3f seconds"%(time.time()-tnow))

    global_store += '</defs></svg>'

        
    # Create a json file of all slides output (refs to store)
    jsonfile = StringIO()
    json.dump(tmpout, jsonfile, indent=None)
    jsonfile.seek(0)

    # Add the svg content
    output += global_store
    
    # Add html_modules to output
    output += html_modules
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
            
    output += footer.substitute(beampy=beampyjs)

    return output


def format_beampy_js(beampyjs: dict) -> str:
    """ 
    Format the javascripts defined in beampy slide to
    a javascript format that could be called when a 
    slide is loaded in html. 

    To do so, we use the following convention:
    - javascripts functions are encapsulated in
      a functions that is called when the slide is
      loaded in html

      scripts_slide[slide_id][function_name] = function(){
          js code
      }

    For Bokeh 
    Parameters:
    -----------

    - beampyjs, dict:
        The dictionnary with slide_id as key and javascript string as value.
        beampyjs = {"slide_0": "alert(1)", "slide_1": "alert('cool from js')"}
    """

    print('TODO!!!')


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



def svgtopdf(filename: str, dpi=300):
    """
    Convert a file from svg to pdf using inkscape
    """

    # External tools cmd
    document = Store.get_layout()
    inkscapecmd = document._external_cmd['inkscape']

    svgcmd = inkscapecmd+(f" --export-filename='{filename}.pdf'"
                          f" --export-dpi={dpi} {filename}.svg")
    
    # TODO: use subprocess.Popen for finer stdout and manage error codes
    res = os.popen(svgcmd)
    retcode = res.close()

    return retcode