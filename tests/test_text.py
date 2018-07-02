#!/usr/bin/env python
#-*- coding:utf-8 -*-
from beampy import *

doc = document(cache=False)

test_name = 'test_text'


with slide():
    maketitle(test_name.replace('_','\_'))

with slide('Title: text with equation'):
    t4 = text(r"""Approximations:\\
    $$\dot{E} \approx \frac{dL/dt}{L_c}$$\\
    $$\frac{dC}{dt} \approx \frac{d\theta_{tip}/dt}{L_c}$$
    """, width = 500, align='center')

    t4.add_border()

with slide('Test text with "with"'):
    with text(width=500, align='center'):
        """
        The new test for the text typing system.\\

        $$\frac{10}{4}$$

        I can now \textbf{write long text} easily in my source
        """

        "$$\frac{dC}{dt} \approx \frac{d\theta_{tip}/dt}{L_c}$$"

with slide():
    with text():
        """
        Test text inside the with statement.
        """
    
save('./html_out/%s.html'%test_name)
#save('./pdf_out/%s.pdf'%test_name)
