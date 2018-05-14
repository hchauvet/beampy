"""
maketitle
=========

Create a title slide for the presentation.

:py:mod:`maketitle` could be overwritten by the theme used for the prensentation


"""

from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)

with slide():
    maketitle('Beampy a tool to make simple presentation',
              author='H. Chauvet',
              subtitle='Written in Python',
              date='now')


display_matplotlib(gcs())


######################################################################################
#
#Module arguments
#================
#
#.. autofunction:: beampy.maketitle
#   :noindex:
