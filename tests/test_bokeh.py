#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *
import numpy as np
from bokeh.plotting import figure as bokfig
import os

test_name = 'test_bokeh'
doc = document(cache=True, optimize=False)

with slide():
    p = bokfig(sizing_mode='scale_both')
    p.circle([1,2], [3,4])
    figure(p)    

with slide('Test s1'):
    p = bokfig(height=300, width=600)
    x = np.linspace(0, 4*np.pi, 30  )
    y = np.sin(x)
    p.circle(x, y, legend="sin(x)")

    text('test')[:]
    figure(p)[1]

with slide():
    p = bokfig(height=600, width=800)
    x = np.linspace(0, 4*np.pi, 30  )
    y = np.sin(x)
    p.circle(x, y, legend="sin(x)", size=10)

    figure(p)

with slide():
    p = bokfig(height=300, width=600)
    x = np.linspace(0, 4*np.pi, 30  )
    y = np.sin(x)
    p.circle(x, y, legend="sin(x)")

    figure(p)

    p = bokfig(height=300, width=600)
    x = np.linspace(0, 4*np.pi, 30  )
    y = np.sin(x)
    p.circle(x, y, legend="sin(x)", color='red')

    #figure(p)
    
with slide():
    N = 4000
    x = np.random.random(size=N) * 100
    y = np.random.random(size=N) * 100
    radii = np.random.random(size=N) * 1.5
    colors = [
        "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
    ]

    TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

    p = bokfig(tools=TOOLS)

    p.scatter(x, y, radius=radii,
          fill_color=colors, fill_alpha=0.6,
          line_color=None)

    figure(p)
    
save('./html_out/%s.html'%test_name)
# save('./pdf_out/%s.pdf'%test_name)
