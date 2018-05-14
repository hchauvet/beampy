"""
code
====

Include code in your presentation.

Code coloration is managed by `Pygments <http://pygments.org/>`_

.. warning::
       This module is in very draft stage !!!

"""

from beampy import *

# Remove quiet=True to get beampy compilation outputs
doc = document(quiet=True)

with slide('A small python code'):
    c = code("""
    from pylab import *

    n = range(10)

    plot(n, n*random.rand(), 'ko')

    for i in range(10):
        print(i)

    """, width=500)

display_matplotlib(gcs())

###########################################################
#Module arguments
#================
#
#.. autoclass:: beampy.code
#   :noindex:
#
