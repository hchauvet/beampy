#!/usr/bin/env python3

"""
Functions to manipulate svg file in python.
Part of Beampy-Slideshow
"""
import tempfile
from bs4 import BeautifulSoup
from beampy.core.functions import convert_unit
from beampy.core.store import Store
import os
import re
import logging
_log = logging.getLogger(__name__)

try:
    from xxhash import xxh3_64 as hashfunction
except Exception:
    _log.debug('Beampy is faster using xxhash librabry, pip install xxhash')
    from hashlib import md5 as hashfunction


def get_viewbox(svg: object) -> list:
    """Find the viewbox in the svg tag and return a list with x, y, width,
    height.

    Parameter:
    ----------

    - svg, a BeautifulSoup object,
        An instance of BeautifulSoup parser.

    """

    assert isinstance(svg, BeautifulSoup), "svg input should be a BeautifulSoup instance"

    out = None

    svgsoup = svg.find('svg')

    if svgsoup is not None:
        vbox = svgsoup.get('viewBox')
        if vbox is not None:
            out = [float(i) for i in vbox.split()]

    return out


def get_baseline(svg: object) -> float:
    """Bad way to get baseline of a text, just look at the first use of dvisvgm
    output.
    TODO: find a better way, maybe a dvi decompiler (dviasm)
    https://github.com/aminophen/dviasm
    https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/dviread.py
    """

    baseline = 0
    yuse = [float(u['y']) for u in svg.find_all('use', {'y': True})]
    if len(yuse) > 0:
        baseline = min(yuse)

    return baseline


def get_svg_size(svg: object) -> list:
    """Return the size of a given svg.

    Parameter:
    ----------

    - svg, a BeautifulSoup object:
        And instance of BeautifulSoup parser, containing the svg to get size.

    Output:
    -------

    list: [width, height] of the svg in pixels
    """

    assert isinstance(svg, BeautifulSoup), "svg input should be a BeautifulSoup instance"
    width = 0
    height = 0

    svgtag = svg.find('svg')
    svg_viewbox = get_viewbox(svg)

    # If their is a view box, we could use it to get the with/height of a svg
    if svg_viewbox is not None:
        width = svg_viewbox[2]
        height = svg_viewbox[3]
    else:
        # Try to find height and width tag
        width = svgtag.get("width")
        height = svgtag.get("height")

        if width is None or height is None:
            # The last solution is to use inkscape to get svg size (but this is
            # slow)
            with tempfile.NamedTemporaryFile(mode='w', prefix='beampytmp', suffix='.svg') as f:
                f.write(svg.prettify(formatter=None))

                # force to write file content to disk
                f.file.flush()

                # get svg size using inkscape
                width, height = inkscape_get_size(f.name)

    width = convert_unit(width)
    height = convert_unit(height)

    return width, height


def make_global_svg_defs(svg_soup: object) -> object:
    """
        Function to use global counter for id in svg defs and use

        svg_soup a BeautifulSoup object of the svg file
    """

    #str_svg to replace modified id in all the svg content
    # strsvg = svg_soup.decode('utf8')

    # OLD way only work on defs.... Find defs
    # svgdefs = svg_soup.find('defs')
    # New way find all id in the svg

    #Create seed by hashing the entire svg file
    try: 
        seed = hashfunction(svg_soup.encode('utf8')).hexdigest()[:5]
    except Exception as error: 
        seed = hashfunction(svg_soup.decode('utf8')).hexdigest()[:5]
    
    strsvg = svg_soup.decode('utf8')
        
    for tag in svg_soup.findAll(lambda x: x is not None and x.has_attr('id')):
        oldid = tag['id']
        newid = "S%s_%i"%(seed, Store.svg_id())
        strsvg = re.sub(oldid+'"', newid+'"', strsvg)

        if tag.name in ['clipPath','linearGradient']:
            strsvg = re.sub(f'(#{oldid})', f'#{newid}', strsvg)
                

        # print(oldid, newid)
        Store.update_svg_id()

    #Reparse the new svg
    soup = BeautifulSoup(strsvg, 'xml')
    #print('Svg refs changed in %0.4fs'%(time.time() - tps))

    return soup


