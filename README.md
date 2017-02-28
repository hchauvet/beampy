# Beampy

Beampy is in early stage development!

Beampy is a python tool to create slide-show in svg that can be displayed with HTML5
(tested on Firefox and Chromium)
The size of slides is fixed, like in a Latex Beamer document.

Beampy presentation output only one html file with every contents embedded.

[See a Beampy tests presentation](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html) (source is in *examples/beampy_tests_modules.py*)

## TODO:
* A clear documentation

## Curent version:

### 0.4.3

* Matplotlib figures can now be directly passed to *figure()* or a list of matplotlib figures can be animated with *animatesvg()*
* Minor improvement in cache size (content is no more stored in cache file)
* Update of scour version (svg-optimiser) 

### 0.4.2
* Glyph paths from Latex are now unique (this reduce the number of svg lines in documents)
* Add *svg* command ton include raw svg in slide
* Improve the theme flexibility, a background with interactive elements can now be created!

### 0.4.1
* All slide are now loaded into ram, improve speed
* Modules are now classes which inherit from a base class "beampy_module" in modules/core.py
* cache is now unique for all format (pdf, svg, html) and special keys can be added
  to modules in order to create their chache id

## Introduction

Beampy is in between Latex beamer and html5 slide-show libraries.
It creates slides in svg format (with a bit of HTML5 for video and interactive
things like Bokeh plots).

Slide can contains:
- Vector graphics (svg, pdf)

- Raster images (png, jpeg)

- Raster videos (using webm or mp4 format)

- Animated vectorial graphics (list of svg figures)

- bokeh plots (experimental)

- Texts are rendered using Latex (then translated to svg, as vector paths)

- Tikz/PGF figure and graphics

- Inline svg commands. 

Svg slides are exported in html5 with every raster elements embed in one file.
The slides can also be exported to svg and pdf (videos and animations are rendered as first frame image in pdf/Svg)

Beampy uses a simple cache system to compile slide only when it's needed!
## A quick example :

```python
from beampy import *

doc = document()

with slide():
   maketitle('Beampy a tool to make simple presentation', ['Hugo Chauvet'] )

with slide():
   title("Beampy test")
   text("""Use LaTeX to render text and $$\\sqrt{10}$$""", align='center')

save('./beampy_presentation.html')

#To save in pdf just change the above command to the following
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

### From pip

You can use python pip to install beampy.
```bash
pip install -e git+https://github.com/hchauvet/beampy.git#egg=beampy
```

You can also use python vitual environements to install beampy and all the dependencies
in a contained space:
[http://docs.python-guide.org/en/latest/dev/virtualenvs/](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

####Optionals packages to install with pip
for code coloration *pygments*:
```bash
pip install pygments
```

for bokeh figures *bokeh*:
```bash
pip install bokeh
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

For that:

```python
from beampy import *

doc = document()

#To let Bempy search automatically for a program replace
#the path by "auto" (check the default_theme.py file)

doc._theme['document']['external_app'] = {
"inkscape": "/path/to/inkscape",
"dvisvgm": "/path/to/dvisvgm",
"pdfjoin": "/path/to/pdfjoin",
"video_encoder": '/path/to/ffmpeg [or avconv]',
"pdf2svg": "/path/to/pdf2svg"
}
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

with slide('Svg animation'):
    animatesvg("./svg_anims/", width="500")

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#3)

### Using Matplotlib 

```python
from beampy import *
import pylab as p

doc = document()

with slide("Matplotlib figure"):
    fig = p.figure()
    x = p.linspace(0,2*p.pi)
    
    p.plot(x, p.sin(x), '--')
    
    figure(fig)


with slide("Mpl animation"):

    anim_figs = []
    for i in range(20):
        fig = p.figure()   
        x =  p.linspace(0,2*p.pi)
        p.plot(x, p.sin(x+i))
        p.plot(x, p.sin(x+i+p.pi))
        p.close(fig) 
        anim_figs += [ fig ]
        
        
    animatesvg( anim_figs )
     

save("test_figures.html")
```

[Figure Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#4)
[Animation Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#5)

###Video

```python
from beampy import *
doc = document()

