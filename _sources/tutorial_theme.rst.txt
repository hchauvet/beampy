.. _tutorial_theme:

Beampy Theme
============

.. warning::
   This tutorial is a Draft! And provide minimum informations to intrepid developers.

To create personal theme you could find inspiration in **beampy/themes/** folder
to the check available examples. The default theme is defined in
`beampy/statics/default_theme.py <https://github.com/hchauvet/beampy/blob/master/beampy/statics/default_theme.py>`_.

Copy one of these files to a new one (in the **beampy/themes/** folder) and
rename it with a new name like **mytheme_theme.py**. You should keep the
"_theme.py" at the end of the file.

Theme file are organised as python dictionary for which keys refers to Beampy
modules. For each Beampy modules the dictionary contains a new dictionary with
module arguments and their default values. For instance, the default theme
define the following for Beampy text module:

.. code-block:: python

   THEME['text'] = {
    'size':20,
    'font':'CMR',
    'color':'#000000',
    'align':'',
    'x':'center',
    'y':'auto',
    'width':None,
    'usetex':True,
    'va': ''
    }


Then you could load your theme using:

.. code-block:: python

   #for a file named mytheme_theme.py in beampy/themes folder
   doc = document(theme='mytheme')


You could also change theme property directly in your presentation source file.

.. code-block:: python

   from beampy import *

   doc = document(theme="mytheme")
   # show keys of the theme dictionary
   print(doc._theme)

   # Change some keys
   doc._theme['title']['color'] = '#000000'
   doc._theme['title']['x'] = 'center'


If your proud of your new theme, please share it with us ! Either creating a
`github pull request <https://github.com/hchauvet/beampy/pulls>`_ or send it to
the mailing list `mailing list <https://framalistes.org/sympa/info/beampy>`_
