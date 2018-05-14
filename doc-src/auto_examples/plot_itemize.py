"""
itemize
=======

Create a list or an enumeration of items from an input python list of strings.

"""

from beampy import *

# Remove quiet=True to get Beampy render outputs
doc = document(quiet=True)

with slide('Itemize'):
    itemize(['''This is a long text inside an item. 
             It will crop at the given itemize width''',
             r'\sqrt{1+10} \times \frac{x}{y}',
             'tata'],
            width=400
    )

display_matplotlib(gcs())

####################################################
#
#Module arguments
#================
#
#.. autofunction:: beampy.itemize
#   :noindex:
#
