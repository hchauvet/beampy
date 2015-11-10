# Beampy

Beampy is in early stage development! 

Beampy is a python tool to create slide-show in svg that can be displayed with HTML5
(tested on Firefox and Chromium)
The size of slides is fixed, like in a Latex Beamer document.

Beampy presentation output only one html file with every contents embedded.

[Beampy tests presentation](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html) (source is in *examples/beampy_tests_modules.py*)

## Introduction

Beampy is in between Latex beamer and html5 slide-show libraries.
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

Svg slides are exported in html5 with every raster elements embed in one file.
The slides can also be exported to svg and pdf (videos and animations are not rendered in pdf/Svg)

Beampy uses a simple cache system to compile slide only when it's needed!

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

[beampy_presentation.html](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/simple_one.html)

## Instalation

Add *beampy* folder to your python path.

You can do it at the beginning of your script using *sys* module:

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
  
- pdfjoin (tool to join pdf pages) it is part of [pdfjam project](http://www2.warwick.ac.uk/fac/sci/statistics/staff/academic-research/firth/software/pdfjam/) and is also included in Tex Live distribution
    
   On debian:
   sudo apt-get install texlive-extra-utils


To change path of these command in beampy (by defaults the command name is used):
```python
from beampy import *

doc = document()

document._external_cmd['inkscape'] = '/path/to/inkscape'
document._external_cmd['dvisvgm'] = '/path/to/dvisvgm'
document._external_cmd['pdfjoin'] = '/path/to/pdfjoin'
```

##### Optionals

- python-pygment (for code coloration command)
- bokeh (to include bokeh interactive plot in figure command)

## Examples

To see all these examples download the output **beampy_tests.html** and source **beampy_tests_modules.py** files in the example folder

###Figure


```python
from beampy import *
doc = document()

slide()
title('Figure')
figure("./svg_anims/test_0.svg", width="500")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#2)

###Svg plot animation

Click on figure to start the animation 

```python
from beampy import *
doc = document()

slide()
title('Svg animation')
animatesvg("./svg_anims/", width="500")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#3)

###Video

```python
from beampy import *
doc = document()

slide()
title('Video')
video("./test.webm", width="500", height="294")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#4)

###Group and columns

```python
from beampy import *
doc = document()

slide()
title('Group and columns')
colwidth=350
begingroup(width=colwidth, height=doc._height-100, x="1cm", y="1.8cm", background="#000")
text("""
This is a test for a long text in a column style. 

$$ \sum_{i=0}^{10} x_i $$ 
""", align="center", width=colwidth-20, color="#ffffff")
endgroup()

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#5)

###Relative positioning

```python
from beampy import *
doc = document()

slide()
title('Relative positioning')
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")

text("youpi x=+1cm, y=+0.5cm", x="+1cm", y="+0.5cm")
text(r"youpi x=-1.5cm,\\ y=+0.5cm", x="-1.5cm", y="+0.5cm")
text(r"youpi x=+1.5cm,\\ y=+0cm", x="+1.5cm", y="+0cm")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#6)

###Tikz


```python
from beampy import *
doc = document()

slide()
title('Tikz')

tikz(r"""\draw[->] (0,0) -- ++ (10,5);""", x="+3cm", y="+5px")

save('test.html')
```

Here is a more complex Tikz output on the result:
[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#7)

###Bokeh interactive plot

```python
from beampy import *
from bokeh.plotting import figure as bokfig
import numpy as np

doc = document()

slide()
title('Bokeh plot')
p = bokfig(height=300, width=600)
x = np.linspace(0, 4*np.pi, 30  )
y = np.sin(x)
p.circle(x, y, legend="sin(x)")
figure(p, y="+5px", x="center")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/exemples/beampy_tests.html#8)

### Code highlight

[Pygments](http://pygments.org/) is used to highlight code

```python
from beampy import *


doc = document()

slide()
title('Code')

begingroup(width=700, height=155, background="#EFEFEF")

code("""
slide()
title('Bokeh plot')
from bokeh.plotting import figure as bokfig
import numpy as np
p = bokfig(height=300, width=600)
x = np.linspace(0, 4*np.pi, 30  )
y = np.sin(x)
p.circle(x, y, legend="sin(x)")
figure(p, y="+5px", x="center")
""", langage="python", width="300", x="1cm")

endgroup()

save('test.html')
```

## Change theme

To change the global theme of slide copy the file 
[/beampy/statics/default.theme] where you want change it and load it with:

```python
from beampy import * 

doc = document()
doc.load_theme('./path/to/cool.theme')
```

## How to write your own modules

Check files in *./beampy/modules/* folder.

A module file contain to functions, one to define the command and the other to define the render (how command is transformed to svg)

The base of a module file 

```python 
from beampy import document
from beampy.functions import gcs, convert_unit

#For the command function should output write dictionary to document._data list with 'type', 'content', 'args' and 'render' keys
def my_command( data, x='center', y='auto', width=None, height=None):
    
    if width == None:
        width = str(document._width)
    if height == None:
        height = str(document._height)
            
    args = {"x":str(x), "y": str(y) , "width": str(width), "height": str(height)}
            
    command_out = {'type': 'svg', 'content': data, 'args': args, "render": myrender_command}
    
    #Add command_out dictionary to the document data, gcs() function return current slide id
    document._contents[gcs()]['contents'] += [ command_out ]

#Render should output 3 variables: the svgpart (as text), the width (float), the height (float) 
def myrender_command( datain, argsin ):
    
    #datain will be assigned to command_out['content'] 
    #argsin will be assigned to command_out['args']
    
    #Now you have to translate datatin into svg syntax (or html, if args['type'] == 'html')
    svgout = "<g> My svg output </g>"
    width = my_svg_width
    height = my_svg_height
    
    return svgout, float(width), float(height) 

```

Then you can test you module by importing your python file

```python
from beampy import * 

from my_module import *

doc = document()

slide()
title('My module')
my_module("data needed by my module")

save('test.html')
```
