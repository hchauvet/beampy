# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:48:01 2015

@author: hugo
"""

#from beampy.global_variables import _document, _width, _height, _global_counter
from beampy.renders import *
from beampy.commands import document
from beampy.functions import *
from cache import cache_slides
import beampy
import json
import cStringIO as stringio
import os
import time

#Get the beampy folder
curdir = os.path.dirname(__file__) + '/'

#External tools cmd
inkscapecmd = document._external_cmd['inkscape']
pdfjoincmd = document._external_cmd['pdfjoin']

def save(output_file=None, format=None):
    """
        Function to render the document to html

    """

    texp = time.time()
    bname = os.path.basename(output_file)
    bdir = output_file.replace(bname,'')


    if 'html' in output_file:
        document._output_format = 'html5'

        #check if we use cache
        if document._cache == True:
            cache_file = bdir+'.cache_'+bname.split('.')[0]+'_html5.pklz'
            print("[Beampy] Chache file to %s"%cache_file)
            document._cache = cache_slides(cache_file)

        output = html5_export()

    elif output_file != None and format == "svg":
        document._output_format = 'svg'

        #check if we use cache
        if document._cache == True:
            cache_file = bdir+'.cache_'+bname.split('.')[0]+'_svg.pklz'
            print("[Beampy] Chache file to %s"%cache_file)
            document._cache = cache_slides(cache_file)

        output = svg_export(output_file)
        output_file = None

    elif 'pdf' in output_file:
        document._output_format = 'pdf'

        #check if we use cache
        if document._cache == True:
            cache_file = bdir+'.cache_'+bname.split('.')[0]+'_pdf.pklz'
            print("[Beampy] Chache file to %s"%cache_file)
            document._cache = cache_slides(cache_file)

        output = pdf_export(output_file)
        output_file = None

    if output_file != None:
        with open(output_file,'w') as f:
            f.write( output.encode('utf8') )

    else:
        print(output)

    #write cache file
    if document._cache != None:
        document._cache.write_cache()

    print("[Beampy] Done in %0.1f seconds"%(time.time()-texp))

def pdf_export(name_out):
    #use inkscape to translate svg to pdf
    svgcmd = inkscapecmd+" --without-gui  --file='%s' --export-pdf='%s'"
    bdir = os.path.dirname(name_out)

    print('Render svg slides')
    aa = svg_export(bdir+'/tmp')

    print('Convert svg to pdf with inkscape')
    for islide in xrange(document._global_counter['slide']+1):
        print('slide %i'%islide)
        #check if content type need to be changed
        check_content_type_change( document._contents["slide_%i"%islide] )
        
        #Use inkscape to render svg to pdf
        res = os.popen(svgcmd%(bdir+'/tmp/slide_%i.svg'%islide, bdir+'/tmp/slide_%i.pdf'%islide) )
        res.close()

    #join all pdf
    res = os.popen(pdfjoincmd+' %s -o %s'%(' '.join(['"'+bdir+'/tmp/slide_%i.pdf"'%i for i in xrange(document._global_counter['slide']+1)]), name_out))
    output = res.read()

    res.close()
    msg = "Saved to %s"%name_out
    os.system('rm -rf %s'%(bdir+'/tmp'))

    return msg

def svg_export(dir_name):
    #Export evry slides in svg inside a given folder

    try:
        os.mkdir(dir_name)
    except:
        pass

    if dir_name[-1] != '/':
        dir_name += '/'

    for islide in xrange(document._global_counter['slide']+1):
        print("Export slide %i"%islide)
        
        #check if content type need to be changed
        check_content_type_change( document._contents["slide_%i"%islide] )
        tmp = render_slide( document._contents["slide_%i"%islide] )
        
        with open(dir_name+'slide_%i.svg'%islide, 'w') as f:
            f.write(tmp)
            
    return "saved to "+dir_name

def html5_export():

    with open(curdir+'statics/jquery.js','r') as f:
        jquery = f.read()

    with open(curdir+'statics/header_V2.html','r') as f:
        output = f.read()%jquery

    #Loop over slides in the document
    #If we directly want to charge the content in pure html
    tmpout = {}
    tmpscript = {}
    for islide in xrange(document._global_counter['slide']+1):
        #print("[Beampy] export slide %i"%islide)
        tnow = time.time()

        tmpout["slide_%i"%islide] = {}
        tmp = render_slide( document._contents["slide_%i"%islide] )
        #save the rendered svg to a new dict
        tmpout["slide_%i"%islide]['svg'] = document._contents["slide_%i"%islide]['svg_output']

        if 'svg_animations' in document._contents["slide_%i"%islide]:
            tmpout["slide_%i"%islide]['animations'] = document._contents["slide_%i"%islide]['svg_animations']

        if 'script' in document._contents["slide_%i"%islide]:
            tmpscript['slide_%i'%islide] = document._contents["slide_%i"%islide]['script']

        if 'html_output' in document._contents['slide_%i'%islide]:
            tmpout["slide_%i"%islide]['htmlcontent'] = document._contents["slide_%i"%islide]['html_output']

        print("[Slide %i] done in %0.1f seconds"%(islide+1, time.time()-tnow))

    #Create a json file of all slides output
    jsonfile = stringio.StringIO()
    json.dump(tmpout,jsonfile, indent=None)

    jsonfile.seek(0) 

    output += '<script> var slides = eval( ( %s ) );</script>'%jsonfile.read()

    #Javascript output
    #format: scripts_slide[slide_i]['function_name'] = function() { ... }
    if tmpscript != {}:
        bokeh_required = False
        output += '\n <script> scripts_slide = {}; //dict with scrip function for slides \n'
        for slide in tmpscript:
            output += '\nscripts_slide["%s"] = {};\n scripts_slide["%s"]%s; \n'%(slide, slide, tmpscript[slide])
            if 'bokeh' in tmpscript[slide].lower():
                bokeh_required = True

        output += '</script>\n'

        if bokeh_required:
            #Need to download bokeh
            with open(curdir+'statics/bokeh/bokeh.min.js','r') as f:
                bokjs = f.read()

            with open(curdir+'statics/bokeh/bokeh.min.css','r') as f:
                bokcss = f.read()

            output += """
            <style>%s</style>
            <script>%s</script>
            """%(bokcss, bokjs)

    output += """
    <!-- Default Style -->
    <style>
      * { margin: 0; padding: 0; -moz-box-sizing: border-box; -webkit-box-sizing: border-box; box-sizing: border-box; }
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


      html { background-color: #000; height: 100%; width: 100%;}
             
      body.loaded { display: block;}

    </style>
    
    """
    
    with open(curdir+'statics/footer_V2.html','r') as f:
        output += f.read()

    return output


def check_content_type_change(slide):
    """
        Function to change type of some slide contents (like for video html -> svg ) when render is changer from html5 to another
    """
    
    for ct in slide['contents']:
        if 'type_nohtml' in ct:
            print('done')
            ct['type'] = ct['type_nohtml'] 
                
                
