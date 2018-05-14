=================================
Welcome to Beampy's documentation
=================================


Beampy is a Python tool to create slide-show. It's inspired by *Latex-Beamer*
but generates HTML5 documents instead of PDF. HTML format allows to includes a
wide range of contents like video and Scalable Vector Graphics (SVG) and is
compatible across a lot of platforms and web-browsers.

The slides are written using Python syntax to call Beampy modules (figure, text,
video, `Check Beampy Modules gallery <auto_examples/index.html>`_). Unlike in
*Latex-Beamer*, changing Beampy modules positions is straightforward and could
be done using absolute or relative coordinates. Beampy modules are then rendered
by Beampy to produce SVG or HTML elements. These elements are written to an
unique HTML file, and the entire content of your presentation are embedded in
one file!

Beampy uses *Latex* to render text, keeping all the power of *Latex* typesetting
system.
   
Sometimes we need to keep a PDF of our presentation, so Beampy can also export
in PDF (HTML elements like video are converted to a still image).

As writing a presentation slideshow is an iterative process, Beampy uses a
simple cache system to compile slide elements only when they are added or
modified!

A quick example
===============


.. code-block:: python

                from beampy import *
                
                doc = document()

                with slide():
                    maketitle('Beampy a tool to make simple presentation', ['H. Chauvet'])

                with slide('Beampy test'):
                    text(r'\href{#0}{Go to Title}')
                    text(r'Use LaTeX to render text and $$\sqrt{10}$$', align='center')

                with slide('Beampy test with animated layers'):
                    text(r'\href{#0}{Go to Title}')[:]
                    text(r'Use LaTeX to render text and $$\sqrt{10}$$', align='center')[1]

                save('./simple_one.html')
                

.. raw:: html

         <iframe src="_static/simple_one.html" width="100%" height="400px"></iframe>

How to start
============

You could check the install instructions on the :ref:`beampy_install` page. Then
you could have look at the available :ref:`tutorials` or have a look to
:ref:`beampy_modules`.

Contributions
=============
* Use the `mailing list <https://framalistes.org/sympa/info/beampy>`_ to ask questions/bugs/suggestion: 
* You can fill bugs, rise issues and suggest features on the issue tracker of `github <https://github.com/hchauvet/beampy/issues>`_
* Check the API autodoc (:ref:`API`)
* Check the change-log (:ref:`changelog`) to see new features and source codes updates.
* Guide to create new Beampy modules.
* Guide to create new Beampy theme.

.. warning::

   Beampy is still in development stage, the syntax could evolve.




.. toctree::
   :hidden:

   install
   tutorials
   auto_examples/index
   themes
   API
   changelog
   todo

