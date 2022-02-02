#!/usr/bin/env python3

"""
Functions to manipulate svg file in python.
Part of Beampy-Slideshow
"""
import tempfile
from bs4 import BeautifulSoup
from beampy.core.functions import inkscape_get_size, convert_unit


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
