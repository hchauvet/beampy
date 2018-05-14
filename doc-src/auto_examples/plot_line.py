"""
line
====

Easiest way to create lines in svg rather than using the :py:mod:beampy.svg.

"""


from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)

with slide('Svg: Line'):
    line(800-20, 600-50, x=20, y=50, color='red')
    hline(300, color='orange', linewidth='4px')
    vline(400, color='crimson', linewidth='10px', opacity=0.5)

display_matplotlib(gcs())

####################################################
#
#Module arguments
#================
#
#.. autoclass:: beampy.line
#   :noindex:
#
#.. autofunction:: beampy.hline
#   :noindex:
#
#.. autofunction:: beampy.vline
#   :noindex:
#

