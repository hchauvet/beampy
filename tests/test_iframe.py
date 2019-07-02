# coding: utf-8

import pytest
from beampy import *

test_name = 'iframe'

@pytest.fixture
def make_iframes():

    doc = document()

    with slide():
        iframe('https://developer.mozilla.org/fr/docs/Web/SVG/Element/foreignObject')

    return doc


def test_html(make_iframes):
    doc = make_iframes
    save('./html_out/test_%s.html' % test_name)
