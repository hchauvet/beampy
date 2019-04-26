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
from subprocess import check_call, check_output
import tempfile
import time
import hashlib  # To create uniq id for elements

import logging
_log = logging.getLogger(__name__)

# Lib to check the source code
import inspect
# Create REGEX pattern
find_svg_tags = re.compile('id="(.*)"')
# Regex to remove tab new line
remove_tabnewline = re.compile('\s+')

def unit_operation(value, to=0):
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


def convert_unit(value, ppi=72):
    """
    Function to convert size given in some unit to pixels, following the
    https://www.w3.org/TR/2008/REC-CSS2-20080411/syndata.html#length-units

    Parameters:
    -----------

    value, str or int:
        The given size followed by it's unit. Fixed units are (in, cm,
        mm, pt, pc). Relative units are (em, ex, %)

    ppi, int, optional:
        The number of pixel per inch (Latex use 72)
    """

    value = str(value)

    # px to px
    if 'px' in value:
        value = '%0.1f' % (float(value.replace('px', '')))

    # mm to cm
    if 'mm' in value:
        value = "%fcm" % (float(value.replace('mm',''))*10**-1)
        
    # cm to inch
    if "cm" in value:
        value = "%fin" % (float(value.replace('cm', ''))*(1/2.54))

    # pc to inch
    if 'pc' in value:
        value = '%fin' % (float(value.replace('pc','')*12))
                             
    # pt to inch
    if "pt" in value:
        value = "%fin" % (float(value.replace('pt', ''))*(1/72.0))

    # inch to px
    if "in" in value:
        # 1 inch = 72px
        out = float(value.replace('in', ''))*ppi
    else:
        out = float(value)

    return out


