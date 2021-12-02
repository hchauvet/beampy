#!/usr/bin/env python3

"""
Functions to manipulate svg file in python.
Part of Beampy-Slideshow
"""
from bs4 import BeautifulSoup

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
