#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document()

slide()
maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')

slide()
title("A simple slide")
text(r"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$""")

save('./simple_one.html')
