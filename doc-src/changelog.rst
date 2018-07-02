.. _changelog:

Change-log
==========

0.5.0
-----

* Add box function to decorate group
* New experimental way to write text inside presentation using context manager

  .. code-block:: python
		  
     with text(width=400):
         """
	 Any comment inside the context manager will be passed to the
	 text function as input argument. This allows clearer source
	 when writing long texts.

	 No more need to add an *r* before to protect the text passed to
	 latex, it's now automatically added.
	 """
	 
* Correct bug when only html object are present in one slide
* Correct small typos in the install section of the documentation.

0.4.9
-----

* Add documentation in Beampy module
* Add 'anchor' key to position dictionary to define anchor along the
  bounding-box of module to place them.
* Add utils.py to store functions that call beampy modules. 
* Add function **bounding_box(module)** to utils.py to draw bounding box with
  anchors around Beampy modules. Add also a function to draw axes on slide,
  **draw_axes()**

0.4.8
-----

* Partially fix issue #12.
* Clean code syntaxe. 

0.4.7
-----

* Introduce layer mechanism. Slide elements can be animated by layers allowing mechanism like beamer "\only".
  The layer are managed as python slicing on Beampy modules.

  .. code-block:: python

     with slide('Test layers'):
         text('First printed on layer 0')
         text('Secondly printed on layer 1')[1]
         text('Printed from layer 2 to 3')[2,3]
         text('Printed on all layers')[:]
         text('Printed on layer 4')[4]
    
     with group(width=300)[2:]:
         text('Printed inside group')
         text('for layers 2 to end')

0.4.6
-----

* The core of Beampy slide processor has been rewritten and now allows recursive group of elements.

  .. code-block:: python

     with group():
        text('toto')
        with group(width=300):
            text('tata')

     with group(width=200):
        figure('./niceplot.pdf')
        text('nice legend')


* If a group width is given all elements in groups without specified width take the width of the group

  .. code-block:: python

     with group(width=200):
         figure('./niceplot.pdf')
         text('nice legend')
         # Figure and text width will be automatically set to 200 px


* Relative placement now could be done on auto positioned elements

  .. code-block:: python

     t0 = text('toto')
     text('tata', x=t0.center + center(0), t0.bottom + 0.1)


* Video now could use external links (with *embedded=True*) rather than be included in the html file.
  The video is loaded from disk (be careful with file path) when the slide is displayed on screen.

0.4.5
-----

* All texts are preprocessed in a single latex file (Latex is called only once: improve compilation time)
* Cache bug fix: Video and svg are now cached correctly

0.4.4
-----

* Improve cache: one file per element cached (don't write the cache twice!)
* Svg: Add line and rectangle commands to easily draw lines and rectangles
* Relative placement: add shortcut center(shift), right(shift) and bottom(shift) 
  to change the anchor of the current element.
  
  .. code-block:: python

    e1 = text('Somthing', x=0.2, y=0.4)
    e2 = text('An other thing', 
              x=e1.left + right(0.1), 
              y=e1.center + center(0))



0.4.3
-----

* Matplotlib figures can now be directly passed to *figure()* or a list of matplotlib figures can be animated with *animatesvg()*
* Minor improvement in cache size (content is no more stored in cache file)
* Update of scour version (svg-optimiser) 

0.4.2
-----

* Glyph paths from Latex are now unique (this reduce the number of svg lines in documents)
* Add *svg* command ton include raw svg in slide
* Improve the theme flexibility, a background with interactive elements can now be created!

0.4.1
-----

* All slide are now loaded into ram, improve speed
* Modules are now classes which inherit from a base class "beampy_module" in modules/core.py
* cache is now unique for all format (pdf, svg, html) and special keys can be added
  to modules in order to create their chache id
