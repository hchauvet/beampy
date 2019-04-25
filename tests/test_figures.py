# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Test of figure module
"""
import pytest
from beampy import *

test_name = 'test_figures'

@pytest.fixture
def make_presentation():
    import matplotlib
    matplotlib.use('agg')
    import pylab as p
    doc = document(cache=False)

    with slide("Matplotlib figure"):
        fig = p.figure()
        x = p.linspace(0,2*p.pi)

        p.plot(x, p.sin(x), '--')

        figure(fig)


    with slide("Mpl animation"):

        anim_figs = []
        for i in range(20):
            fig = p.figure()   
            x =  p.linspace(0,2*p.pi)
            p.plot(x, p.sin(x+i))
            p.plot(x, p.sin(x+i+p.pi))
            p.close(fig) 
            anim_figs += [ fig ]


        animatesvg( anim_figs )

    with slide("Test gif"):
        figure('./test.gif', width=300)

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
