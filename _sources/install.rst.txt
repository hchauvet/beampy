.. _beampy_install:

Install Beampy
==============

Beampy relies on several external programs to run properly.

On linux these programs could be easily installed from packages of your linux distribution.

On Mac/Windows Beampy has never been tested but all dependencies seems compatible with Windows and Mac.

Dependencies
------------

External programs
*****************

* **ffmpeg [or avconv]**: for video processing
* **inkscape**: to extract some svg properties like width and height.
* **Latex**: to manage text, equations and more (Need the standalone class, in texlive  it's in the texlive-latex-extra package).
* **dvisvgm**: to translate latex dvi to svg, see the `dvisvgm website <http://dvisvgm.bplaced.net/>`_. It is included in Tex-Live distribution
* **pdfjoin**: to merge multiple single pdf files to a unique one. (part of pdfjam project and included in TexLive distribution)
* **pdf2svg**: to include pdf as svg in slides.

Python libraries
****************

* **Beautiful Soup**: to parse svg file.
* **lxml**: used by beautifulsoup to parse xml
* **Python Image Library (PIL)**: to minipulate images.
* **pygments**: [Optional] allows to add code syntax coloration to display code in your presentation.
* **bokeh**: [Optional] Include `bokeh <https://bokeh.pydata.org/en/latest/>`_ interactive plots in your presentation.

Beampy also includes a version of `scour <https://github.com/codedread/scour>`_, an svg optimiser.

Linux
-----

The exemple is given for debian or ubuntu distro using **apt**.

Install dependencies using apt-get
**********************************

.. code-block:: bash

   sudo apt-get install ffmpeg inkscape texlive-extra-utils texlive-latex-extra pdf2svg python-pil python-beautifulsoup

From Python pip
***************

.. code-block:: bash

   sudo pip install  -e git+https://github.com/hchauvet/beampy.git#egg=beampy


From the github archive
***********************

Download beampy archive (.zip) from github `here <https://github.com/hchauvet/beampy/archive/master.zip>`_.
Unzip the folder and copy the Beampy folder on your disk and add your folder
location to the python path.

.. code-block:: python

   import sys
   sys.path.append('/path/to/beampy_folder')

   from beampy import *


Link external program executables to Beampy
-------------------------------------------

Beampy automatically search for external executables. If it fails, you can setup the path to these excecutables manualy.

.. code-block:: python

   from beampy import *

   doc = document()

   # To let Bempy search automatically for a program replace
   # the path by "auto" (check the default_theme.py file)

   doc._theme['document']['external_app'] = {
   "inkscape": "/path/to/inkscape",
   "dvisvgm": "/path/to/dvisvgm",
   "pdfjoin": "/path/to/pdfjoin",
   "video_encoder": '/path/to/ffmpeg [or avconv]',
   "pdf2svg": "/path/to/pdf2svg"
   }

