# Beampy

Beampy is a python tool to create slideshow in svg that can be display with HTML5 or PDF.

## Introduction

Beampy is in between Latex beamer and html5 slideshow libraries. It creates slides as svg, that can contains vectorial elements, raster images and videos. It uses Latex to render texts and mathematics transleted into svg. Svg slides are expoted in html5 (on file containing everithing), in raw svg or in pdf.

A quick exemple of the python source code for making a presentation:
```python
from beampy import *

doc = document()

slide()
maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')

slide()
title("Beampy test")
text("""Use LaTeX to render text and $$\\sqrt{10}$$""", align='center')

save('./beampy_presentation.html')
```

## Instalation

## Exemples

## How to write your own modules


