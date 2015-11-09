# Beampy

Beampy is a python tool to create slideshow in svg that can be displayed with HTML5
(tested on Firefox and Chromium)
The size of slides is fixed, like in a Latex Beamer document.

Beampy presentation output only one html file with every contents embeded.

## Introduction

Beampy is in between Latex beamer and html5 slideshow libraries.
It creates slides in svg format (with a bit of HTML5 for video and interactive
things like Bokeh plots).

Slide can contains:
- Vector graphics (svg)

- Raster images (png, jpeg)

- Raster videos (using webm format)

- Animated vectorial graphics (list of svg figures)

- bokeh plots (experimental)

- Texts are rendered using Latex (then translated to svg, as vector paths)

- Tikz/PGF figure and graphics

Svg slides are expoted in html5 with every raster elements embed in one file.
The slides can also be exported to svg and pdf (videos and animations are not rendered in pdf/Svg)

## A quick exemple :

```python
from beampy import *

doc = document()

slide()
maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')

slide()
title("Beampy test")
text("""Use LaTeX to render text and $$\\sqrt{10}$$""", align='center')

save('./beampy_presentation.html')
#To save in pdf just change the above command to the following
#save('./beampy_presentation.pdf')
```

## Instalation

Add *beampy* folder to your python path.

You can do it at the begining of your script using *sys* module:

```python
import sys
sys.path.append('/path/to/beampy')

#Test to import beampy
from beampy import *
```

### Requirements:
Beampy includes a version of svg optimized written in python "scour"
[https://github.com/codedread/scour](https://github.com/codedread/scour).

##### Python programs

- Beautiful Soup (pip install beautifulsoup4// or use conda )
- Python Image Library (PIL) (available in linux // or in anaconda)

##### External programs

- Inkscape (for pdf export and svg size estimation)
- dvisvgm (to translate latex dvi to svg) Available in Tex Live distribution
  [http://dvisvgm.bplaced.net/](http://dvisvgm.bplaced.net/)

  On debian:
  sudo apt-get install texlive-extra-utils

To change path of these command in beampy:
```python
from beampy import *

doc = document()

document._external_cmd['inkscape'] = '/path/to/inkscape'
document._external_cmd['dvisvgm'] = '/path/to/dvisvgm'
```

##### Optionals

- python-pygment (for code coloration command)
- bokeh (to include bokeh interactive plot in figure command)

## Exemples

###Figure

###Svg plot animation

###Bokeh interactive plot

###Group and columns

###Placement system

## How to write your own modules


