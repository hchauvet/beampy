#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *

doc = document(cache=False)

test_name = 'test_text'


with slide():
    maketitle(test_name.replace('_','\_'))

with slide('Title: text with equation'):
    #text(r'Tutu de $\sqrt{2}$ tata')

    t4 = text(r"""Approximations:\\
    $$\dot{E} \approx \frac{dL/dt}{L_c}$$\\
    $$\frac{dC}{dt} \approx \frac{d\theta_{tip}/dt}{L_c}$$
    """, width = 500, align='center')

    t4.add_border()

save('./html_out/%s.html'%test_name)
#save('./pdf_out/%s.pdf'%test_name)
