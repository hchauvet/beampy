#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *
from beampy.geometry import distribute

doc = document(cache=False, theme='ComplicatedBlue')

with slide():
    maketitle('Beampy a tool to make simple presentation',
    ('Hugo Chauvet',),'Institut de python',date="now")


    s = svg("""
    <rect width="782" height="10" style="fill:royalblue;"/>
    """, x=0.01, y=0.6)

with slide("A simple slide"):
    text(r"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$""",
        y='center', x='center')

with slide('A second title'):
    text(r'\href{#0}{Go to Title}')

save('./simple_one.html')