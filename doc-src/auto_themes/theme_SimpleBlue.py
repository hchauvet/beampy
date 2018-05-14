"""
SimpleBlue
==========

Just change title color to simple blue.

"""

from beampy import *

doc = document(theme="SimpleBlue", quiet=True)

with slide():
    maketitle('Beampy theme ``SimpleBlue"',
              author=['Author 1', 'Author 2'],
              subtitle='A subtitle',
              date='now')

display_matplotlib(gcs())

with slide('Slide title are in blue'):
    pass

display_matplotlib(gcs())