def pre_cache_svg_image(svg_frames):
    """
        Function to extract raster image from svg to define them only
        once on the slide.
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


def make_global_svg_defs_new_but_buggy(svg_soup):
    """
        Function to change svg refs and id to a global counter 
        to avoid miss-called elements in slides

        Input -> svg_soup: beautifulsoup object of the svg
    """

    
    # Test if it exist a svg_id global counter
    if 'svg_id' not in document._global_counter:
        document._global_counter['svg_id'] = 0  # init the counter

    # Get all id from defined object in <defs>
    for defs in svg_soup.find_all('defs'):
        tags_to_replace = find_svg_tags.findall(str(defs))


        base_name = "beampy"
        for cpt, tag in enumerate(tags_to_replace):
            #print(tag)
            #print({'xlink:href': '#%s'%tag})
            #Some use of this defs 
            new_tag = "%s_%i"%(base_name, document._global_counter['svg_id'])
            for elem in svg_soup.find_all(attrs={'xlink:href': '#%s'%tag}):
                elem['xlink:href'] = "#%s"%new_tag
    
            #Inside defs get the good one to change
            for elem in svg_soup.find_all(attrs={'id': tag}):
                elem['id'] = new_tag

            document._global_counter['svg_id'] += 1

    #print('Svg refs changed in %0.4fs'%(time.time() - tps))
    
    return svg_soup


def make_global_svg_defs(svg_soup):
    """
        Function to use global counter for id in svg defs and use

        svg_soup a BeautifulSoup object of the svg file
    """

    # Test if it exist a svg_id global counter
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
    #print('Svg refs changed in %0.4fs'%(time.time() - tps))
    
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
    t = time.time()
    #svgout = scour.scourString(svgfile_in, opts).encode("UTF-8")
    svgout = scour.scourString(svgfile_in, opts)
    print('optimize svg run in %f'%(time.time()-t))
    #print('done')

    return svgout

def latex2svg(latexstring, write_tmpsvg=False):
    """
        Command to render latex -> dvi -> svg

    Parameters
    ==========

    write_tmpsvg: true or false optional,
        Write the svg produced by dvisvgm to a file (if True)
        otherwise the output is read from stdout
    """

    _log.debug('Run latex2svg function')
    _log.debug(latexstring)
    
    dvisvgmcmd = document._external_cmd['dvisvgm']

    #Write the document to a tmp file
    tmpfile, tmpnam = tempfile.mkstemp(prefix='beampytmp')
    #print tmpnam
    tmppath = tmpnam.replace(os.path.basename(tmpnam), '')
    #print tmppath
    with open( tmpnam + '.tex', 'w' ) as f:
        f.write( latexstring )

    #Run Latex
    #t = time.time()
    tex = os.popen( "cd "+tmppath+" && latex -interaction=nonstopmode "+tmpnam+".tex" )
    #print('latex run in %f'%(time.time()-t))
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
    if 'error' in output or '!' in output:
        print('Latex compilation error')
        print(output)
        sys.exit(1)
        
    else:
        #dvisvgm to convert dvi to svg [old -e option not compatible with linkmark]
        if write_tmpsvg:
            _log.debug('Write dvisvgm output as an svg file')
            res = os.popen( dvisvgmcmd+' -n -a --linkmark=none -o '+tmpnam+'.svg --verbosity=0 '+tmpnam+'.dvi' )
            resp = res.read()
            res.close()
            
            with open(tmpnam+'.svg') as svgf:
                outsvg = svgf.read()
        else:
            cmd = dvisvgmcmd+' -n -s -a --linkmark=none -v0 '+tmpnam+'.dvi'
            outsvg = check_output(cmd, shell=True).decode('utf8')

        #Remove temp files
        for f in glob.glob(tmpnam+'*'):
            os.remove(f)

        outsvg = clean_ghostscript_warnings(outsvg)
        
        _log.debug(outsvg)
        _log.debug(type(outsvg))
    
        return outsvg


def clean_ghostscript_warnings(rawsvg):
    """
    Function to remove warning that appears in stdout

    The begining of the file is something like:

    *** WARNING - you have selected SAFER, indicating you want Ghostscript
               to execute in a safer environment, but at the same time
               have selected WRITESYSTEMDICT. Unless you use this option with
               care and specifically, remember to execute code like:
                      "systemdict readonly pop"
               it is possible that malicious <?xml version='1.0'?>
    <svg [...]/>
    """

    
    if isinstance(rawsvg, list):
        svg_lines = rawsvg
    else:
        svg_lines = rawsvg.splitlines()
        
    start_svg = 0
    for i, line in enumerate(svg_lines):
        if line.startswith('<svg') or line.startswith('<?xml'):
            start_svg = i
            break

    if isinstance(rawsvg, list):
        good_svg = svg_lines[start_svg:]
    else:
        good_svg = '\n'.join(svg_lines[start_svg:])

    if start_svg > 2:
        _log.debug('SVG have been cleaned from GS warnings, here is the original:')
        _log.debug(rawsvg)
        
    return good_svg


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


def gcs():
    """
        Fonction get current slide of the doc
    """

    return document._curentslide

def set_curentslide(slide_id):
    """
    Set the curent slide to the given slide_id
    """

    document._curentslide = slide_id

def set_lastslide():
    '''
    Set the curent slide as the last slide added in the presentation
    '''

    last_slide_id = 'slide_%i' % (document._global_counter['slide'])
    document._curentslide = last_slide_id


def gce(doc=document):
    """
        Function to get the current element number
    """

    return doc._global_counter['element']


def pdf2svg(pdf_input_file, svg_output_file):
    '''
    Runs pdf2svg in shell:
    pdf2svg pdf_input_file svg_output_file

    '''

    return check_call([document._external_cmd['pdf2svg'],
                       pdf_input_file, svg_output_file])


def convert_pdf_to_svg(pdf_input_file, temp_directory='local'):
    '''
    Open pdf_input_file, convert to svg using pdf2svg.
    '''

    local_directory, filename_pdf = os.path.split(pdf_input_file)
    filename = os.path.splitext(filename_pdf)[0]

    if temp_directory == 'local':
        temp_directory = local_directory
    if len(temp_directory) > 0:
        svg_output_file = temp_directory + '/' + filename + '.svg'
    else:
        svg_output_file = filename + '.svg'

    try:
        pdf2svg(pdf_input_file, svg_output_file)

        with open(svg_output_file, 'r') as f:
            svg_figure = f.read()

        check_call(['rm', svg_output_file])

        return svg_figure

    except ValueError:
        return None


def load_args_from_theme(function_name, args):
    """
        Function to set args of a given element
    """

    for key in args:
        if args[key] == "" or args[key] is None:
            try:
                args[key] = document._theme[function_name][key]
            except KeyError:
                print("[Beampy] No theme propertie for %s in %s" % (key, element_id))


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

    if "#" in color:
        textin = r'{\color[HTML]{%s} %s }' % (color.replace('#', '').upper(),
                                              textin)
    else:
        textin = r'{\color{%s} %s }' % (color, textin)

    return textin


def dict_deep_update(original, update):

    """
    Recursively update a dict.
    Subdict's won't be overwritten but also updated.
    from http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression/44512#44512
    """

    for key, value in original.items():
        if not key in update:
            update[key] = value
        elif isinstance(value, dict):
            dict_deep_update( value, update[key] )

    return update



def create_element_id(bpmod, use_args=True, use_name=True,
                      use_content=True, add_slide=True, slide_position=True):
    """
        create a unique id for the beampy_module using bpmod.content
        and bpmod.args.keys() and bpmod.name
    """
    ct_to_hash = ''

    if add_slide:
        ct_to_hash += bpmod.slide_id

    if use_args and bpmod.args is not None:
        ct_to_hash += ''.join(['%s:%s' % (k, v) for k, v in bpmod.args.items()])

    if use_name and bpmod.name is not None:
        ct_to_hash += bpmod.name

    if use_content and bpmod.content is not None:
        ct_to_hash += str(bpmod.content)
            
    if slide_position:
        ct_to_hash += str(len(document._slides[bpmod.slide_id].element_keys))

    outid = None
    if ct_to_hash != '':
        # print(ct_to_hash)
        try:
            outid = hashlib.md5( ct_to_hash ).hexdigest()
        except:
            outid = hashlib.md5( ct_to_hash.encode('utf8') ).hexdigest()

        if outid in document._slides[bpmod.slide_id].element_keys:
            print("Id for this element already exist!")
            sys.exit(0)
            outid = None

        #print(outid)

    return outid


# TODO: Improve this function
def get_command_line(func_name):
    """
    Function to print the line of the command in the source code file
    frame,filename,nline,function_name,lines,index = inspect.stack()[-1]
    """

    frame, filename, nline, function_name, lines, index = inspect.stack()[-1]
    # print(nline, func_name)
    if not isinstance(func_name, str):
        # func_name = func_name.func_name
        func_name = func_name.__name__

    # print(frame,filename,nline,function_name,lines,index)
    start = None
    src = document._source_code.source(stop=nline).split('\n')
    # print(src)
    for cpt, line in enumerate(src[::-1]):
        if func_name+'(' in line:
            # print(line)
            start = (nline) - (cpt + 1)
            break

    # print start
    if start is not None:
        stop = nline-1
        source = document._source_code.source(start+1, nline).replace('\n', '')
    else:
        start = 0
        stop = 0
        source = func_name

    # Remove tab and space from source
    source = remove_tabnewline.sub(' ', source)
    
    return (start, nline-1, source)


def guess_file_type(file_name, file_type=None):
    """
    Guess the type of a file name
    """

    file_extensions = {
        'svg': ['svg'],
        'pdf': ['pdf'],
        'png': ['png'],
        'jpeg': ['jpg', 'jpeg'],
        'gif': ['gif']
        }
    
    if file_type is None:
        try:
            ext = file_name.lower().split('.')[-1]
            
            for file_type in file_extensions:
                if ext in file_extensions[file_type]:
                    break
        except TypeError:
            print('Unknown file type for file name: ' + file_name + '.' )

    return file_type


# Function to render texts in document
def render_texts(elements_to_render=None, extra_packages=None):
    r"""
    Function to merge all text in the document to run latex only once
    This function build the .tex file and then call two external programs
    .tex -> latex -> .dvi -> dvisvgm -> svgfile

    Parameters:
    -----------

    elements_to_render, list of beampy_module (optional):
        List of beampy_module object to render (the default is None,
        which render all text module in all slides).

    extra_packages, list of string (optional):
        Give a list of extra latex packages to use in the latex
        template. Latex packages should be given as follow:
        [r'\usepackage{utf8x}{inputenc}']
    """

    if elements_to_render is None:
        elements_to_render = []

    if extra_packages is None:
        extra_packages = []
        
    print('Render texts of slides with latex')
    latex_header = r"""
    \documentclass[crop=true, multi=true]{standalone}
    \usepackage[utf8x]{inputenc}
    \usepackage{fix-cm}
    \usepackage[hypertex]{hyperref}
    \usepackage[svgnames]{xcolor}
    \renewcommand{\familydefault}{\sfdefault}
    \usepackage{varwidth}
    \usepackage{amsmath}
    \usepackage{amsfonts}
    \usepackage{amssymb}
    %s
    \begin{document}
    """ % ('\n'.join(extra_packages + document._latex_packages))
    latex_pages = []
    latex_footer = r"\end{document}"

    # logging.debug(latex_header)
    #Loop over slide
    t = time.time()
    cpt_page = 1
    elements_pages = []


    if elements_to_render == []:
        for sid in document._slides:
            #Loop over content in the slide
            for cid in document._slides[sid].element_keys:
                e = document._slides[sid].contents[cid]
                #Check if it's a text element, is it cached?, render it to latex syntax
                if e.type == 'text' and e.usetex and not e.rendered:
                    elements_to_render += [e]

                    
    for e in elements_to_render:
        if e.cache and document._cache is not None:
            _log.debug('Render_texts test cache for element %s(id=%s) on slide: %s' % (e.name, e.id, e.slide_id))
            ct_cache = document._cache.is_cached(e.slide_id, e)
            if ct_cache is False:
                # Run the pre_rendering
                e.pre_render()

                try:
                    latex_pages += [e.latex_text]
                    elements_pages += [{"element": e, "page": cpt_page}]
                    cpt_page += 1
                except Exception as e:
                    print(e)
        else:
            
            e.pre_render()

            try:
                latex_pages += [e.latex_text]
                elements_pages += [{"element": e, "page": cpt_page}]
                cpt_page += 1
            except Exception as e:
                print(e)

    _log.debug(latex_pages)
    if len(latex_pages) > 0:
        # Write the file to latex

        tmpfile, tmpname = tempfile.mkstemp(prefix='beampytmp')
        tmppath = tmpname.replace(os.path.basename(tmpname), '')

        with open( tmpname + '.tex','w') as f:
            f.write(latex_header)
            f.write('\n \\newpage \n'.join(latex_pages))
            f.write(latex_footer)

        print('Latex file writen in %f'%(time.time()-t))

        #Run Latex using subprocess
        #t = time.time()
        cmd = "cd "+tmppath+" && latex -interaction=nonstopmode --halt-on-error "+tmpname+".tex"
        _log.debug(cmd)
        
        tex = os.popen(cmd)
        #print('Latex run in %f'%(time.time()-t))
        tex_outputs = tex.read()
        _log.debug(tex_outputs)
        
        if 'error' in tex_outputs or '!' in tex_outputs:
            print(tex_outputs)
            print('Latex compilation error')
            sys.exit(1)
            
        tex.close()

        #Upload svg to each elements
        dvisvgmcmd = document._external_cmd['dvisvgm']

        t = time.time()
        cmd = dvisvgmcmd+' -n -s -p1- --linkmark=none -v0 '+tmpname+'.dvi'
        allsvgs = check_output(cmd, shell=True).decode('utf8')
        allsvgs = allsvgs.splitlines()

        # Check if their is warning emitted by dvisvgm inside the svgfile
        allsvgs = clean_ghostscript_warnings(allsvgs)
        
        #To split the data get the first line which define the <? xml ....?> command
        schema = allsvgs[0]
        
        #Join all svg lines and split them each time you find the schema
        svg_list = ''.join(allsvgs[1:]).split(schema)

        #Process all pages to svg
        for i, ep in enumerate(elements_pages):
            #Loop over content in the slide
            ep['element'].svgtext = schema + svg_list[i]
            
        print('DVI -> SVG in %f'%(time.time()-t))
        #Remove temp files
        for f in glob.glob(tmpname+'*'):
            os.remove(f)

            
# How do we split inputs paragraphs (all type of python strings)
PYTHON_COMMENT_REGEX = re.compile('"{3}?|"|\'{3}?|\'', re.MULTILINE)


def small_comment_parser(src):
    """
    Find comments inside a python source code.
    return a list of parsed comments.

    Parameters
    ----------
    
    src : str
        The source code to parse.x
    """

    # print(src)
    cur_marker_pos = 0
    cur_marker_type = ''
    marker_open = False
    text_parts = []
    for part in PYTHON_COMMENT_REGEX.finditer(src):
        start, stop = part.start(), part.end()
        # Init
        if cur_marker_pos == 0:
            cur_marker_type = src[start:stop].strip()
            cur_marker_pos = stop
            marker_open = True
        else:
            if marker_open:
                if cur_marker_type == src[start:stop].strip():
                    # print("end of marker %s" % cur_marker_type)
                    # Store the text
                    # comments = cur_marker_type
                    comments = src[cur_marker_pos:stop-len(cur_marker_type)]
                    text_parts += [comments]

                    cur_marker_pos = stop
                    cur_marker_type = ''
                    marker_open = False

            else:
                cur_marker_pos = stop
                cur_marker_type = src[start:stop].strip()
                marker_open = True

    return text_parts
