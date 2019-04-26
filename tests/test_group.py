#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pytest

from beampy import *
import os

test_name = 'test_group'

@pytest.fixture
def make_presentation():
    doc = document(cache=False, optimize=False)
    videofile = '../examples/test.webm'

    with slide('TEST'):



        with group(width=200, x=0.1, y='center') as g2:
            video(videofile, x='center', y='auto')

            with group(width = 100, height=50, x=0, background='lightblue') as g5:
                text('tutu')
            with group(width = 100, height=50, x = g5.right + 0, y=g5.top+0, background='lightgreen'):
                text('toto')

            figure('./test.gif')

        e0 = text('toto', x=g2.left + 0, y=g2.top - bottom(0.01))

        with group(width=350, height=500, x=g2.right + 0.1, y=g2.center+center(0)) as g3:
            text('tata')
            text('ploplo')

            with group(height=350) as g4:
                video(videofile)
                text('Petite legende')


        for g in [g2, g3, g4]:
            g.add_border()

        text('youpi', x=g3.center + center(0), y=g3.top - bottom(0.1))


    with slide('test group relative position'):

        with group(x='center', y='center') as g1:
            text('inside first group')

        with group(x=g1.left+0, y=g1.bottom+0) as g2:
            text('inside second group')


        g1.add_border()
        g2.add_border()
        
    return doc


# TODO: solve the bug for video when pdf is exported after html....
def test_html(make_presentation):
    doc = make_presentation
    save('./html_out/%s.html'%test_name)

def test_pdf(make_presentation):
    doc = make_presentation
    save('./pdf_out/%s.pdf'%test_name)


