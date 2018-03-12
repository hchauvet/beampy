#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *
import os

test_name = 'test_layers'
doc = document(cache=False, optimize=False)


with slide():

    text('test')

    with group() as g1:
        text('toto')
        ss = text('tutu')
        with group():
            text('tutu')




save('./html_out/%s.html'%test_name)
#save('./pdf_out/%s.pdf'%test_name)
