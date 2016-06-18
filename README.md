# Beampy

Beampy is in early stage development!

Beampy is a python tool to create slide-show in svg that can be displayed with HTML5
(tested on Firefox and Chromium)
The size of slides is fixed, like in a Latex Beamer document.

Beampy presentation output only one html file with every contents embedded.

[See a Beampy tests presentation](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html) (source is in *examples/beampy_tests_modules.py*)

## TODO:
* **work in progress** Improvement of cache, (bug of color change for text)
* A clear documentation

## Curent version:
### 0.4
* All slide are now loaded into ram, improve speed
* Modules are now classes which inherit from a base class "beampy_module" in modules/core.py

## Introduction

Beampy is in between Latex beamer and html5 slide-show libraries.
It creates slides in svg format (with a bit of HTML5 for video and interactive
things like Bokeh plots).

Slide can contains:
- Vector graphics (svg, pdf)

- Raster images (png, jpeg)

- Raster videos (using webm format)

- Animated vectorial graphics (list of svg figures)

- bokeh plots (experimental)

- Texts are rendered using Latex (then translated to svg, as vector paths)

- Tikz/PGF figure and graphics

Svg slides are exported in html5 with every raster elements embed in one file.
The slides can also be exported to svg and pdf (videos and animations are rendered as first frame image in pdf/Svg)

Beampy uses a simple cache system to compile slide only when it's needed!

## A quick example :

```python
from beampy import *

doc = document()
#to export in pdf add doc = document(format = pdf)

with slide():
   maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')

with slide():
   title("Beampy test")
   text("""Use LaTeX to render text and $$\\sqrt{10}$$""", align='center')

save('./beampy_presentation.html')
#To save in pdf just change the above command to the following and add the option
#format = "pdf" to document class
#save('./beampy_presentation.pdf')
```

[beampy_presentation.html](https://cdn.rawgit.com/hchauvet/beampy/master/examples/simple_one.html)

## Installation

Add *beampy* folder to your python path.

You can do it at the beginning of your script using *sys* module:

```python
import sys
sys.path.append('/path/to/folder/beampy-master/')

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

- ffmpeg For video manipulations (sudo apt-get install ffmpeg (linux) // [binaries for mac](http://ffmpegmac.net/)
- Inkscape (for pdf export and svg size estimation)
- dvisvgm (to translate latex dvi to svg) Available in Tex Live distribution
  [http://dvisvgm.bplaced.net/](http://dvisvgm.bplaced.net/)

  On debian:
  sudo apt-get install texlive-extra-utils

- pdfjoin (tool to join pdf pages) it is part of [pdfjam project](http://www2.warwick.ac.uk/fac/sci/statistics/staff/academic-research/firth/software/pdfjam/) and is also included in Tex Live distribution

   On debian:
   sudo apt-get install texlive-extra-utils


- pdf2svg To translate pdf2svg [github](https://github.com/db9052/pdf2svg) (sudo apt-get install pdf2svg // For os X available on MacPort)

The executable of these external programs is set-up automatically. If this fail, you can set manually the path to the executable of the external program.
For that, you have create a new theme file **my_theme.py** containing:

```python

#To let Bempy search automatically for a program replace
#the path by "auto" (check the default_theme.py file)

THEME = {

'document':{
    'external_app': {"inkscape": "/path/to/inkscape",
        "dvisvgm": "/path/to/dvisvgm",
        "pdfjoin": "/path/to/pdfjoin",
        "video_encoder": '/path/to/ffmpeg [or avconv]',
        "pdf2svg": "/path/to/pdf2svg"}
    }
}
```

Then when you create your beampy document, load your theme, this will set the new paths for external programs.

```python
from beampy import *

doc = document(theme='/path/to/my_theme.py')
```

##### Optionals

- python-pygment (for code coloration command)
- bokeh (>= 0.11) (to include bokeh interactive plot in figure command)

## Examples

To see all these examples download the output **beampy_tests.html** and source **beampy_tests_modules.py** files in the example folder

###Figure


```python
from beampy import *
doc = document()

with slide():
    title('Figure')
    figure("./svg_anims/test_0.svg", width="500")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#2)

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

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#3)

###Video

```python
from beampy import *
doc = document()

slide()
title('Video')
video("./test.webm", width="500", height="294")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#4)

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

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#5)

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
text(r"youpi x=-0, \\ y=+0.5cm", x="-0", y="+0.5cm")
text(r"youpi x=+1.5cm,\\ y=-0", x="+1.5cm", y="-0")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#6)

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
[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#8)

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

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#9)

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

### Arrow

To create arrow (using tikz commands behind)

```python

from beampy import *

doc = document()

slide('Test arrow')

#An arrow starting at 400px, 400px, and of size 40 in x and 40 in y.
arrow(400, 400, 40, 40, bend='left')

save('test.html')
```

## Change theme

Basic theme features are store in a dictionary *document._theme*. You can check
the default features in [/beampy/statics/default_theme.py]. You can adapt this dictionary
to fit your needs:

```python
from beampy import *

doc = document()
#sow keys of the theme dictionary
print doc._theme

#Change some keys
doc._theme['title']['color'] = '#000000'
doc._theme['title']['x'] = 'center'

```

## How to write your own module

Check files in *./beampy/modules/* folder.

A module file contain to functions, one to define the command and the other to define the render (how command is transformed to svg (or html)

The base of a module file

```python
from beampy.functions import add_to_slide
from beampy.geometry import positionner

#For the command function should output write dictionary
#to document._data list with 'type', 'content', 'args' and 'render' keys
def my_command( data, x='center', y='auto', width=None, height=None):

    args = {"some_args_used_in_renders": "auto_conf"}

    command_out = {'type': 'svg', 'content': data,
                    'args': args, "render": myrender_command,
                    'positionner': positionner(x, y, width, height)}

    #Add command_out dictionary to the document data and return the positionner
    return add_to_slide( command_out )

#Render should output 1 variables:
#the svgpart (as text)
def myrender_command( content ):

    #content will get the command_out dictionnary

    #Now you have to translate datatin into svg syntax (or html, if args['type'] == 'html')
    svgout = "<g> My svg output %s </g>"%content['content']
    width = my_svg_width
    height = my_svg_height

    #You need to update the size of your element in order to place it correctly
    content['positionner'].update_size( width=width, height=height )

    return svgout

```

Then you can test your module by importing your python file

```python
from beampy import *

from my_module import *

doc = document()

slide()
title('My module')
my_command("data needed by my module")

save('test.html')
```
