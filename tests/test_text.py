#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest
from beampy import *

import logging
logging.basicConfig(level=logging.DEBUG)

test_name = 'test_text'

@pytest.fixture
def make_presentation():
    
    doc = document(cache=True, source_filename=__name__)
    
    def my_funct():

        with text():
            """
            Test of text inside a statement in a function
            """

        
    with slide():
        maketitle(test_name.replace('_','\_'))

    with slide('Title: text with equation'):
        t4 = text(r"""Approximations:\\
        $$\dot{E} \approx \frac{dL/dt}{L_c}$$\\
        $$\frac{dC}{dt} \approx \frac{d\theta_{tip}/dt}{L_c}$$
        """, width = 500, align='center')

        t4.add_border()

    with slide('Test text with "with"'):
        with text(width=500, align='center'):
            """
            The new test for the text typing system.\\
            
            $$\frac{10}{4}$$

            I can now \textbf{write long text} easily in my source
            """

            "$$\frac{dC}{dt} \approx \frac{d\theta_{tip}/dt}{L_c}$$"

    with slide('Avec des accents léééé looo öoooo'):
        with text():
            """
            Test text inside the with statement.
            """

    with slide('Test with inside a function'):
        my_funct()


    return doc

def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

"""
def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
"""
