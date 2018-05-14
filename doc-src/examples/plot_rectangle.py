"""
rectangle
=========

Easiest way to create rectangle in svg rather than using the
:py:mod:beampy.svg.

"""

from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)

with slide('Svg: rectangle'):
    rectangle(width=300, height=300, y='center')
    rectangle(width=100, height=100, color='yellow', y='center',
              edgecolor='red')

display_matplotlib(gcs())


####################################################
#
#Module arguments
#================
#
#.. autoclass:: beampy.rectangle
#   :noindex:
#
