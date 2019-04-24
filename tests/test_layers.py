#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest

from beampy import *
import os

import logging
logging.basicConfig(level=logging.DEBUG)

test_name = 'test_layers'

@pytest.fixture
def make_presentation():
    doc = document(cache=False, optimize=False, theme='ComplicatedBlue')


    with slide('Test s1'):

        t = text('test')[:-1]
        #v0 = video('../examples/test.webm', width=300)

        with group()[1:] as g1:
            v0 = video('../examples/test.webm', width=300)[2]
            text('toto')
            ss = text('tutu')[2]
            with group(width=300) as g2:
                t0=text('New sub group text', width=150, x=0, y=0)[3]
                text('Yeah Beampy Rocks!', width=150, y=t0.center+center(0), x=t0.right + 0.1)[4]

        g1.add_border()
        g2.add_border()

    with slide('Test s2'):
        text('The first text, printed over all layers')[:]
        text('The second text')[1]
        text('The text from 3 to the end')[2:]
        text('Only at the end')[3]

        it = itemize([r'test item <+->','with an',r'ugly hacking item\_layers=["2:","3:",4]'],
                     x='center', y='auto', item_layers=['2:','3:',4])
        it.add_border()

    with slide('Test s3'):
        with group():
            text('test group in group no layer in first group')
            with group()[1]:
                text('Second group should have layer 1')

    with slide('Test layers example'):
        text('First printed on layer 0')
        text('Secondly printed on layer 1')[1]
        text('Printed from layer 2 to 3')[2, 3]
        text('Printed on all layers')[:]
        text('Printed on layer 4')[4]

        with group(width=300)[2:]:
            text('Printed inside group')
            text('for layers 2 to end')
            
    return doc


def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)