def apply_style_to_all_images(svg_soup: object, style: str) -> object:
    """
    Apply the given style to all image tag in an svg
    """

    for imt in svg_soup.findAll('image'):
        # TODO: keep old style and merge it properly with the new one
        imt['style'] = style 

    return svg_soup

def export_svgdefs(modules: list, exported_id: list, svgaltdef=False) -> (str, list):
    """Export svgdef for each module in the list, if the module content_id is not in
    the exported_list. If the module is a group run export_svgdef to do the recursivity

    Returns
    -------

    list of svgdef and list of updated exported_id
    """

    svgdef = []
    for m in modules:
        # Special case of group which exports id with layer
        if m.type == 'group':
            tmp_id, tmp_svgdefs = m.svgdef
            for i in range(len(tmp_id)):
                if tmp_id[i] not in exported_id and tmp_svgdefs[i] is not None:
                    svgdef += [tmp_svgdefs[i]]
                    exported_id += [tmp_id[i]]

            tmp_svgdef, tmp_id = export_svgdefs(m.modules, exported_id, svgaltdef)
            svgdef += [tmp_svgdef]
            exported_id += [tmp_id]
        else:
            if m.content_id not in exported_id:
                tmp = m.export_svgdefs(svgaltdef)
                if tmp is not None:
                    svgdef += [tmp]

                exported_id += [m.content_id]


    svgdef = '\n'.join(svgdef)

    return svgdef, exported_id


def inkscape_get_size(svgfile: str) -> list:
    """Get the width, height of an svgfile
    """

    # __APPS__ defined by beampy.__init__.py
    inkscapecmd = Store.get_exec('inkscape')
    cmd = f'{inkscapecmd} --actions="query-width;query-height;" {svgfile}'
    req = os.popen(cmd)
    res = req.readlines()

    width = float(res[0].strip())
    height = float(res[1].strip())

    req.close()

    return width, height


def make_unique_glyphs(svgsoup: object) -> object:
    """Process the svg (parsed with BeautifulSoup) to ensure unique id for
    glyphs path.
    Glyphs are stored in the Store with a unique id based on their
    vectorized path hash.

    Parameter:
    ----------

    Return:
    -------

    The modified svgsoup object, with updated glyph ids in svg "use" and
    "defs".
    """

    # Find the defs tag of the svg
    defs_soup = svgsoup.find('defs')
    if defs_soup is not None:
        for path in defs_soup.find_all('path'):
            old_id = path['id']
            uid = hashfunction(path['d'].encode('utf8')).hexdigest()

            if Store.is_glyph(uid):
                # Update the new_path_id from the Store
                new_path_id = Store.get_glyph(uid)['id']
            else:
                # Create a new id for this new glyph in Store
                new_path_id = f'g_{len(Store._glyphs)}'
                # Replace the id in the svg path tag
                path['id'] = new_path_id
                nglyph = {'id': new_path_id,
                            'dvisvgm_id': old_id,
                            'svg': str(path),
                            'uid': uid}

                Store.add_glyph(nglyph)

            # in defs, they could be "use" tag that reuse a path and define
            # a new id to it with different arguments.
            for usedef in defs_soup.find_all('use', {'xlink:href': f'#{old_id}'}):
                old_use_id = usedef['id']
                use_uid = hashfunction(str(usedef).encode('utf8')).hexdigest()

                if Store.is_glyph(use_uid):
                    # Get the new id from Store
                    new_use_id = Store.get_glyph(use_uid)['id']
                else:
                    # Create the new use id
                    new_use_id = f'g_{len(Store._glyphs)}'
                    # Update reference for before storing the svg tag in Store
                    usedef['id'] = new_use_id
                    usedef['xlink:href'] = f'#{new_path_id}'
                    nuse = {'id': new_use_id,
                            'uid': use_uid,
                            'dvisvgm_id': old_use_id,
                            'svg': str(usedef)}

                    Store.add_glyph(nuse)

                # Find all use (not in defs tag) that refer to this use tag
                # id and update their link to the new id
                for use in svgsoup.find_all('use', {'xlink:href': f'#{old_use_id}'}):
                    use['xlink:href'] = f'#{new_use_id}'

            # find all use that reference this path
            # and replace the reference by the new uniqueid
            for use in svgsoup.find_all('use', {'xlink:href': f'#{old_id}'}):
                use['xlink:href'] = f'#{new_path_id}'

    return svgsoup
