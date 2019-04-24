#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pytest
from beampy import *

test_name = 'test_video'

@pytest.fixture
def make_presentation():
    doc = document(cache=False)

    with slide():
        maketitle(test_name.replace('_','\_'))

    with slide('Title: test video'):
        video('../examples/test.webm')

    with slide('Test video not embedded'):
        video('../examples/test.webm', embedded=False)

    with slide():
        video('../examples/test.webm')
        video('../examples/test.webm')[1]

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
