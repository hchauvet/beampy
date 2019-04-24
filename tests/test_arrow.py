
import pytest
from beampy import *

test_name = 'test_arrow'

@pytest.fixture
def make_presentation():
    doc = document(cache=False)

    with slide():
        arrow(x=10, y=0.1, dx=780, dy=0, lw=6, color='Crimson')

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html' % test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf' % test_name)
