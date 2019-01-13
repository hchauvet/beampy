# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Test of figure module
"""

from beampy import *
import pylab as p

test_name = 'test_figures'
doc = document(cache=False)

with slide("Matplotlib figure"):
    fig = p.figure()
    x = p.linspace(0,2*p.pi)
    
    p.plot(x, p.sin(x), '--')
    
    figure(fig)


with slide("Mpl animation"):

    anim_figs = []
    for i in range(20):
        fig = p.figure()   
        x =  p.linspace(0,2*p.pi)
        p.plot(x, p.sin(x+i))
        p.plot(x, p.sin(x+i+p.pi))
        p.close(fig) 
        anim_figs += [ fig ]
        
        
    animatesvg( anim_figs )

with slide("Test gif"):
    figure('./test.gif', width=300)

save('./html_out/%s.html'%test_name)
# save('./pdf_out/%s.pdf'%test_name)
