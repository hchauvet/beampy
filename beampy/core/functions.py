# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:45:51 2015

@author: hugo
"""
from pathlib import Path
from beampy.core.store import Store
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


def horizontal_centering(object_width, xinit=0, page_width=None):
    """
        Function to center and object on the page_width

        xinit: is the initial position

        final position:
            xinit + available_space/2
    """

    if page_width == None:
        page_width = Store.get_layout()._width

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


def latex2svg(latexstring, cached_preamble=None, write_tmpsvg=False):
    """
        Command to render latex -> dvi -> svg

    Parameters
    ==========

    - cached_preamble: Path object or None,
        Path to the header file for latex (i.e. caching of preamble compiled
        with latex --ini "&latex my_preamble"). This file will be passed to
        latex --fmt.
    - write_tmpsvg: true or false optional,
            Write the svg produced by dvisvgm to a file (if True)
            otherwise the output is read from stdout
    """

    _log.debug('Run latex2svg function')
    _log.debug(latexstring)

    dvisvgmcmd = Store.get_layout()._external_cmd['dvisvgm']

    # Create variable to store name of the created temp file
    tmpname = None
    tex_outputs = None

    # Get the temporary dir location
    tmppath = tempfile.gettempdir()

    with tempfile.NamedTemporaryFile(mode='w', prefix='beampytmp', suffix='.tex') as f:
        # Get the name of the file
        tmpname, tmpextension = os.path.splitext(f.name)

        # Write latex commands to the file
        f.write( latexstring )

        # Flush file content, so that it is available for latex command
        f.file.flush()

        #Run Latex
        #t = time.time()
        if cached_preamble is not None:
            cmd = f'cd {tmppath} && latex -interaction=nonstopmode -fmt="{str(cached_preamble)}" {f.name}'
        else:
            cmd = f'cd {tmppath} && latex -interaction=nonstopmode {f.name}'

        tex = os.popen(cmd)
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
        tex_outputs = tex.read()
        tex.close() # close the os.popen

    #Run dvi2svgm
    # TODO: better check for error should read test if a dvifile is present!
    if tex_outputs is None or 'error' in tex_outputs:
        print('Latex compilation error')
        print('------ TEX OUTPUTS ------')
        print(tex_outputs)
        print('------ TEX INPUT ------')
        if cached_preamble is not None:
            print(open(str(cached_preamble).replace('.fmt', '.tex'), 'r').read())
        print(latexstring)

        #Remove temp files
        for f in glob.glob(tmpname+'*'):
            os.remove(f)

        # Stop beampy compilation
        sys.exit(1)

    else:
        #dvisvgm to convert dvi to svg [old -e option not compatible with linkmark]
        if write_tmpsvg:
            _log.debug('Write dvisvgm output as an svg file')
            cmd = dvisvgmcmd
            cmd += ' -n -a --linkmark=none -o {filename}.svg --verbosity=0 {filename}.dvi'
            cmd = cmd.format(filename=tmpname)
            res = os.popen(cmd)
            resp = res.read()
            res.close()

            with open(tmpname + '.svg') as svgf:
                outsvg = svgf.read()
        else:
            cmd = dvisvgmcmd+' -n -s -a --linkmark=none -v0 {filename}.dvi'
            cmd = cmd.format(filename=tmpname)
            outsvg = check_output(cmd, shell=True).decode('utf8')

        #Remove temp files
        for f in glob.glob(tmpname+'*'):
            os.remove(f)

        outsvg = clean_ghostscript_warnings(outsvg)

        _log.debug(outsvg)
        _log.debug(type(outsvg))

        return outsvg


def process_latex_header(texfile: object, texcommands: str):
    """
    Render the header of latex using the INI mode.

    Parameters:
    -----------
    - texfile: a Path object from pathlib,
        The file name to write the preamble
    - texcommands: str,
        The latex command to add to the file
    """

    texfile.write_text(texcommands)
    tex = os.popen("cd "+str(texfile.parent)+rf' && latex -ini -interaction=nonstopmode "&latex {texfile.name}\dump"')
    tex_outputs = tex.read()
    tex.close() # close the os.popen

    # Check that compilation is ok
    if tex_outputs is None or 'error' in tex_outputs or '!' in tex_outputs:
        print('Latex compilation error')
        print(tex_outputs)

        # Stop beampy compilation
        sys.exit(1)

    # Check that a .fmt file is created by latex

    if not (texfile.parent / texfile.name.replace('.tex', '.fmt')).is_file():
        print('No %s created for the header, something wront' % texfile.name.replace('.tex', '.fmt'))
        sys.exit(1)


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


def gcs():
    """
        Fonction get current slide of the doc
    """

    return Store.get_current_slide_id()

def set_curentslide(slide_id):
    """
    Set the curent slide to the given slide_id
    """
    raise NotImplemented
    # Store.set_curentslide(slide_id)

def set_lastslide():
    '''
    Set the curent slide as the last slide added in the presentation
    '''
    raise NotImplemented
    # last_slide_id = 'slide_%i' % (document._global_counter['slide'])
    # document._curentslide = last_slide_id


def gce():
    """
        Function to get the current element number
    """

    # TODO: return doc._global_counter['element']
    raise NotImplemented


def epstopdf(eps_input_file, pdf_output_file):
    '''
    Runs pdf2svg in shell:
    pdf2svg pdf_input_file svg_output_file

    '''

    return check_call([Store.get_layout()._external_cmd['epstopdf'],
                       eps_input_file, pdf_output_file])

def pdf2svg(pdf_input_file, svg_output_file):
    '''
    Runs pdf2svg in shell:
    pdf2svg pdf_input_file svg_output_file

    '''

    return check_call([Store.get_layout()._external_cmd['pdf2svg'],
                       pdf_input_file, svg_output_file])


def convert_eps_to_svg(eps_input_file, temp_directory='local'):
    '''
    Open pdf_input_file, convert to svg using pdf2svg.
    '''

    local_directory, filename_pdf = os.path.split(eps_input_file)
    filename = os.path.splitext(filename_pdf)[0]

    if temp_directory == 'local':
        temp_directory = local_directory
    if len(temp_directory) > 0:
        svg_output_file = temp_directory + '/' + filename + '.svg'
        pdf_output_file = temp_directory + '/' + filename + '.pdf'
    else:
        svg_output_file = filename + '.svg'
        pdf_output_file = filename + '.pdf'

    try:
        epstopdf(eps_input_file, pdf_output_file)
        pdf2svg(pdf_output_file,svg_output_file)

        with open(svg_output_file, 'r') as f:
            svg_figure = f.read()

        check_call(['rm', svg_output_file])
        check_call(['rm', pdf_output_file])

        return svg_figure

    except ValueError:
        return None

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
                args[key] = Store.theme(function_name)[key]
            except KeyError:
                print("[Beampy] No theme propertie for %s in %s" % (key, element_id))


def check_function_args( function, arg_values_dict, lenient = False ):
    """
        Function to check input function args.

        Functions args are defined in the default_theme.py
        or if a theme is added the new value is taken rather than the default one
    """

    function_name = function.__name__
    default_dict = Store.theme(function_name)
    outdict = {}

    for key, value in arg_values_dict.items():
        #Check if this arguments exist for this function

        if key in default_dict:
            outdict[key] = value

        else:
            if not lenient :
                print("Error the key %s is not defined for %s module"%(key, function_name))
                print_function_args( function_name )
                sys.exit(1)


    #Check if their is ommited arguments that need to be loaded by default
    for key, value in default_dict.items():
        if key not in outdict:
            outdict[key] = value

    return outdict

def print_function_args(function_name):
    #Pretty print of function arguments with default values
    print("Allowed arguments for %s"%(function_name))
    for key, value in Store.theme(function_name).items():
        print("%s: [%s] %s"%(key, str(value), type(value)))

def inherit_function_args(function_name, args_dict):
    #Allow to add args defined for an other function to the args_dict

    for key, value in Store.theme(function_name).items():
        if key not in args_dict:
            args_dict[key] = value

    return args_dict


def color_text(textin, color):
    '''
    Adds Latex color to a string.
    '''

    if color.startswith("#"):
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


def create_element_id(bpmod, use_args=True, use_name=True, use_content=True,
                      add_slide=True, slide_position=True):
    """
        create a unique id for the beampy_module using bpmod.content
        and bpmod.args.keys() and bpmod.name
    """
    ct_to_hash = ''

    if add_slide:
        ct_to_hash += bpmod.slide_id

    if use_args and bpmod.args is not None:
        ct_to_hash += ''.join(['%s:%s' % (k, v) for k, v in bpmod.args.items() if k not in ['x', 'y']])

    if use_name and bpmod.name is not None:
        ct_to_hash += bpmod.name

    if use_content and bpmod.content is not None:
        ct_to_hash += str(bpmod.content)

    if slide_position:
        ct_to_hash += str(len(Store.get_slide(bpmod.slide_id).element_keys))

    outid = None
    if ct_to_hash != '':
        # print(ct_to_hash)
        outid = hashlib.md5( ct_to_hash.encode('utf8') ).hexdigest()

        if bpmod.slide_id is not None and Store.get_slide(bpmod.slide_id).is_module(outid):
            _log.debug("Id for %s already exist!" % str(bpmod.name))
            sys.exit(0)
            # outid = None

        #print(outid)

    return outid


# TODO: Improve this function
def get_command_line(func_name):
    """
    Function to print the line of the command in the source code file
    frame,filename,nline,function_name,lines,index = inspect.stack()[-1]
    """

    sourcemanager = Store.get_layout()._source_code

    frame, filename, nline, function_name, lines, index = inspect.stack()[-1]
    
    # On IPython nline gives a weird thing
    if sourcemanager._IPY_ != False:
        nline = len(sourcemanager._IPYsource.split('\n'))

    if not isinstance(func_name, str):
        # func_name = func_name.func_name
        func_name = func_name.__name__

    # print(frame,filename,nline,function_name,lines,index)
    start = None
    src = sourcemanager.source(stop=nline).split('\n')

    for cpt, line in enumerate(src[::-1]):
        if func_name+'(' in line:
            # print(line)
            start = (nline) - (cpt + 1)
            break

    # print start
    if start is not None:
        stop = nline-1
        if not sourcemanager._IPY_:
            source = sourcemanager.source(start+1, nline).replace('\n', '')
        else:
            stop = stop - 1
            source = sourcemanager.source(start, stop).replace('\n', '')
            start = start + 1
    else:
        start = 0
        stop = 0
        source = func_name

    # Remove tab and space from source
    source = remove_tabnewline.sub(' ', source)

    return (start, nline-1, source)


def guess_file_type(file_name: str, file_type=None) -> str:
    """
    Guess the type of a file name
    """

    file_name = Path(file_name)

    file_extensions = {
        'svg': ['svg'],
        'pdf': ['pdf'],
        'png': ['png'],
        'jpeg': ['jpg', 'jpeg'],
        'gif': ['gif'],
        'eps': ['eps']
        }

    if file_type is None:
        ext = file_name.suffix.replace('.', '')

        found = False
        for file_type in file_extensions:
            if ext in file_extensions[file_type]:
                found = True
                break
        if not found:
            raise TypeError('Unknown file type '+ext+' for file name: ' + file_name + '.' )

    return file_type


PYTHON_XMLFIND_REGEX = re.compile(r'<\?xml[^>]+>')
def get_xml_tag(rawsvg):
    """
    Function to find the xml tag in a file this tag could be
    <?xml version='1.0'?>
    or
    <?xml version='1.0' encoding='UTF-8'?>
    or other (depends on dvisvgm version

    """


    if isinstance(rawsvg, list):
        svg_lines = rawsvg
    else:
        svg_lines = rawsvg.splitlines()

    xmltag = None
    for l in svg_lines:
        search_re = PYTHON_XMLFIND_REGEX.search(l)
        if search_re:
            xmltag = search_re.group(0)
            break

    return xmltag

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


def find_strings_in_with(source_code: str, module_name: str) -> list:
    """
    parse python source file (or part of source code) to extract string inside a
    "with" statement. Extract any string enclosed either by \"\"\" or by '''.

    Parameters:
    -----------

    source_code: string,
        the source code to be parsed.

    module_name: string,
        the name of the beampy module for which the with statement is used.

    outputs:
    --------

    list of texts found inside the with statement
    """

    # First try to find indentation level of the source 
    pattern1 = r'(?:with.*text.*:.*[\n\r])(\s+)'
    indent_level=len(re.findall(pattern1, source_code, re.MULTILINE)[0])

    # Parse the indented block in the source file to keep only valid indented regions
    # TODO: this implementation is dirty!!!
    start_text = False
    keep_text = []
    cur_tripple_quotes = None
    for line in source_code.splitlines():
        # trick to test blank line len(line.strip())>0
        if start_text and line and len(line.strip())>0:
            if line.startswith(' '*indent_level) or cur_tripple_quotes is not None:
                keep_text += [line.strip()]
            
                # Need to handle case when tripple quote are used 
                # as they could remove indentation inside
                if '"""' in line:
                    if cur_tripple_quotes != '"""':
                        cur_tripple_quotes = '"""'
                    else:
                        cur_tripple_quotes = None
                    
                if "'''" in line:
                    if cur_tripple_quotes != "'''":
                        cur_tripple_quotes = "'''"
                    else: 
                        cur_tripple_quotes = None
            
            else:
                if cur_tripple_quotes is None:
                    break

        
        if not start_text and 'text' in line:
            start_text = True
        
    
    indented_part = '\n'.join(keep_text)

    patterns_2 = [r'(?:^\"{3}[\r\n]?)([\s\S]*?)(?:\"{3})',
                  r'(?:^\'{3}[\r\n]?)([\s\S]*?)(?:\'{3})',
                  r'(?<=\")([^\"]+)(?=\")',
                  r'(?<=\')([^\"]+)(?=\')']

    all_groups = re.findall('|'.join(patterns_2), 
                            indented_part, 
                            re.MULTILINE)
    
    # export text_parts finded with regexp
    text_parts = []
    for groups in all_groups:
        for g in groups:
            if g != '':
                text_parts += [g.strip()]

    return text_parts
