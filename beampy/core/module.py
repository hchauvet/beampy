#!/usr/bin/env python3

"""
Base class for beampy-sldieshow modules
"""
from beampy.core.document import document
from beampy.core.store import Store
from beampy.core.content import Content
from beampy.core.functions import (get_command_line, print_function_args,
                                   pre_cache_svg_image, convert_unit)
from beampy.core.geometry import Position, Length, relative_length

from copy import deepcopy
import inspect
import logging
_log = logging.getLogger(__name__)


class beampy_module():
    """Base class for creating a module. All beampy modules are a subclass of
    this class.
    """

    args = {}  # Store the raw dict of passed args (see check_args_from_theme)

    call_cmd = ''  # Store the command used in the source script
    call_lines = ''  # Store lines of the call cmd
    id = None  # store an id for this module
    uid = None  # store an unique id for the module using python id() function
    group_id = None  # store the group id if the module is inside one group
    start_line = 0
    stop_line = 0

    #  Special args used to create cache id from md5
    args_for_cache_id = None

    # Do cache for this element or not
    cache = True

    # Save the id of the current slide for the module
    slide_id = None

    # Store svg definitions like FILTERS or ClipPAth see self.add_svgdef method
    svgdefs = []
    svgdefsargs = []

    def __init__(self, x, y, width, height, margin, content_type='svg', **kwargs):
        """Beampy module is the base class for each elements added to slide or group in
        Beampy-slideshow. Modules create a Content (with a given size)
        registered to the Store. A unique ID is created for the Content and
        added to the module class with a position. The module is added to the
        slide it belongs.
        Module define a render method to transform the Content object to svg
        (only if the module is not cached).

        Parameters
        ----------

        x : int or float or {'center', 'auto'} or str
            Horizontal position for the text container. See positioning system
            of Beampy.

        y : int or float or {'center', 'auto'} or str
            Vertical position for the text container. See positioning system of
            Beampy.

        width : int or float or None
            Width of the module. If None, the width will be set when module is
            rendered to svg.

        height : int or float or None
            Height of the module. If None, the width will be set when module is
            rendered to svg.

        margin : number or string or list ([vertical, horizontal] or [top,
            right, bottom, left]), Add margin around the module. If margin is a
            number or a string it applies on all border of the module. If a list
            of size 2 is given, it contains the vertical (top = bottom =
            vertical) and the horizontal (left = right = horizontal)
            margins. Each element of list or single number is converted to a
            Length object so that length could be given as a string with unit or
            % of the current size.

        content_type : str in ['svg', 'html', 'js']
            The type of the content

        **kwargs, any key=value list:
            will be added to the class variables to use them in the render for
            exemple.

        """

        self.register()

        # Store the layers where this module should be printed
        self.layers = [0]

        # Store a boolean to know if this module has been exported to slide store
        self.exported = False

        # Store svg definitions like FILTERS or ClipPAth see self.add_svgdef method
        self.svgdefs = []
        self.out_svgdefs = None
        self.svgdefsargs = []

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.margin = margin
        self._final_x = None
        self._final_y = None
        self.type = content_type

        # Variables that will store output of render functions
        self.svgout = ''  # The svg template to produce the final valid svg string
        self.htmlout = ''  # The html template
        self.jsout = ''  # The javascript template to produce the valid javascrpit output
        self.animout = ''  # Store multiple rasters for animation

        # Add kwards as variable of the class
        self.set(**kwargs)

    def register(self):
        # Function to register the module (run the function add to slide)

        # Store the list of groups id where the module is finally located (used for html element to
        # resolve final positionning)
        self.groups_id = []

        # Ajout du nom du module
        self.name = self.get_name()

        # Add the id of the current slide for the module
        self.set_slide_id()

        # Add module to his slide or to the current group
        if self.slide_id is not None:
            if Store.isgroup():
                Store.group().add_module(self)
            else:
                Store.get_slide(self.slide_id).add_module(self)
            sid = self.slide_id
            self.id = self.get_index()
        else:
            if Store.isgroup():
                Store.group().add_module(self)
            sid = None
            self.id = None

        _log.debug('%s(id=%s) store the slide id: %s' % (self.name, self.id, self.slide_id))

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

    def set_slide_id(self):
        """Method to check if the current slide is defined in the store and to
        set the id of this slide to self.slide_id attribute.
        """

        if Store.get_current_slide_id() is not None:
            self.slide_id = Store.get_current_slide_id()
        else:
            _log.debug('No slide id for this module')
            self.slide_id = None

    def add_content(self, content, content_type):
        """Add the content to this module.

        Parameters:
        -----------

        content: str,
            The content to be added, that will be used by the parser

        content_type:
        """
        # Create a content
        self._content = Content(content, content_type,
                                self.width.value,
                                self.height.value,
                                self.name,
                                self.args_for_cache_id)

        if Store.is_content(self._content.id):
            print(f'This module {self.signature} already exist in the Store, I will use {self.content_id}' )
            self._content.load_from_store()
        else:
            # Check if the module is cached
            if self._content.is_cached:
                # Load from cache
                self._content.load_from_cache()
            else:
                # Render the module
                self.pre_render()
                self.run_render()
                # Add content to cache
                self._content.add_to_cache()

    def update_signature(self, *args, **kwargs):
        """Create a unique signature of the init method using inspect module.
        This would be usefull to cache the module
        """
        if not hasattr(self, '_signature'):
            self._signature = inspect.signature(self.__init__)

        self._arguments = self._signature.bind(*args, **kwargs)

    @property
    def signature(self):
        if not hasattr(self, '_arguments'):
            args = inspect.signature(self.__init__).bind()
        else:
            args = self._arguments

        args.apply_defaults()
        argsout = []
        for k in args.arguments:
            # Remove args useless for caching like x and y
            if k not in ['x', 'y']:
                argsout += [f'{str(k)}={args.arguments[k]}']

        return f'{self.name}({", ".join(argsout)})'

    @property
    def content_id(self):
        return self._content.id

    @property
    def data(self):
        """The raw data of the content of the module
        """
        if self._content is not None:
            return self._content.data

        return None

    @data.setter
    def data(self, raw_content):
        """Set the raw data of the module. This method should be used from
        self.render.
        """
        self._content.data = raw_content

    @property
    def margin(self):
        """Get the margin process each length
        """
        out_margin = [0, 0, 0, 0]
        if hasattr(self, '_margin') and isinstance(self._margin, list):
            out_margin = [self._margin[0].value,
                          self._margin[1].value,
                          self._margin[2].value,
                          self._margin[3].value]

        return out_margin

    @margin.setter
    def margin(self, new_margin):
        """Check type of given margin and convert each of element to Length
        objects.
        """
        if isinstance(new_margin, (str, float, int)):
            self._margin = [Length(new_margin, 'y'), Length(new_margin, 'x')] * 2
        elif isinstance(new_margin, (list, tuple)):
            if len(new_margin) == 2:
                self._margin = [Length(new_margin[0], 'y'),
                                Length(new_margin[1], 'x')] * 2
            if len(new_margin) == 4:
                self._margin = [Length(new_margin[0], 'y'),
                                Length(new_margin[1], 'x'),
                                Length(new_margin[3], 'y'),
                                Length(new_margin[4], 'x')]
            else:
                raise TypeError("The size of margin list should be 2 or 4, not %s" % len(new_margin))
        elif new_margin is None:
            # This allow theme set of the margin
            self._margin = None
        else:
            raise TypeError("The margin should be a list or a number or a string")

    @property
    def content_width(self):
        """Get the original width of the content
        """
        if self._content is not None:
            return self._content.width

        return None

    @content_width.setter
    def content_width(self, width):
        """Update the originale width of the content.
        This method should be used inside the render function to set the width by:
        module.content_width = the_width_of_the_content
        """
        if isinstance(width, str):
            width = convert_unit(width)

        self._content.width = width


    @property
    def content_height(self):
        """Get the original height of the content
        """
        if self._content is not None:
            return self._content.height

        return None

    @content_height.setter
    def content_height(self, height):
        """Update the originale height of the content.
        This method should be used inside the render function to set the height by:
        module.content_height = the_height_of_the_content
        """
        if isinstance(height, str):
            height = convert_unit(height)

        self._content.height = height

    def set(self, **kwargs):
        """Add extrat args to the module.
        """

        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def get_index(self):
        """Return the position of the module in slide modules list
        """
        if Store.isgroup():
            pos = Store.group().modules.index(self)
        else:
            pos = Store.get_slide(self.slide_id).modules.index(self)

        return pos

    def get_previous_module(self):
        """Return the previous module stored in the slide.
        """

        previous_module = None

        mpos = self.get_index()
        if mpos > 0:
            if Store.isgroup():
                previous_module = Store.group().modules[mpos-1]
            else:
                previous_module = Store.get_slide(self.slide_id).modules[mpos-1]
        else:
            raise IndexError("No previous module in the slide or group")

        return previous_module

    @property
    def svgdef(self):
        if 'svgdef' in self.data:
            svgdef = self.data["svgdef"]
            return svgdef

        return None

    @svgdef.setter
    def svgdef(self, svgin):
        """Create the svg group with the correct id
        """
        out = f'<g id="{self.content_id}" class="{self.name}">{svgin}</g>'
        if hasattr(self, 'data') and 'svgdef' in self.data:
            self.data['svgdef'] = out
        else:
            self.data = {'svgdef': out}

    @property
    def svguse(self):
        """Return the svg <use> command for this element
        """
        return f'<use x="{self._final_x}" y="{self._final_y}" href="#{self.content_id}"/>'

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        if not hasattr(self, '_width'):
            if not isinstance(w, Length):
                length = Length(w, axis='x')
            else:
                length = w

            self._width = length
        else:
            if isinstance(w, Length):
                self._width.value = w._value
            else:
                self._width.value = w

    @property
    def height(self):
        return self._height

    @property
    def total_height(self):
        """The height + vertical margins
        """
        margin = self.margin
        return self.height + margin[0] + margin[2]

    @property
    def total_width(self):
        """The width + horizontal margins
        """
        margin = self.margin
        return self.width + margin[1] + margin[3]

    @height.setter
    def height(self, h):
        if not hasattr(self, '_height'):
            if not isinstance(h, Length):
                length = Length(h, axis='y')
            else:
                length = h

            self._height = length
        else:
            if isinstance(h, Length):
                self._height.value = h._value
            else:
                self._height.value = h

    @property
    def x(self):
        # print("prop class")
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, position):
        """
        Set a new horizontal position for the module. Create a Position object
        which allow delayed operation.

        Parameters
        ----------

        position: int or float or dict or string in 'auto' or 'center'
            When the position is given as a int or float: if position<1 will be a % of the
            current width, else if will be the position in pixel



        """

        # String cases
        if isinstance(position, str):
            if position.startswith('+') or position.startswith('-'):
                position = self.process_previous_position(position, 'x')
            elif position == 'auto':
                if self.slide_id is not None:
                    if Store.isgroup():
                        Store.group().id_modules_auto_x += [self.id]
                    else:
                        Store.get_slide(self.slide_id).id_modules_auto_x += [self.id]
                else:
                    if Store.isgroup():
                        Store.group().id_modules_auto_x += [self.id]
                    else:
                        raise IndexError("The module could not have x='auto' as it's defined outside of a slide or a group")

        # Tuple cases (x, y) or [x, y]
        if isinstance(position, (tuple, list)):
            # only keep the position for the y direction
            position = position[0]

        # Do I need to update X or create a new position object
        if not hasattr(self, '_x'):
            # Ensure that position is a Position class
            if not isinstance(position, Position):
                pos = Position(self, position, axis='x')
            else:
                pos = position

            self._x = pos
        else:
            # Update only the value
            if isinstance(position, Position):
                self._x.value = position._value
            else:
                self._x.value = position

    @y.setter
    def y(self, position):
        """
        Set a new vertical position for the module. Create a Position object
        which allow delayed operation.

        Parameters
        ----------

        position: int or float or list or tuple or dict or string in 'auto' or 'center'
            When the position is given as a int or float: if position<1 will be a % of the
            current width, else if will be the position in pixel
        """

        # String cases
        if isinstance(position, str):
            if position.startswith('+') or position.startswith('-'):
                position = self.process_previous_position(position, 'y')
            elif position == 'auto':
                if self.slide_id is not None:
                    if Store.isgroup():
                        Store.group().id_modules_auto_y += [self.id]
                    else:
                        Store.get_slide(self.slide_id).id_modules_auto_y += [self.id]
                else:
                    if Store.isgroup():
                        Store.group().id_modules_auto_y += [self.id]
                    else:
                        raise IndexError("The module could not have y='auto' as it's defined outside of a slide or group")


        # Tuple cases (x, y) or [x, y]
        if isinstance(position, (tuple, list)):
            # only keep the position for the y direction
            position = position[1]

        if not hasattr(self, '_y'):
            # Create a new position object
            if not isinstance(position, Position):
                pos = Position(self, position, axis='y')
            else:
                pos = position

            self._y = pos
        else:
            # Update the Position object
            if isinstance(position, Position):
                self._y.value = position._value
            else:
                self._y.value = position

    def process_previous_position(self, position, axis='x'):
        """Find the previous module in slide to process the current position
        position relative to this module.

        Parameters
        ----------

        - position, str (kind '+XX' or '-XXcm'):
            The position given as a relative position to the previous module of
            the slide.

        - axis, str in ['x', 'y'] (optional):
            The axis of the given position (default is 'x')

        Return
        ------

        a Position object with the correct operation if possible or None
        """

        assert isinstance(position, str), "Relative position should be a string"
        assert not position.startswith('+') or not position.startswith('-'), "Relative position should starts with + or -"
        assert axis in ['x', 'y'], "Axis should be 'x' or 'y'"

        previous_module = self.get_previous_module()

        if position.startswith('+'):
            offset = position.replace('+', '')
            previous_operation = '+'

        if position.startswith('-'):
            offset = position.replace('-', '')
            previous_operation = '-'

        if previous_module is not None:
            if previous_operation == '+':
                position = getattr(previous_module, axis) + offset
            else:
                position = getattr(previous_module, axis) - offset

        return position

    @property
    def right(self):
        """Return the horizontal position to be align with the right edge of the
        module.
        """
        return self.x + self.width + self.margin[1]

    @property
    def bottom(self):
        """Return the vertical position to be align with the bottom edge of the
        module.
        """
        return self.y + self.height + self.margin[2]

    @property
    def left(self):
        """Return the left anchor of the module
        """
        return self.x - self.margin[3]

    @property
    def top(self):
        """Return the top anchor of the module"""
        return self.y - self.margin[0]

    @property
    def center(self):
        """Return the horizontal and vertical positions to be align with the center of the
        module.
        """
        return (self.x + self.width/2, self.y + self.height/2)

    @property
    def x_center(self):
        return self.x + self.width/2

    @property
    def y_center(self):
        return self.y + self.height/2

    def compute_position(self):
        """Compute the position of the module and store the result in
        self._final_x, self._final_y variables.

        The computation of Position and Length will fix the relative length used
        for "%" operations.

        If the Position depends of 'auto' positionning, those "auto" positions
        should be computed before.
        """

        # Run the processing for x and y
        self._final_x = self.x.value
        self._final_y = self.y.value

    def delete(self):
        # Remove from document

        if self.slide_id is not None:
            for sid in self.slide_id:
                Store.get_slide(sid).remove_module(self.id)

        Store.remove_module(self.id)
        del self

    def reset_outputs(self):
        self.svgout = ''  # The output of the render
        self.htmlout = ''  # We can store also html peace of code
        self.jsout = ''  # Store javascript if needed
        self.animout = ''  # Store multiple rasters for animation
        self.data = None

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
        self.data['svgdef'] = "a data thing"
        self.content_width = self.width.value
        self.content_height = self.height.value

        self.rendered = True

    def run_render(self):
        """
            Run the function self.render if the module is not in cache
        """

        # Get the current slide object
        if self.slide_id is None:
            slide = None
            snum = None
        else:
            slide = Store.get_slide(self.slide_id)
            snum = slide.slide_num

        _log.debug("Render %s(id=%s): with height: %s and width: %s on slide: %s" % (self.name,
                                                                                     self.id,
                                                                                     self.height,
                                                                                     self.width,
                                                                                     snum))

        self.render()
        # Process the svg definitions
        # self.render_svgdefs()

    def get_name(self):
        # Return the name of the module
        # return str(self.__init__.im_class).split('.')[-1]
        name = str(type(self).__name__)

        return name

    def apply_theme(self, parent=None, lenient=False, exclude=None):
        """
        Load arguments of beampy_module.__init__ methods from the THEME when
        they are set to None. The beampy module should have a valid signature,
        updated with *beampy_module.update_signature* method.

        Parameters
        ----------
        parent: string optional,
            The name of the parent beampy_module to also load args

        lenient: boolean optional
            When True, allows check function to not stop Beampy
            compilation when the argument is not defined in the THEME
            dictionary (default value is False)

        exclude: list of str optional,
            Define key for which their is no THEME default to apply.

        """

        # Use an auto mode with arg=None -> then load from THEME
        # print(inspect.signature(self.__init__).parameters.keys())


        assert hasattr(self, '_arguments'), "Need to add use self.update_signature in your module init"
        self._arguments.apply_defaults()

        args = self._arguments.arguments
        keys = args.keys()

        function_name = self.name
        default_dict = Store.theme(function_name)

        # Merge default dictionary with the parent dictionary
        if parent is not None:
            default_dict = dict(default_dict,
                                **Store.theme(parent))

        if exclude is None:
            exclude = []

        for key, value in args.items():
            # If the value is None look for it in the default_dict
            if value is None and key not in exclude:
                if key in default_dict:
                    # Update the value in the object
                    setattr(self, key, default_dict[key])
                    # Update the args in the signature
                    self._arguments.arguments[key] = getattr(self, key)
                else:
                    if not lenient:
                        print_function_args(function_name)
                        raise IndexError("Error the key %s is not defined for %s module" % (key, function_name))
                    else:
                        _log.debug('Your argument %s is not defined in the Theme' % (key))

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
        out += 'Id: %s\n' % self.id
        if hasattr(self, '_content') and self._content is not None:
            out += 'Content id: %s\n' % self._content.id
        out += 'width: %s, height: %s\n' % (str(self.width), str(self.height))
        out += 'x: %s, y: %s\n' % (self.x, self.y)

        try:
            out += 'source (lines %i->%i):\n%s\n'%(self.call_lines[0], self.call_lines[1],
                                       self.call_cmd)
        except:
            out += 'source : fail\n'

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

    def __call__(self, x, y):
        """Add the module to the current slide or group with a given x, y
        position. This will add a deep copy of the module to the list of modules
        of group or slide.

        Parameters:
        -----------

        - x: str, int or float, or position or length object
            The horizontal position for the module

        - y: str, int or float, or position or length object
            The vertical position for the module
        """

        copy_self = deepcopy(self)

        # Reset the layers
        copy_self.layers = [0]

        # Redefine the slide_id
        copy_self.set_slide_id()


        # Add module to his slide or to the current group
        if copy_self.slide_id is not None:
            if Store.isgroup():
                Store.group().add_module(copy_self)
            else:
                Store.get_slide(copy_self.slide_id).add_module(copy_self)
            copy_self.id = copy_self.get_index()
        else:
            if Store.isgroup():
                Store.group().add_module(copy_self)
            copy_self.id = None

        # Update x, y positions
        copy_self._final_x = None
        copy_self._final_y = None
        copy_self.x = x
        copy_self.y = y

        return copy_self

    def __getitem__(self, item):
        """
        Manage layer of a given module using the python getitem syntax
        with slicing

        self()[0] -> layer([0])
        self()[:1] -> layer([0,1])
        self()[1:3] -> layer([1,2,3])
        self()[2:] -> layer([2,..,max(layer)])
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
                    self.add_layers('range(%i,max,%i)'%(start, step) )

            else:
                if isinstance(start, str):
                    self.add_layers('range(%s,%i,%i)'%(start, stop+1, step))
                else:
                    self.add_layers(list(range(start, item.stop+1, step)))

        else:
            if isinstance(item, (list, tuple)):
                string_layers = False
                item = list(item)
                for i, it in enumerate(item):

                    if isinstance(it, str):
                        string_layers = True
                    else:
                        if it < 0:
                            item[i] = 'max%i+1'%it
                            string_layers = True

                if string_layers:
                    # Need to replace ' by None because str([0,'max']) -> "[0,'max']"
                    self.add_layers(str(item).replace("'",""))
                else:
                    self.add_layers(item)

            else:
                if isinstance(item, str):
                    self.add_layers('[%s]'%item)
                else:
                    if item < 0:
                        item = 'max%i+1'%item
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
