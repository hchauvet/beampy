"""
arrow
=====

Add arrow to slide. Arrow are drawn using tikz.

"""

from beampy import *

# Remove quiet=True to get beampy compilation outputs
doc = document(quiet=True)

with slide('Draw an arrow'):
    arrow(x=10, y=0.1, dx=780, dy=0, lw=6, color='Crimson')

    rectangle(x=0.05, y=0.3, width=150, height=150,
              color='crimson', edgecolor='None')

    t1 = text('First', y=0.25, x=0.55)
    a1 = arrow(x=t1.right+0, y=t1.bottom+0, dx=100, dy=100)
    t2 = text('Second', y=a1.bottom+0, x=a1.right+0)
    a2 = arrow(x=t2.center+0, y=t2.bottom+0, dx=-100, dy=150, color='red',
               style='<->', bend='left', head_style='latex', lw=4)
    t3 = text('Third', y=a2.bottom+bottom(0), x=a2.left+right(0))

    a3 = arrow(x=t3.left+0, y=t3.center+0, dx=-350, dy=-170,
               color='LightGreen', lw=5, out_angle=180, in_angle=0,
               dashed=True)


display_matplotlib(gcs())

###############################################################################
#
#Module arguments
#================
#
#.. autofunction:: beampy.arrow
#   :noindex:
#

