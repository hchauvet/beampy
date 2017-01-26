#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
sys.path.append('/home/hugo/developpement/python/beampy_git/')

from beampy import *

doc = document(cache=False)

with slide():
    text('Test de toto')

with slide():
    #text(r'Tutu de $\sqrt{2}$ tata')

    t4 = text(r"""Approximations:\\
    $$\dot{E} \approx \frac{dL/dt}{L_c}$$\\
    $$\frac{dC}{dt} \approx \frac{d\theta_{tip}/dt}{L_c}$$
    """, width = 500, align='center', x = 0.12,
    y=0.3)

    
save('test_text.html')
