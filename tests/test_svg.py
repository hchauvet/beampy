#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *

doc = document(cache=False)

test_name = 'test_svg'

with slide('Test rectangle size'):

    r1 = rectangle(width=200, height=200, x=5, y='center')
    r2 = rectangle(width=200, height=200, x=300, y='center',
                   color='yellow', opacity=0.3, linewidth=30)

    r1.add_border()
    r2.add_border()


save('./html_out/%s.html'%test_name)
