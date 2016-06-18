#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=False)

with slide('Svg animation'):
    animatesvg("../examples/svg_anims/", width="500", x='center', y='center')

save('test_animatesvg.html')
