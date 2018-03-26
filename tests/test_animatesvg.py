#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document(cache=False, optimize=False)

with slide():
    animatesvg("../examples/svg_anims/*.svg", width="500", x='center', y='center')
    animatesvg("../examples/svg_anims/*.svg", width="100", x='0.1', y='0.1')

with slide('Animate with layers'):
    with group()[:]:
        animatesvg("../examples/svg_anims/*.svg", width="500")
        with group()[1]:
            animatesvg("../examples/svg_anims/*.svg", width="100")

save('./html_out/test_animatesvg.html')
