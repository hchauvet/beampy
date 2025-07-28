
import pytest
from beampy import *

test_name = 'test_arrow'

@pytest.fixture
def make_presentation():
    doc = document(cache=False)

    with slide():
        a1 = arrow(x=10, y=0.1, dx=780, dy=0, lw=6, color='Crimson')
        arrow(x=10, y=0.1, dx=780, dy=100)
        
        arrow(x=a1.right + 0, y=a1.y_center+0, dx=-50, dy=10, color='green')

    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html' % test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf' % test_name)
