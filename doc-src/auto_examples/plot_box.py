"""
box
===

Add box around a group. 

.. warning::
   This function is in beta version and need to be interfaced with beampy THEME.

"""

from beampy import *
from beampy.utils import box

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)


with slide('Add nice boxes to group'):

    with group(width=300, height=500, x=20, y='center') as g:
        box(g, title='Very very very long box title', head_height=60)
        text('Box text')

    with group(width=450, height=200, x=g.right+10, y=g.top+0) as g2:
        box(g2, title='Change color and drop-shadow', title_align='center', color='forestgreen',
            shadow=True)
        text('Box text, with a centered title')

    with group(width=450, height=280, x=g.right+10, y=g2.bottom+20) as g3:
        box(g3, color='darkorange', rounded=70, background_color='lightgray', linewidth=4)
        
        text('''
            Without title for the box, more rounded angle, bigger
            linewidth, and a background color
            ''', align='center', width=420-20)
            

display_matplotlib(gcs())

###################################################
#
#Module arguments
#================
#
#.. autofunction:: beampy.utils.box
#   :noindex:
