#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *

doc = document(cache=False)

test_name = 'test_video'


with slide():
    maketitle(test_name.replace('_','\_'))

with slide('Title: test video'):
    video('../examples/test.webm')

with slide('Test video not embedded'):
    video('../examples/test.webm', embedded=False)
    
with slide():
    video('../examples/test.webm')
    video('../examples/test.webm')[1]
    
save('./html_out/%s.html'%test_name)
# save('./pdf_out/%s.pdf'%test_name)
