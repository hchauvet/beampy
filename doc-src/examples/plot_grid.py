"""
grid
====

Easiest way to create grid in svg rather than using the :py:mod:beampy.svg

.. note::
   This function is not yet optimised creating a grid loop over hline and vline resulting
   in a slow compilation time.

"""

from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)


with slide('Svg: grid'):
    grid(25, 25, color='gray')
    grid(100, 100, color='crimson')

display_matplotlib(gcs())

####################################################
#
#Module arguments
#================
#
#.. autofunction:: beampy.grid
#   :noindex:
#
