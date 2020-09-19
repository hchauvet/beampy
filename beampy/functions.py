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

    return "%0.1f" % to


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
    strsvg = svg_soup.decode('utf8')

    #Find defs
    svgdefs = svg_soup.find('defs')
    #change_tags = ['path','clipPath','symbol','image', 'mask']
    #change_tags = ['clipPath','mask','symbol','image']
    #print(strsvg, svgdefs)

    #Create unique_id_ with time
    text_id =  ("%0.4f"%time.time()).split('.')[-1]
    if svgdefs is not None:
        for tag in svgdefs.findAll(lambda x: x is not None and x.has_attr('id')):
            oldid = tag['id']
            newid = "%s_%i"%(text_id, document._global_counter['svg_id'])
            strsvg = re.sub(oldid+'"', newid+'"', strsvg)

            if tag.name in ['clipPath','linearGradient']:
                strsvg = re.sub('(#'+oldid+')', '#'+newid, strsvg)

            # print(oldid, newid)
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


def latex2svg(latexstring,
              dvisvgmoptions=['-n', '-a', '--linkmark=none'],
              write_tmpsvg=False):
    """
    Render latex -> dvi -> svg

    Parameters
    ==========

    dvisvgmoptions: list of string optional,
        Give option to be passed to dvisvgm to convert dvi to svg.

    write_tmpsvg: true or false optional,
        Write the svg produced by dvisvgm to a file (if True)
        otherwise the output is read from stdout
    """

    _log.debug('Run latex2svg function')
    _log.debug(latexstring)

    dvisvgmcmd = document._external_cmd['dvisvgm']

    # Create variable to store name of the created temp file
    tmpname = None
    tex_outputs = None

    # Get the temporary dir location
    tmppath = tempfile.gettempdir()

    with tempfile.NamedTemporaryFile(mode='w', prefix='beampytmp', suffix='.tex') as f:
        # Get the name of the file
        tmpname, tmpextension = os.path.splitext(f.name)

        # Write latex commands to the file
        f.write(latexstring)

        # Flush file content, so that it is available for latex command
        f.file.flush()

        #Run Latex
        #t = time.time()
        cmd = "cd "+tmppath+" && latex -interaction=nonstopmode --halt-on-error "+f.name
        _log.debug(cmd)
        tex = os.popen(cmd)
        tex_outputs = tex.read()
        _log.debug(tex_outputs)
        tex.close() # close the os.popen

    #Run dvi2svgm
    if tex_outputs is None or 'error' in tex_outputs or '!' in tex_outputs:
        print('Latex compilation error')
        print(tex_outputs)
        #Remove temp files
        for f in glob.glob(tmpname+'*'):
            os.remove(f)

        # Stop beampy compilation
        sys.exit(1)

    else:
        #dvisvgm to convert dvi to svg [old -e option not compatible with linkmark]
        if write_tmpsvg:
            _log.debug('Write dvisvgm output as an svg file')
            cmd = dvisvgmcmd+' '
            cmd += ' '.join(dvisvgmoptions)
            cmd += ' -o {filename}.svg --verbosity=0 {filename}.dvi'
            cmd = cmd.format(filename=tmpname)
            res = os.popen(cmd)
            resp = res.read()
            res.close()

            with open(tmpname + '.svg') as svgf:
                outsvg = svgf.read()
        else:
            cmd = dvisvgmcmd+' '
            cmd += ' '.join(dvisvgmoptions)
            cmd += ' -s -v0 {filename}.dvi'
            cmd = cmd.format(filename=tmpname)
            outsvg = check_output(cmd, shell=True).decode('utf8', errors='replace')
            
        # Remove temp files
        for f in glob.glob(tmpname+'*'):
            os.remove(f)

        # Check if their is warning emitted by dvisvgm inside the svgfile
        outsvg = clean_ghostscript_warnings(outsvg)
        
        _log.debug(outsvg)

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


def getsvgwidth(svgfile):
    """
        get svgfile width using inkscape
    """

    inkscapecmd = document._external_cmd['inkscape']

    cmd = inkscapecmd + ' -z -W %s'%svgfile
    req = os.popen(cmd)
    res = req.read()
    req.close()

    return res


def getsvgheight(svgfile):
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


def check_function_args( function, arg_values_dict, lenient = False ):
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
    for key, value in document._theme[function_name].items():
        print("%s: [%s] %s"%(key, str(value), type(value)))


def inherit_function_args(function_name, args_dict):
    #Allow to add args defined for an other function to the args_dict

    for key, value in document._theme[function_name].items():
        if key not in args_dict:
            args_dict[key] = value

    return args_dict


