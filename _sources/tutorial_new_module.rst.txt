.. _tutorial_new_module:

New Beampy module
=================

.. warning::
   This tutorial is a Draft! And provide minimum informations to intrepid developers.

Check files in **./beampy/modules/** folder. Especially check the
"beampy_module" class in file **beampy/modules/core.py**

A Beampy module is a class that inherit from beampy_module class.


Base module source code
-----------------------


.. code-block:: python

   from beampy.modules.core import beampy_module


   class my_module(beampy_module):

       def __init__(self, content, your_args, **kwargs):
       
            # Args need to be defined in the theme file (default_theme in static folder)
            # in the theme file the key should have the same name of the module 
            # to document._data list with 'type', 'content', 'args' and 'render' keys
            
            self.type = 'svg' # or 'html' 
       
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
            # You have to define this function to transform your content to svg or html
       
            # Now you have to translate datatin into svg syntax (or html, if args['type'] == 'html')
            svgout = "<g> My svg output %s </g>"%self.content
            width = my_svg_width
            height = my_svg_height
       
            # You need to update the size of your element in order to place it correctly
            self.update_size(width, height)
       
            # For an svg you need to update the svgout variable
            self.svgout = svgout
       
            # For html
            # self.htmlout = ""
       
            self.rendered = True # Turn the rendered flag to true for cache system

Test your module
----------------

.. code-block:: python

   from beampy import *

   from my_module import *

   doc = document()

   with slide('Test my new module'):
       my_module("data needed by my module")

   save('test.html')


