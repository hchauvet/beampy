"""
ComplicatedBlue
===============

Redefine title page with new arguments and a page layout with add a progress
bar and slide numbers.

.. raw:: html

   <iframe src="../_static/theme_html_outputs/complicatedblue.html" width="100%" height="500px"></iframe>

"""

from beampy import *

doc = document(theme="ComplicatedBlue", quiet=True)

with slide():
    maketitle('Beampy theme ``ComplicatedBlue"',
              author=['Author 1', 'Author 2'],
              lead_author=1,
              meeting='Beampy Users Meeting (BUM 2018)',
              affiliation='From Univ. of Python',
              date='now')

with slide('Slide title are in blue'):
    pass

with slide('Last slide'):
    text('This them includes a progress-bar !')

save('./theme_html_outputs/complicatedblue.html')

display_matplotlib('slide_0')