def color_text(textin, color):

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
        if key not in update:
            update[key] = value
        elif isinstance(value, dict):
            dict_deep_update(value, update[key])

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
    \documentclass[crop=true, multi=varwidth]{standalone}
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
    latex_footer = r"\end{document}"

    cpt_page = 1
    elements_pages = []
    latex_pages = []
    elements_nofont = []
    
    if elements_to_render == []:
        for islide in range(len(document._slides)):
            # don't loop over document._slides keys directly as they will be ordered differentyl in py2 and py3
            sid = 'slide_%i' % (islide)
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
                    if e.nofont:
                        elements_nofont += [True]
                    else:
                        elements_nofont += [False]
                        
                    latex_pages += [e.latex_text]  
                    elements_pages += [{"element": e, "page": cpt_page}]
                    cpt_page += 1
                except Exception as e:
                    print(e)
        else:
            e.pre_render()
            try:
                if e.nofont:
                    elements_nofont += [True]
                else:
                    elements_nofont += [False]

                latex_pages += [e.latex_text]
                elements_pages += [{"element": e, "page": cpt_page}]
                cpt_page += 1
            except Exception as e:
                print(e)

    # Need to separate elements with font or nofont options
    for nofont in [True, False]:
        latexp = [p for i, p in enumerate(latex_pages) if elements_nofont[i] == nofont]
        if len(latexp) > 0:
            # Create the latex content
            latex_content = latex_header
            latex_content += '\n \\newpage \n'.join(latexp)
            latex_content += latex_footer

            if nofont:
                options = ['-n', '-a', '--linkmark=none', '-p1-']
            else:
                options = ['-a', '--font-format=woff2,ah',
                           '--no-style', '--no-merge', '--linkmark=none',
                           '-p1-']

            allsvgs = latex2svg(latex_content, dvisvgmoptions=options)
            allsvgs = allsvgs.splitlines()
            # print(nofont, len(latexp), allsvgs)

            if len(latexp) == 1:
                svg_list = [''.join(allsvgs)]
                schema = ''
            else:
                #To split the data get the xml syntax <? xml ....?>
                schema = get_xml_tag(allsvgs)
                _log.debug('Schema to cut svg %s' % (str(schema)))
                assert schema is not None

                #Join all svg lines and split them each time you find the schema
                svg_list = ''.join(allsvgs).split(schema)
                if svg_list[0] == '':
                    svg_list = svg_list[1:]

            tmpelems = [e for i, e in enumerate(elements_pages) if elements_nofont[i]==nofont]
            _log.debug('Size of svg %i and size of latex pages %i'%(len(svg_list), len(tmpelems)))
            assert len(svg_list) == len(tmpelems)

            # Process all pages to svg
            for i, ep in enumerate(tmpelems):
                # Loop over content in the slide
                ep['element'].svgtext = schema + svg_list[i]



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
        print(l)
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


def apply_to_all(elements=None, element_type=None, function=print):
    """Apply function to a given element in the elements list. If elements
    list is None (default) the function will be applied on all
    elements of all slides. When element_type is None (the default)
    the function will be applied on all type of elements, if an
    element_type is provided the function will only be applied to this
    element_type.

    Parameters
    ----------

    elements: list of tuple (slide_id, beampy modules id) or None,
       A list of elements (slide_id, module_id) on which the function
       will be applied. When sets to None (default) the elements will
       be set to all elements id for all slides of the presentation.

    element_type: str or None,
       The name of the element type on which to apply the function. If
       None (default) the function is applied on all type of element.

    function: callable,
       A function to apply on elements.
    """

    if elements is None:
        elements = []
        for islide in range(len(document._slides)):
            sid = 'slide_%i' % (islide)
            eids = document._slides[sid].element_keys
            elements += [(sid, eid) for eid in eids]

    for sid, eid in elements:
        e = document._slides[sid].contents[eid]
        if element_type is None or e.type == element_type:
            function(e)


def get_attr(attribute, elements=None, element_type=None, unique=False):
    """
    Retrieve all attribute for a given element_type in the elements
    list. If elements is None, the whole elements from the documents
    are analysed. If element_type is None the attribute is returned
    for all the elements list.

    Parameters:
    -----------

    attribute: str,
       The name of the attribute to retrieve.

    elements: list of tuple (slide_id, beampy modules id) or None,
       A list of elements (slide_id, module_id) on which to get the
       attribute. When sets to None (default) the elements will be
       set to all elements id for all slides of the presentation.

    element_type: str or None,
       The name of the element type on which to get the attribute. If
       None (default) the attribute is retrieved from all type of
       element.

    unique: Boolean,
       Return only attribute with different values (default False)
    """

    if elements is None:
        elements = []
        for islide in range(len(document._slides)):
            sid = 'slide_%i' % (islide)
            eids = document._slides[sid].element_keys
            elements += [(sid, eid) for eid in eids]

    out = []
    for sid, eid in elements:
        e = document._slides[sid].contents[eid]
        if element_type is None or e.type == element_type:
            if hasattr(e, attribute):
                tmp = getattr(e, attribute)
                if unique:
                    if tmp not in out:
                        if (isinstance(tmp, list)):
                            out += tmp
                        else:
                            out += [tmp]
                else:
                    if (isinstance(tmp, list)):
                        out += tmp
                    else:
                        out += [tmp]
            else:
                _log.error('The element %s has no attribute %s',
                           (e, attribute))

    return out


def force_rerender(element_type, elements=None):
    """
    Put rendered flag to false. This for re-rerender all elements.
    """

    def rerender(e):
        e.rendered = False

    apply_to_all(elements,
                 element_type=element_type,
                 function=rerender)

