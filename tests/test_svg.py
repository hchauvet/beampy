#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest
from beampy import *

test_name = 'test_svg'

@pytest.fixture
def make_presentation():
    doc = document(cache=False)


    with slide('Test rectangle size'):

        r1 = rectangle(width=200, height=200, x=5, y='center')
        r2 = rectangle(width=200, height=200, x=300, y='center',
                   color='yellow', opacity=0.3, linewidth=30)

        r1.add_border()
        r2.add_border()

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
