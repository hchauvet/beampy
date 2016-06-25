#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=True)

with slide():
    animatesvg("../examples/svg_anims/", width="500", x='center', y='center')
    animatesvg("../examples/svg_anims/", width="100", x='0.1', y='0.1')
with slide():
    animatesvg("../examples/svg_anims/", width="500", x='center', y='center')

save('test_animatesvg.html')
