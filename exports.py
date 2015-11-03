# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:48:01 2015

@author: hugo
"""

#from beampy.global_variables import _document, _width, _height, _global_counter
from beampy.renders import *
from beampy.commands import document
from beampy.functions import *
import beampy
import json
import cStringIO as stringio
import os

#Get the beampy folder
curdir = str(beampy).split('beampy')[1].split('from')[-1].strip().replace("'",'')+'beampy/'

def save(output_file=None, format=None):
    """
        Function to render the document to html
        
    """
    
    if 'html' in output_file:
        document._output_format = 'html5'
        output = html5_export()

    elif output_file != None and format == "svg":
        document.output_format = 'svg'
        output = svg_export(output_file)
        output_file = None
    
    elif 'pdf' in output_file:
        document._output_format = 'pdf'
        output = pdf_export(output_file) 
        output_file = None
        
    if output_file != None:
        with open(output_file,'w') as f:
            f.write( output.encode('utf8') )
            
    else:
        print(output)

def pdf_export(name_out):
    #use inkscape to translate svg to pdf
    svgcmd = "inkscape --without-gui  --file='%s' --export-pdf='%s'"
    bdir = os.path.dirname(name_out)
    
    print('Render svg slides')
    aa = svg_export(bdir+'/tmp')
    
    print('Convert svg to pdf with inkscape')
    for islide in xrange(document._global_counter['slide']+1):
        print('slide %i'%islide)
        res = os.popen(svgcmd%(bdir+'/tmp/slide_%i.svg'%islide, bdir+'/tmp/slide_%i.pdf'%islide) )
        res.close()
    
    #join all pdf
    res = os.popen('pdfjoin %s -o %s'%(' '.join(['"'+bdir+'/tmp/slide_%i.pdf"'%i for i in xrange(document._global_counter['slide']+1)]), name_out))
    output = res.read()
    
    res.close()
    msg = "Saved to %s"%name_out
    os.system('rm -rf %s'%(bdir+'/tmp'))
        
    return msg
    
def pdf_cairo_export(name_out):
    #Cairo bug very often to translate svg to pdf....
    import cairosvg
    bdir = os.path.dirname(name_out)
    
    try:
        os.mkdir(bdir+'/tmp')
    except:
        pass
    
    for islide in xrange(document._global_counter['slide']+1):
        print("Export slide %i"%islide)
        tmp = render_slide( document._contents["slide_%i"%islide] )    
        try:    
            cairosvg.svg2pdf(document._contents["slide_%i"%islide]['svg_output'], write_to = bdir+'/tmp/slide_%i.pdf'%islide)
        except:
            print("export failed")
        
    #join all pdf
    res = os.popen('pdfjoin %s*.pdf -o %s'%(bdir+'/tmp/',name_out))
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
        print("Export slide %i"%islide)
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
            
    #Create a json file of all slides output
    jsonfile = stringio.StringIO()
    json.dump(tmpout,jsonfile, indent=None)
    
    jsonfile.seek(0) #Go to the biginig of the file
#Test gzip: Not efficient 
#    if document._gzip:
#        #Do we need to compress slides with gzip
#        gziped =  base64.b64encode(zlib.compress(urllib.quote(jsonfile.read()), 9))
#        #Load jsmincompressor.js from statics
#        with open(curdir + 'statics/jsxcompressor.min.js', 'r') as fs:            
#            output += '<script type="text/javascript">%s</script>\n'%fs.read()
#            
#        output += """<script> 
#        var slides = eval( "(" + JXG.decompress( "%s" ) + ")" );
#        </script>"""%gziped

    
    
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
        
    with open(curdir+'statics/footer_V2.html','r') as f:
        output += f.read()

    return output
    
    
