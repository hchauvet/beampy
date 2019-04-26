"""
Test all the exporter of Beampy
"""
import pytest
from beampy import *

test_name = 'test_exports'

@pytest.fixture
def make_one_slide():
    doc = document(cache=False, source_filename=__name__)

    with slide('A test slide'):
        rectangle(width=50, height=50)

    return doc


def test_matplotlib(make_one_slide):
    doc = make_one_slide
    display_matplotlib('slide_0')


def test_html(make_one_slide):
    doc = make_one_slide
    save('./html_out/%s.html' % test_name)


def test_pdf(make_one_slide):
    doc = make_one_slide
    save('./html_out/%s.pdf' % test_name)
