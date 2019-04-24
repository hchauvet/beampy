#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest
from beampy import *

test_name = 'test_animatesvg'

@pytest.fixture
def make_presentation():
    doc = document(cache=False, optimize=False)

    with slide():
        animatesvg("../examples/svg_anims/*.svg", width="500", x='center', y='center')
        animatesvg("../examples/svg_anims/*.svg", width="100", x='0.1', y='0.1')

    with slide('Animate with layers'):
        with group()[:]:
            animatesvg("../examples/svg_anims/*.svg", width="500")
            with group()[1]:
                animatesvg("../examples/svg_anims/*.svg", width="100")

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html' % test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf' % test_name)
