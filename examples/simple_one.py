#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *

doc = document(cache=False)

with slide():
    maketitle('Beampy a tool to make simple presentation', ['H. Chauvet'])

with slide('Beampy test'):
    text(r'\href{#0}{Go to Title}')
    text(r'Use LaTeX to render text and $$\sqrt{10}$$', align='center')

with slide('Beampy test with animated layers'):
    text(r'\href{#0}{Go to Title}')[:]
    text(r'Use LaTeX to render text and $$\sqrt{10}$$', align='center')[1]

save('./simple_one.html')