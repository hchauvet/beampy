import pytest
from beampy import *


@pytest.fixture
def make_presentation():
    doc = document(source_filename = __name__)

    with slide('Test grid'):
        grid(25, 25, color='gray')
        grid(100, 100, color='crimson')


    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html' % __name__)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf' % __name__)
