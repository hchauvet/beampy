import pytest
from beampy import *

import logging
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def make_slide_grid():
    
    doc = document(cache=True, source_filename = __name__, optimize=False)
    
    with slide('Test grid'):
        g = grid(25, 25, color='gray')
        g2 = grid(100, 100, color='crimson')

        g.first()
        g2.above(g)

    return doc


def test_html(make_slide_grid):
    doc = make_slide_grid
    save('./html_out/%s.html' % __name__)


def test_pdf(make_slide_grid):
    doc = make_slide_grid
    save('./pdf_out/%s.pdf' % __name__)
