#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=True)

slide()
maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')


slide()
title("A simple slide")
aa = text(r"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$""", y='center', x='center')
text('toto', y=aa.center+0.05, x=0.1)

slide()
title('A seconde title')

begingroup(x=0.01, width=500, height=400, background="#666")
text('tutu')
video("./test.webm" ,width=300)
text('tata')
endgroup()

save('./simple_one.html')
