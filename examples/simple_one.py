#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=False)

slide()
maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')


slide()
title("A simple slide")
text(r"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$""", y='center', x='center')


slide()
title('A seconde title')
text(r'\href{#0}{Go to Title}')

save('./simple_one.html')