with slide('Video'):
    video("./test.webm", width=500, height=294)

save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#6)

###Group and columns

```python
from beampy import *
doc = document()

with slide('Group and columns'):
    colwidth=350
    with group(width=colwidth, height=doc._height-100, x="1cm", y="1.8cm", background="#000"):
	text("""This is a test for a long text in a column style.
	$$ \sum_{i=0}^{10} x_i $$
	""", align="center", width=colwidth-20, color="#ffffff")


save('test.html')
```

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#7)

###Relative positioning

#### Relative to a given element in the presentation
```python
from beampy import *
doc = document()

with slide("Using element's anchors"):
    e0 = text('central element [e0]', y=0.2)
    e1 = text('left of e0', y=e0.top+0, x=e0.left-{'shift': 0.1, 'align':'right'})
    e2 = text('right of e0', y=e0.top+0, x=e0.right+0.1)
    e4 = text('anchors available: top, bottom, center, right, left',
              y=e0.bottom+'1cm', x=e0.center+{'shift':0, 'align':'middle'})

#You can create shortcuts for relative centering or relative right
#you also have the "top" and "bottom" for the "align" key of the new element
def ecenter( shift = 0 ):
    return {"shift":shift, "align": 'middle'}

def eright( shift = 0 ):
    return {"shift":shift, "align": 'right'}

with slide("Using element's anchors 2"):
    e0 = text('central element [e0]', y=0.2)
    e1 = text('left of e0', y=e0.top+0, x=e0.left-eright(0.1))
    e2 = text('right of e0', y=e0.top+0, x=e0.right+0.1)
    e4 = text('anchors available: top, bottom, center, right, left',
              y=e0.bottom+'1cm', x=e0.center+ecenter())

save('test.html')
```
[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#9)

#### Relative to the previous element
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

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#8)


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
[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#10)

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

[Result](https://cdn.rawgit.com/hchauvet/beampy/master/examples/beampy_tests.html#11)

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
arrow("400px", "400px", 40, 40, bend='left')

save('test.html')
```

## Change theme

Basic theme features are store in a dictionary *document._theme*. You can check
the default features in [/beampy/statics/default_theme.py]. You can adapt this dictionary
to fit your needs.

To create personal themes you can place your theme inside beampy/themes/
(check available examples inside this folder to create your theme files)

The name of your theme file should end-up with the suffix *_theme.py*.
Then you can load them in your presentation as follow:

```python
from beampy import *

#for a file named mytheme_theme.py in beampy/themes folder
doc = document(theme='mytheme')
```

You can also change theme dictionnary directly in your presentation file

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

Check files in *./beampy/modules/* folder. Especially check the "beampy_module" class in
file beampy/modules/core.py 

A module is a class that inherit from beampy_module class 

The base of a module file
```python
from beampy.modules.core import beampy_module


class my_module(beampy_module):

    def __init__(self, content, your_args, **kwargs): 
        #Args need to be defined in the theme file (default_theme in static folder)
        #in the theme file the key should have the same name of the module 
        #to document._data list with 'type', 'content', 'args' and 'render' keys
        
        self.type = 'svg' #or 'html' 

        #Add the extra args defined in the theme
        self.check_args_from_theme(kwargs)
        
        #Add locally defined arg 
        self.your_args = your_args
        self.args['your_args'] = your_args
        
        #Register the content
        self.content = content
        
        #Register your module 
        self.register()
        
        
    
    def render( self ):
        #You have to define this function to transform your content to svg or html

        #Now you have to translate datatin into svg syntax (or html, if args['type'] == 'html')
        svgout = "<g> My svg output %s </g>"%self.content
        width = my_svg_width
        height = my_svg_height

        #You need to update the size of your element in order to place it correctly
        self.update_size(width, height)

        #For an svg you need to update the svgout variable
        self.svgout = svgout
        #For html
        #self.htmlout = ""

```

Then you can test your module by importing your python file

```python
from beampy import *

from my_module import *

doc = document()

slide()
title('My module')
my_module("data needed by my module")

save('test.html')
```
