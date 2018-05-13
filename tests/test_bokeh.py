#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *
import os

test_name = 'test_bokeh'
doc = document(cache=False, optimize=False)


with slide('Test s1'):
    from bokeh.plotting import figure as bokfig
    import numpy as np
    p = bokfig(height=300, width=600)
    x = np.linspace(0, 4*np.pi, 30  )
    y = np.sin(x)
    p.circle(x, y, legend="sin(x)")

    text('test')[:]
    figure(p)[1]

with slide('Test 2'):
    text('toto')

save('./html_out/%s.html'%test_name)
# save('./pdf_out/%s.pdf'%test_name)
