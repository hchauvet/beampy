"""
HipsterChic
===========

Redefine the maketitle function in the theme with a background color and center
the title of slides.

"""

from beampy import *

doc = document(theme="HipsterChic", quiet=True)

with slide():
    maketitle('Beampy theme ``HypsterChic"',
              author='Single Author',
              subtitle='A very very very very very long subtitle on the right')

display_matplotlib(gcs())

with slide('Slide title are centered'):
    pass

display_matplotlib(gcs())

