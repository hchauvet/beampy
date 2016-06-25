# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:45:51 2015

@author: hugo
"""

from beampy.document import document
from bs4 import BeautifulSoup
import re
from beampy.scour import scour
import glob
import os
import sys
from subprocess import check_call
import tempfile
import time
import hashlib #To create uniq id for elements (from content and args_dict)

#Lib to check the source code
import linecache
import inspect

def unit_operation( value, to=0 ):
    """
        realise operation on values and return the result in px

        expl: value = 3px+4cm -> the sum

              value = +5cm, to=450 -> 450px+5cm
    """

    if '+' in value:
        vsplited = value.split('+')
        for v in vsplited :
            to += float(convert_unit(v))

    elif '-' in value:
        vsplited = value.split('-')
        for v in vsplited:
            to -= float(convert_unit(v))

    return "%0.1f"%to

def convert_unit( value ):
    """
        Function to convert unit to px (default unit in svg)
    """

    value = str(value)
    #Convert metric to cm
    if 'mm' in value:
        value = "%fcm"%(float(value.replace('mm',''))*10**-1)


    #if it's pt remove the pt tag and convert to float
    if 'px' in value:
        out = "%0.1f"%(float(value.replace('px','')))

    #cm to pt
    elif "cm" in value:
        #old cm to pt: 28.3464567
        out = "%0.1f"%(float(value.replace('cm','')) * 37.79527559055)

    #px to pt
    elif "pt" in value:
        #old: 0.75 px to pt
        out = "%0.1f"%( float(value.replace('pt','')) * 1.333333 )

    else:
        out = "%0.1f"%(float(value))

    return out



def pre_cache_svg_image( svg_frames ):
    """
        Function to extract raster image from svg to define them only once on the slide
    """

    all_images = []
    out_svg_frames = []
    findimage = re.compile(r'<image.*?>')
    for frame in svg_frames:
        svgimages = findimage.findall(frame)
        all_images += svgimages

        #add the cleaned frame to the ouput
        out_svg_frames += [findimage.sub('\n',frame)]

    return out_svg_frames, all_images

def make_global_svg_defs(svg_soup):
    """
        Function to use global counter for id in svg defs and use

        svg_soup a BeautifulSoup object of the svg file
    """


    #Test if it exist a svg_id global counter
    if 'svg_id' not in document._global_counter:
        document._global_counter['svg_id'] = 0  #init the counter

    #str_svg to replace modified id in all the svg content
    strsvg = str(svg_soup)

    #Find defs
    svgdefs = svg_soup.find('defs')
    #change_tags = ['path','clipPath','symbol','image', 'mask']
    #change_tags = ['clipPath','mask','symbol','image']
    #print svgdefs

    #Create unique_id_ with time
    text_id =  ("%0.4f"%time.time()).split('.')[-1]
    if svgdefs != None:
        for tag in svgdefs.findAll(lambda x: x!=None and x.has_attr('id')):
            oldid = tag['id']
            newid = "%s_%i"%(text_id,document._global_counter['svg_id'])
            strsvg = re.sub(oldid+'"', newid+'"', strsvg)

            if tag.name in ['clipPath','linearGradient']:
                strsvg = re.sub('(#'+oldid+')', '#'+newid, strsvg)

            document._global_counter['svg_id'] += 1

    #Reparse the new svg
    soup = BeautifulSoup(strsvg, 'xml')

    return soup


def horizontal_centering(object_width, xinit=0, page_width=None):
    """
        Function to center and object on the page_width

        xinit: is the initial position

        final position:
            xinit + available_space/2
    """

    if page_width == None:
        page_width = document._width

    if page_width > object_width:
        available_space = (page_width - object_width)
        #print available_space, object_width
        xnew = xinit + (available_space/2)
    else:
        xnew = xinit

    return xnew


def optimize_svg(svgfile_in):
    """
        Use python scour to optimise svg gain roughtly 50% in size

        options (default):
        {'strip_ids': False,
        'shorten_ids': False,
        'simple_colors': True,
        'strip_comments': False,
        'remove_metadata': False,
        'outfilename': None,
        'group_create': False,
        'protect_ids_noninkscape': False,
        'indent_type': 'space',
        'keep_editor_data': False,
        'shorten_ids_prefix': '',
        'keep_defs': False,
        'renderer_workaround': True,
        'style_to_xml': True,
        'protect_ids_prefix': None,
        'enable_viewboxing': False,
        'digits': 5,
        'embed_rasters': True,
        'infilename': 'none',
        'strip_xml_prolog': False,
        'group_collapse': True,
        'quiet': False,
        'protect_ids_list': None}
    """

    #get default option
    opts = scour.generateDefaultOptions()
    options = opts.__dict__

    #custom options for beampy
    #TODO: add this option to a configuration file
    options['indent_type'] = None
    options['strip_comments'] = True
    #options['group_create'] = True #create group with identical element defs

    #run scour
    #print('optimize svg...')
    svgout = scour.scourString(svgfile_in, opts).encode("UTF-8")
    #print('done')

    return svgout

def latex2svg(latexstring):
    """
        Command to render latex -> dvi -> svg
    """

    dvisvgmcmd = document._external_cmd['dvisvgm']

    #Write the document to a tmp file
    tmpfile, tmpnam = tempfile.mkstemp(prefix='beampytmp')
    #print tmpnam
    tmppath = tmpnam.replace(os.path.basename(tmpnam), '')
    #print tmppath
    with open( tmpnam + '.tex', 'w' ) as f:
        f.write( latexstring )

    #Run Latex
    tex = os.popen( "cd "+tmppath+" && latex -interaction=nonstopmode "+tmpnam+".tex" )
    #print tex.read() #To print tex output
    """
    This is a test to get the base line from latex output
    \\newlength\\x
    \\newlength\\y
    \\x=1em
    \\y=1ex
    \\showthe\\x
    \\showthe\\y
    """
    #find_size = re.compile(r'> \d.*?.pt.')
    #tex_em, tex_ex = find_size.findall(tex.read())
    #Convert latex pt to cm (1pt = 28.4cm)
    #tex_em = "%0.5fcm"%(float(tex_em[2:-3]) * 1/28.4)
    #convert to pixel
    output = tex.read()
    tex.close()
    #Run dvi2svgm
    if 'error' in output:
        print output
    else:
        #dvisvgm to convert dvi to svg [old -e option not compatible with linkmark]
        res = os.popen( dvisvgmcmd+' -n -s --linkmark=none -v0 '+tmpnam+'.dvi' )
        testsvg = res.read()
        res.close()

        #Remove temp files
        for f in glob.glob(tmpnam+'*'):
            os.remove(f)

    #tmpfile.close()

    return testsvg

def getsvgwidth( svgfile ):
    """
        get svgfile width using inkscape
    """

    inkscapecmd = document._external_cmd['inkscape']

    cmd = inkscapecmd + ' -z -W %s'%svgfile
    req = os.popen(cmd)
    res = req.read()
    req.close()

    return res

def getsvgheight( svgfile ):
    """
        get svgfile height using inkscape
    """

    inkscapecmd = document._external_cmd['inkscape']

    cmd = inkscapecmd + ' -z -H %s'%svgfile
    req = os.popen(cmd)
    res = req.read()
    req.close()

    return res


def gcs(doc=document):
    """
        Fonction get current slide of the doc
    """

    return "slide_%i"%(doc._global_counter['slide'])


def gce(doc=document):
    """
        Function to get the current element number
    """

    return doc._global_counter['element']

def pdf2svg( pdf_input_file, svg_output_file  ) :

	'''

		Runs pdf2svg in shell:
		pdf2svg pdf_input_file svg_output_file

	'''

	return check_call( [ document._external_cmd['pdf2svg'], pdf_input_file, svg_output_file  ] )


def convert_pdf_to_svg( pdf_input_file, temp_directory = 'local' ):

	'''

		Open pdf_input_file, convert to svg using pdf2svg.

	'''

	local_directory, filename_pdf = os.path.split( pdf_input_file )
	filename = os.path.splitext( filename_pdf)[0]

	if temp_directory == 'local' :
		temp_directory = local_directory

	if len(temp_directory) > 0 :
		svg_output_file = temp_directory + '/' + filename + '.svg'
	else :
		svg_output_file = filename + '.svg'

	try :

		pdf2svg( pdf_input_file, svg_output_file )

		with open( svg_output_file, 'r' ) as f:
			svg_figure = f.read()

		check_call( [ 'rm', svg_output_file ] )

		return svg_figure

	except ValueError :

		return None



def load_args_from_theme(function_name, args):
    """
        Function to set args of a given element
    """

    for key in args:
        if args[key] == "" or args[key] == None:
            try:
                args[key] = document._theme[function_name][key]
            except:
                print("[Beampy] No theme propertie for %s in %s"%(key,element_id))

def check_function_args(function, arg_values_dict):
    """
        Function to check input function args.

        Functions args are defined in the default_theme.py
        or if a theme is added the new value is taken rather than the default one
    """

    function_name = function.__name__
    default_dict = document._theme[function_name]
    outdict = {}
    for key, value in arg_values_dict.items():
        #Check if this arguments exist for this function
        if key in default_dict:
            outdict[key] = value
        else:
            print("Error the key %s is not defined for %s module"%(key, function_name))
            print_function_args(function_name)
            sys.exit(1)

    #Check if their is ommited arguments that need to be loaded by default
    for key, value in default_dict.items():
        if key not in outdict:
            outdict[key] = value

    return outdict

def print_function_args(function_name):
    #Pretty print of function arguments with default values
    print("Allowed arguments for %s"%(function_name))
    for key, value in document._theme[function_name].items():
        print("%s: [%s] %s"%(key, str(value), type(value)))

def inherit_function_args(function_name, args_dict):
    #Allow to add args defined for an other function to the args_dict

    for key, value in document._theme[function_name].items():
        if key not in args_dict:
            args_dict[key] = value

    return args_dict

def color_text( textin, color ):

	'''
		Adds Latex color to a string.
	'''

	if "#" in    color:
		textin = r'{\color[HTML]{%s} %s }'%( color.replace('#','').upper(), textin)

	else:
		textin =r'{\color{%s} %s }'%( color, textin)

	return textin


def dict_deep_update( original, update ):

    """
    Recursively update a dict.
    Subdict's won't be overwritten but also updated.
    from http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression/44512#44512
    """

    for key, value in original.iteritems():
        if not key in update:
            update[key] = value
        elif isinstance(value, dict):
            dict_deep_update( value, update[key] )

    return update

def add_to_slide( content, x, y, width, height ):
    """
        Function to add a given content to the current slide
    """
    from beampy.geometry import positionner

    elem_id = create_element_id( content )
    #print(elem_id)
    document._contents[gcs()]['element_keys'] += [ elem_id ]
    document._contents[gcs()]['contents'][elem_id] =  content
    content['positionner'] = positionner(x,y ,width, height, elem_id)

    #return the positionner for relative placement
    return content['positionner']


def create_element_id( bpmod, use_args=True, use_name=True, use_content=True, add_slide=True, slide_position=True ):
    """
        create a unique id for the beampy_module using bpmod.content and bpmod.args.keys() and bpmod.name
    """
    ct_to_hash = ''

    if add_slide:
        ct_to_hash += gcs()

    if use_args and bpmod.args != None:
        ct_to_hash += ''.join(['%s:%s'%(k,v) for k,v in bpmod.args.items()])

    if use_name and bpmod.name != None:
        ct_to_hash += bpmod.name

    if use_content and bpmod.content != None:
        ct_to_hash += str(bpmod.content)

    if slide_position:
        ct_to_hash += str(len(document._slides[gcs()].element_keys))

    outid = None
    if ct_to_hash != '':
        outid = hashlib.md5( ct_to_hash ).hexdigest()

        if outid in document._slides[gcs()].element_keys:
            print("Id for this element already exist!")
            sys.exit(0)
            outid = None
        #print outid

    return outid



def get_command_line(func_name):
    #Function to print the line of the command in the source code file
    frame,filename,nline,function_name,lines,index = inspect.stack()[-1]
    if type(func_name) != type(''):
        func_name = func_name.func_name

    #print(frame,filename,nline,function_name,lines,index)
    start = None
    for cpt, line in enumerate(document._source_code[:nline][::-1]):
        if func_name+'(' in line:
            start = (nline) - (cpt + 1)
            break

    #print start
    if start != None:
        #print('line (%i->%i):\n'%(start,nline-1) +''.join(document._source_code[start:nline]))
        stop = nline-1
        source = ''.join(document._source_code[start:nline])
    else:
        start = 0
        stop = 0
        source = 'Not found\n'
        #print(frame,filename,nline,function_name,lines,index)

    return (start, nline-1, source)

def guess_file_type( file_name, file_type = None ) :
    
    file_extensions = {
        'svg':['svg'],
        'pdf':['pdf'],
        'png':['png'],
        'jpeg':['jpg','jpeg']
        }
    
    if file_type == None:
        
        try :
            
            ext = file_name.lower().split('.')[-1]
            
            for file_type in file_extensions:
                
                if ext in file_extensions[file_type] :
                    
                    break
                
            
        except :
            
            print('Unknown file type for file name: ' + file_name + '.' )

    return file_type
