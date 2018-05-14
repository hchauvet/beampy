"""
text
====

Add text to your slide.

By default text is processed by Latex and accept Latex syntax.

"""

from beampy import *

# Remove quiet=True to get beampy compilation outputs
doc = document(quiet=True)

with slide('Text module'):
    text(r'A simple text with $\LaTeX$ syntax so you could write equation:')
    text(r'\sqrt{\frac{x}{y}}')

    t = text(r'You could align text to center by using the \textbf{align} parameter',
         align='center', width=350)

    # add border to the text to see the effect of center alignment
    t.add_border()

display_matplotlib(gcs())


##########################################################
#
#Module arguments
#================
#
#.. autoclass:: beampy.text
#   :noindex:
#
