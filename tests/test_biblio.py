#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest
from beampy import *

#import logging
#logging.basicConfig(level=logging.DEBUG)

test_name = 'test_biblio'

@pytest.fixture
def make_presentation():
    
    doc = document(cache=True, source_filename=__name__)
    
    bib = bibliography('../examples/biblio.bib')

    slide('Quantum mechanics')

    text('Any serious consideration of a physical theory must take into account the distinction     between the objective reality, which is independent of any theory, and the physical concepts with which the theory operates.', y = '+1cm')

    cite('Einstein 1935', y = '+1cm')
    bib.cite('einstein1935can', y = '+1cm' )
    bib.cite('einstein1935can', y = '+1cm', initials = True )
    b1 = bib.cite('einstein1935can', y = '+1cm', max_author = 1, journal = True )
    bib.cite(['einstein1935can']*3, y = b1.bottom+'1cm', max_author = 1)

    return doc

def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)


def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)

