#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest

from beampy import *

test_name = 'test_bokeh'

@pytest.fixture
def make_presentation():
    import numpy as np
    from bokeh.plotting import figure as bokfig
    from bokeh.models import Legend, LinearAxis
    import os
    doc = document(cache=False, optimize=False)

    with slide():
        p = bokfig(sizing_mode='scale_both')
        p.circle([1,2], [3,4])
        figure(p)    

    with slide('A bokeh figure (the one in the documentation)'):

        p = bokfig(height=300, width=600)
        x = np.random.rand(100)
        y = np.random.rand(100)
        p.circle(x, y, legend="sin(x)")

        figure(p)


    with slide('Test s1'):
        p = bokfig(height=300, width=600)
        x = np.linspace(0, 4*np.pi, 30  )
        y = np.sin(x)
        p.circle(x, y, legend="sin(x)")

        text('test')[:]
        figure(p)[1]

    with slide():
        p = bokfig(height=600, width=800)
        x = np.linspace(0, 4*np.pi, 30  )
        y = np.sin(x)
        p.circle(x, y, legend="sin(x)", size=10)

        figure(p)

    with slide('Big font'):
        p = bokfig(height=500, width=750)

        x = np.linspace(0, 4*np.pi, 30  )
        y = np.sin(x)
        p.circle(x, y, legend="sin(x)", size=8)
        # configure visual properties on a plot's title attribute
        p.title.text = "Title With Options"
        p.title.text_color = "orange"
        p.title.text_font_size = "2.5vw"

        p.xaxis.axis_label = 'Time'
        p.yaxis.axis_label = 'Value'
        p.xaxis.axis_label_text_font_size = "1.5vw"
        p.xaxis.major_label_text_font_size = "1vw"
        p.yaxis.axis_label_text_font_size = "1.5vw"
        p.yaxis.major_label_text_font_size = "1vw"

        figure(p)
        """
        p = bokfig(height=300, width=600)
        x = np.linspace(0, 4*np.pi, 30  )
        y = np.sin(x)
        p.circle(x, y, legend="sin(x)", color='red')
        """
        #figure(p)

    with slide():
        N = 4000
        x = np.random.random(size=N) * 100
        y = np.random.random(size=N) * 100
        radii = np.random.random(size=N) * 1.5
        colors = [
            "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
        ]

        TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

        p = bokfig(tools=TOOLS, output_backend="webgl")

        p.scatter(x, y, radius=radii,
              fill_color=colors, fill_alpha=0.6,
              line_color=None)

        figure(p)

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

# TODO
"""
def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
"""
