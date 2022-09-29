#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest
from beampy import *

test_name = 'test circle'

@pytest.fixture
def make_presentation():
    doc = document(cache=False)


    with slide('test circle'):

        c = circle()
        c1 = circle(r=100, margin=10, linewidth=3, edgecolor='blue')
        c2 = circle(center(c1.right), center(c1.top), width=c1.width/2, color='red')
        c3 = circle(5, 'center', width=0.5, color='none', linewidth=10)
        for cc in [c, c1, c2]:
            cc.show_box_model = True

    return doc


def test_svg():
    doc = document(cache=False)
    c = circle(10, 10)
    assert c.x.value == 10
    assert c.y.value == 10

def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
