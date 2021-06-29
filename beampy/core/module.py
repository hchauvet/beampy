#!/usr/bin/env python3

"""
Base class for beampy modules
"""
from beampy.core.document import document
from beampy.core.functions import (gcs, create_element_id,
                                   get_command_line, print_function_args,
                                   pre_cache_svg_image)
from beampy.core.geometry import positionner

import sys
import inspect
import logging
_log = logging.getLogger(__name__)


class beampy_module(object):
    """
        Base class for creating a module

        Each module need a render method and need to return a register
    """

    rendered = False  # State of the module (True if it has been rendered to an svg
    positionner = None  # Store the positionner (to manage placement in slide)
    content = None  # Store the input content
    type = None  # Define the type of the module
    name = None
    args = {}  # Store the raw dict of passed args (see check_args_from_theme)

    # Storage of render outputs
    svgout = None  # The output of the render
    htmlout = None  # We can store also html peace of code
    jsout = None  # Store javascript if needed
    animout = None  # Store multiple rasters for animation

    call_cmd = ''  # Store the command used in the source script
    call_lines = ''  # Store lines of the call cmd
    id = None  # store an id for this module
    uid = None  # store an unique id for the module using python id() function
    group_id = None  # store the group id if the module is inside one group
    start_line = 0
    stop_line = 0

    # Needed args (give some default one)
    x = 0
    y = 0
    width = None
    height = None
    svg_decoration = '' # strore an svg element to add to the elemen group like a rectangle

    #  Special args used to create cache id from md5
    args_for_cache_id = None

    # Define special keyword arguments not included in THEME file
    special_kwargs = {'parent_slide_id': None}

    # Do cache for this element or not
    cache = True

    # Save the id of the current slide for the module
    slide_id = None

    # Store svg definitions like FILTERS or ClipPAth see self.add_svgdef method
    svgdefs = []
    svgdefsargs = []

    def __init__(self, **kargs):

        self.check_args_from_theme(kargs)
        self.register()
        print("Base class for a new module")

    def register(self, auto_render=False):
        # Function to register the module (run the function add to slide)

        # Load the special_kwargs to set them as attribute of the module
        self.load_special_kwargs()

        # Save the id of the current slide for the module
        if self.parent_slide_id is None:
            self.slide_id = gcs()
        else:
            self.slide_id = self.parent_slide_id

        # Store the list of groups id where the module is finally located (used for html element to
        # resolve final positionning)
        self.groups_id = []

        # Ajout du nom du module
        self.name = self.get_name()


        # Create a unique id for this element
        self.id = create_element_id( self )

        _log.debug('%s(id=%s) store the slide id: %s' % (self.name, self.id, self.slide_id))

        # Store the layers where this module should be printed
        self.layers = [0]
        # Store a boolean to know if this module has been exported to slide store
        self.exported = False

        # Store svg definitions like FILTERS or ClipPAth see self.add_svgdef method
        self.svgdefs = []
        self.out_svgdefs = None
        self.svgdefsargs = []

        # Add module to his slide
        document._slides[self.slide_id].add_module(self.id, self)

        self.positionner = positionner(self.x, self.y ,
                                       self.width, self.height,
                                       self.id, self.slide_id)

        # Add anchors for relative positionning
        self.top = self.positionner.top
        self.bottom = self.positionner.bottom
        self.left = self.positionner.left
        self.right = self.positionner.right
        self.center = self.positionner.center

        # Report width, height from positionner to self.width, self.height
        # Always use the update_size method
        self.update_size(self.width, self.height)

        # Add the source of the script that run this module
        try:
            start, stop, source = get_command_line(self.name)
        except Exception as e:
            _log.debug('Error to get command line')
            _log.debug(e)
            start = 0
            stop = 0
            source = 'None'

        self.call_cmd = source
        self.call_lines = (start, stop)

        # Do we need to auto render elements
        if auto_render:
            if not self.rendered:
                self.pre_render()
                self.run_render()

                # At the end of the render, width and height should be fixed !
                assert self.width.value is not None
                assert self.height.value is not None

    def delete(self):
        # Remove from document
        document._slides[self.slide_id].remove_module(self.id)
        del self

    def reset_outputs(self):
        self.svgout = None  # The output of the render
        self.htmlout = None  # We can store also html peace of code
        self.jsout = None  # Store javascript if needed
        self.animout = None  # Store multiple rasters for animation
        self.rendered = False
        self.exported = False

    def pre_render(self):
        """
        A method that is called at the begining of the slide.newrender method
        """
        pass

    def render(self):
        # Define the render for this module (how it is translated to an svg (or html element))
        # If the width/height changes ... update them!
        # self.update_size(new_width, new_height)

        # Store your the render outputs to
        self.svgout = None
        self.htmlout = None
        self.jsout = None
        self.animout = None

        self.rendered = True

    def run_render(self):
        """
            Run the function self.render if the module is not in cache
        """

        # Get the current slide object
        slide = document._slides[self.slide_id]
        _log.debug("Render %s(id=%s): with height: %s and width: %s on slide: %s" % (self.name,
                                                                                     self.id,
                                                                                     self.height,
                                                                                     self.width,
                                                                                     slide.num))

        if self.cache and document._cache is not None:
            ct_cache = document._cache.is_cached('slide_%i'%slide.num, self)
            if ct_cache:
                #Update the state of the module to rendered
                self.rendered = True
                try:
                    print("Elem [%s ...] from cache"%self.call_cmd.strip()[:20])
                except:
                    print("Elem %s from cache"%self.name)
            else:
                #print("element %i not cached"%ct['positionner'].id)
                if not self.rendered:
                    self.render()
                    _log.debug('Add %s(id=%s) cache for slide_id: %s' % (self.name, self.id, slide.num))
                    document._cache.add_to_cache('slide_%i'%slide.num, self)
                    try:
                        print("Elem [%s ...] rendered"%self.call_cmd.strip()[:20])
                    except:
                        print("Elem %s rendered"%self.name)
        else:
            if not self.rendered:
                self.render()
                try:
                    print("Elem [%s ...] rendered"%self.call_cmd.strip()[:20])
                except:
                    print("Elem %s rendered"%self.name)

        # Process the svg definitions
        self.render_svgdefs()

    def get_name(self):
        # Return the name of the module
        # return str(self.__init__.im_class).split('.')[-1]
        name = str(self.__init__.__self__.__class__).split('.')[-1]

        # For python 3.x compatibility
        if "'>" in name:
            name = name.replace("'>", '')

        return name

    def check_args_from_theme(self, arg_values_dict, parent=None,
                              lenient=False):
        """
        Function to check input function keyword args.

        Functions args are defined in the default_theme.py or if a
        theme is added the new value is taken rather than the
        default one.

        Parameters
        ----------
        arg_values_dict: dictionary,
            The key-value dictionary containing function arguments.

        parent: string optional
            The name of the parent beampy_module to also load args

        lenient: boolean optional
            When True, allows check function to not stop Beampy
            compilation when the argument is not defined in the THEME
            dictionary (default value is False)
        """

        # Add args value to the module
        self.args = arg_values_dict

        function_name = self.get_name()
        default_dict = document._theme[function_name]
        # Merge default dictionary with the parent dictionary
        if parent is not None:
            default_dict = dict(default_dict, **document._theme[parent])

        outdict = {}
        for key, value in arg_values_dict.items():
            #Check if this arguments exist for this function
            if key in default_dict or key in self.special_kwargs:
                outdict[key] = value
                setattr(self, key, value)
            else:
                if not lenient:
                    print("Error the key %s is not defined for %s module"%(key, function_name))
                    print_function_args(function_name)
                    sys.exit(1)
                else:
                    _log.debug('Your argument %s is not defined in the Theme' % (key))

        # Check if their is ommited arguments that need to be loaded by default
        for key, value in default_dict.items():
            if key not in outdict:
                setattr(self, key, value)

    def load_special_kwargs(self):
        """

        Load all attributes contained in self.sepcial_kwargs
        dictionnary as attributes of the beampy_module with the
        setattr function.

        """

        # Check if their is ommited arguments from the special_kwargs
        for key, value in self.special_kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def load_extra_args(self, theme_key):
        """
        Function to load default args from the theme for the given theme_key
        and add them to the module
        """

        for key, value in document._theme[theme_key].items():
            if not hasattr(self, key):
                setattr(self, key, value)

                #Add args to the args dictionnary also
                self.args[key] = value

    def load_args(self, kwargs_dict):
        """
            Function to transform input kwargs dict into attribute of the module
        """

        for key, value in kwargs_dict.items():
            setattr(self, key, value)

    def update_size(self, width, height):
        """
            Update the size (width, height) of the current module
        """

        self.positionner.update_size( width, height )
        self.width = self.positionner.width
        self.height = self.positionner.height

    def add_svgdef(self, svgdef, svgdefsargs=None):
        """
        Function to add svg clipPath or filter.

        Parameters:
        -----------

        svgdef: string,
            The svg syntax to add to <defs> environnement. This svg
            syntax could include arguments as python string format
            replacement (like '{width}') that will be replaced by
            their value (store as instance of the class, like
            self.width for '{width}') when render is executed.

        svgdefargs: list of string optional
            The list of arguments as string to format in the svgdef.
        """

        if svgdefsargs is None:
            svgdefsargs = []

        assert isinstance(svgdefsargs, list)

        self.svgdefs += [svgdef]
        self.svgdefsargs += [svgdefsargs]

    def render_svgdefs(self):
        """
        Function to render the svgdefs
        """
        out_svgdefs = ''
        if len(self.svgdefs) > 0:

            logging.debug('Export svg defs added to module %s' % str(self.name))
            # print('Svgdefs type for ', str(self.name))
            for i, svgdef in enumerate(self.svgdefs):
                # print(type(svgdef))
                out_args = {}
                for args in self.svgdefsargs[i]:
                    out_args[args] = getattr(self, args)

                if out_args != {}:
                    svgdef = svgdef.format(**out_args)

                out_svgdefs += svgdef

            logging.debug(out_svgdefs)

        if out_svgdefs != '':
            document._slides[self.slide_id].svgdefout += [out_svgdefs]

        self.out_svgdefs = out_svgdefs

    def __repr__(self):
        out = 'module: %s\n'%self.name
        try:
            out += 'source (lines %i->%i):\n%s\n'%(self.call_lines[0], self.call_lines[1],
                                       self.call_cmd)
        except:
            out += 'source : fail\n'

        out += 'width: %s, height: %s\n'%(str(self.width.value), str(self.height.value))

        return out

    # Export methods (how the final svg/html/multisvg is written down)
    # add a group/div object with the good x, y, positions
    def export_svg(self):
        """
            function to export rendered svg in a group positionned in the slide
        """

        out = '<g transform="translate(%s,%s)" class="%s">' % (self.positionner.x['final'],
                                                    self.positionner.y['final'], self.name)

        out += self.svgout

        if document._text_box:
            out +="""<rect x="0"  y="0" width="%s" height="%s"
            style="stroke:#009900;stroke-width: 1;stroke-dasharray: 10 5;
            fill: none;" />""" % (self.positionner.width.value,
                                  self.positionner.height.value)

        if self.svg_decoration != '':
            out += self.svg_decoration.format(width=self.positionner.width.value,
                                              height=self.positionner.height.value)

        out += '</g>'

        return out

    def export_svg_def(self):
        """
            function to export rendered svg in a group positionned in the slide
        """

        # Todo: add data- to element like data-python="self.call_cmd.strip()"
        out = '<g id="%s" transform="translate(%s,%s)" class="%s" >' % (self.id,
                                                                        self.positionner.x['final'],
                                                                        self.positionner.y['final'],
                                                                        self.name)

        out += self.svgout

        if document._text_box:
            out +="""<rect x="0"  y="0" width="%s" height="%s"
            style="stroke:#009900;stroke-width: 1;stroke-dasharray: 10 5;
            fill: none;" />""" % (self.positionner.width.value,
                                  self.positionner.height.value)

        if self.svg_decoration != '':
            out += self.svg_decoration.format(width=self.positionner.width.value,
                                              height=self.positionner.height.value)

        out += '</g>'

        logging.debug(str(self.name), type(out))

        return out

    def export_html(self):

        out = """<div style="visibility: hidden; position: absolute; left: %spx; top: %spx;"> %s </div></br>"""
        out = out%(self.positionner.x['final'], self.positionner.y['final'], self.htmlout)

        return out

    def export_animation(self):
        # Export animation of list of svg
        if isinstance(self.animout, list):
            # print(self.slide_id, slide.cpt_anim)
            # Pre cache raster images
            frames_svg_cleaned, all_images = pre_cache_svg_image( self.animout )

            # Add an animation to animout dict
            animout = {}
            animout['header'] = "%s"%(''.join(all_images))
            animout['config'] = { 'autoplay':self.autoplay, 'fps': self.fps }
            animout['anim_num'] = self.anim_num
            animout['frames'] = frames_svg_cleaned

            return animout

    def export_animation_layer(self, layer):
        out = '<g id="svganimate_{slide}-{layer}_{id_anim}"' \
              ' transform="translate({x},{y})" onclick="Beampy.animatesvg({id_anim},{fps},{anim_size});"' \
              ' data-slide={slide} data-anim={id_anim} data-fps={fps} data-lenght={anim_size}>{frame_init}</g>'\

        out = out.format(slide=self.slide_id, layer=layer, id_anim=self.anim_num, x=self.positionner.x['final'],
                         y = self.positionner.y['final'], fps=self.fps, anim_size=len(self.animout),
                         frame_init=self.animout[0])
        return out

    def add_border(self, svg_style={'stroke':'red', 'fill':'none', 'stroke-width': 0.5}):
        """
            function to add a border to the given element
        """

        output = '<rect x="0" y="0" width="{width}" height="{height}" '
        for key in svg_style:
            output += '%s="%s" '%(key, svg_style[key])

        output += ' />'

        self.svg_decoration = output

    def add_layers(self, layerslist):
        """
        Function to add this elements to given layers
        :param layerslist: list of layers where the module should be printed
        :return:
        """
        logging.debug('layer list %s' % str(layerslist))
        self.layers = layerslist

    def __call__(self, *args, **kwargs):
        # Todo: regegister the module where it is called (use it to recall a module in another slide)
        raise NotImplementedError("Not implemented, you can call a module twice!")

    def __getitem__(self, item):
        """
        Manage layer of a given module using the python getitem syntax
        with slicing

        self()[0] -> layer(0)
        self()[:1] -> layer(0,1)
        self()[1:3] -> layer(1,2,3)
        self()[2:] -> layer(2,..,max(layer))
        """

        if isinstance(item, slice):
            # print(item.start, item.stop, item.step)
            if item.step is None:
                step = 1
            else:
                step = item.step

            if item.start is None:
                start = 0
            else:
                start = item.start

                if start < 0:
                    start = 'max%i'%start

            if item.stop is None or item.stop > 100000:
                stop = 'max'
            else:
                stop = item.stop

                if stop < 0:
                    stop = 'max%i'%stop

            # print(start, stop, step)
            if isinstance(stop, str):
                if isinstance(start, str):
                    self.add_layers('range(%s,max,%i)' % (start, step))
                else:
                    self.add_layers( 'range(%i,max,%i)'%(start, step) )

            else:
                if isinstance(start, str):
                    self.add_layers('range(%s,%i,%i)'%(start, stop+1, step))
                else:
                    self.add_layers(list(range(start, item.stop+1, step)))

        else:
            if isinstance(item, list) or isinstance(item, tuple):
                string_layers = False
                item = list(item)
                for i, it in enumerate(item):
                    if it < 0:
                        item[i] = 'max%i+1'%it
                        string_layers = True

                    if isinstance(it, str):
                        string_layers = True

                if string_layers:
                    # Need to replace ' by None because str([0,'max']) -> "[0,'max']"
                    self.add_layers(str(item).replace("'",""))
                else:
                    self.add_layers(item)

            else:
                if item < 0:
                    item = 'max%i+1'%item

                if isinstance(item, str):
                    self.add_layers('[%s]'%item)
                else:
                    self.add_layers([item])

        return self

    def __len__(self):
        # Need a len of 0 to manager layer [:-1] should return -1
        return 0

    def __enter__(self):
        """
        Implement __enter__ __exit__ to pass the string input of
        the function as comment inside a "with" statement to an input
        of the function via the "process_with" method


        with beampy_module():
            '''
            This text will be stored in the self.input
            '''

            "this one also"
        """

        # Get the line in the source code of the group
        previous_frame = inspect.currentframe().f_back
        traceback = inspect.getframeinfo(previous_frame)
        self.start_line = traceback.lineno

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        previous_frame = inspect.currentframe().f_back
        traceback = inspect.getframeinfo(previous_frame)
        self.stop_line = traceback.lineno
        self.process_with()

    def process_with(self):
        """
        Function called by the __exit__ function

        Need to be redefined by each module to adjust the behaviours
        of "with :"
        """
        raise NotImplementedError("With statement not implemented for this module")

    def above(self, other_element):
        """
        Set the current module to appears above the other_element_id.
        """
        assert isinstance(other_element, beampy_module)

        if self.type == 'group':
            pid = self.parentid
        else:
            pid = self.group_id

        curgroup = document._slides[self.slide_id].contents[pid]
        other_pos = curgroup.exports_id.index(other_element.id)
        self_pos = curgroup.exports_id.index(self.id)

        #remove the id of the current module
        curgroup.exports_id.pop(self_pos)
        #add the current module to it's new place (above the other)
        curgroup.exports_id.insert(other_pos+1, self.id)

    def below(self, other_element):
        """
        Set the current module to appears beow the othe_element
        """
        assert isinstance(other_element, beampy_module)

        if self.type == 'group':
            pid = self.parentid
        else:
            pid = self.group_id

        curgroup = document._slides[self.slide_id].contents[pid]
        other_pos = curgroup.exports_id.index(other_element.id)
        self_pos = curgroup.exports_id.index(self.id)

        #remove the id of the current module
        curgroup.exports_id.pop(self_pos)
        #add the current module to it's new place (below the other)
        curgroup.exports_id.insert(other_pos, self.id)

    def first(self):
        """
        Set the current object in the background
        """
        if self.type == 'group':
            pid = self.parentid
        else:
            pid = self.group_id

        curgroup = document._slides[self.slide_id].contents[pid]
        self_pos = curgroup.exports_id.index(self.id)

        #remove the id of the current module
        curgroup.exports_id.pop(self_pos)
        #add the current module at the beginning
        curgroup.exports_id.insert(0, self.id)

    def last(self):
        """
        Set the current object in the foreground
        """
        if self.type == 'group':
            pid = self.parentid
        else:
            pid = self.group_id

        curgroup = document._slides[self.slide_id].contents[pid]
        self_pos = curgroup.exports_id.index(self.id)

        #remove the id of the current module
        curgroup.exports_id.pop(self_pos)
        #add the current module at the end
        curgroup.exports_id.insert(len(curgroup.exports_id), self.id)
