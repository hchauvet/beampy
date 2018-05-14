"""
figure
======

Insert a figure inside a slide.

Figure format can be:

* pdf
* svg
* jpeg
* png
* Matplotlib figure object
* Bokeh figure object

From one file
-------------
"""


from beampy import *

# Remove quiet=True to get beampy compilation outputs
doc = document(quiet=True)

with slide('A figure from a file'):
    figure('./ressources/test_0.svg', width=400)


display_matplotlib(gcs())

########################################################
#
#From Matplotlib
#---------------
#

with slide('A matplotlib figure'):
    import matplotlib.pyplot as mpl
    import numpy as np

    f = mpl.figure()
    mpl.plot(np.random.rand(100), np.random.rand(100), 'o')

    figure(f, width=500)

display_matplotlib(gcs())

########################################################
#
#From Bokeh
#----------
#
#.. note::
#   No svg export available for now, check the
#   html file of the prensetation
#

with slide('A bokeh figure'):
    from bokeh.plotting import figure as bokfig

    p = bokfig(height=300, width=600)
    x = np.random.rand(100)
    y = np.random.rand(100)
    p.circle(x, y, legend="sin(x)")

    # figure(p)

# Export the 3 slides of the presentation
save('./examples_html_outputs/figure.html')

########################################################
#
#HTML output
#===========
#
#.. raw:: html
#
#    <iframe src="../_static/examples_html_outputs/figure.html" width="100%" height="500px"></iframe>
#
#
#Module arguments
#================
#
#.. autoclass:: beampy.figure
#   :noindex:
#

