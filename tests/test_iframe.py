# coding: utf-8

import pytest
from beampy import *

test_name = 'iframe'

@pytest.fixture
def make_iframes():

    doc = document()

    with slide():
        ifr = iframe('https://www.openstreetmap.org/export/embed.html?bbox=152.84720420837402%2C-27.152032753362846%2C152.9905414581299%2C-27.082665432390733&amp;layer=mapnik')
        print(ifr)
    return doc


def test_html(make_iframes):
    doc = make_iframes
    save('./html_out/test_%s.html' % test_name)
