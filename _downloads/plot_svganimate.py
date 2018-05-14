"""
animatesvg
==========

Create animation from a list of svg files or a list of matplotlib figures.

From svg file list
------------------
"""

from beampy import *

# Remove quiet=True to get beampy compilation outputs
doc = document(quiet=True)

with slide('Animation from svg files'):
    animatesvg("./ressources/svg_anims/*.svg", width="600")

display_matplotlib(gcs())

##########################################################################
#
#From matplotlib figure list
#----------------------------
#

import pylab as p

with slide('Animation from matplotlib figures'):

    anim_figs = []
    for i in range(20):
        fig = p.figure()
        x =  p.linspace(0,2*p.pi)
        p.plot(x, p.sin(x+i))
        p.plot(x, p.sin(x+i+p.pi))
        p.close(fig)
        anim_figs += [fig]

    animatesvg(anim_figs)

save('./examples_html_outputs/animatesvg.html')

##########################################################################
#
#HTML output
#===========
#
#.. raw:: html
#
#    <iframe src="../_static/examples_html_outputs/animatesvg.html" width="100%" height="500px"></iframe>
#
#Module arguments
#================
#
#.. autoclass:: beampy.animatesvg
#   :noindex:
#
