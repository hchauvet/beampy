#!/usr/bin/env python3

"""
The slide class of the beampy project:
"""
from beampy.core.store import Store
from beampy.core.document import document
from beampy.core.functions import (check_function_args, convert_unit,
                                   set_curentslide, set_lastslide)
from beampy.core.group import group
from beampy.core.layers import unique_layers, get_maximum_layer
from beampy.core.geometry import horizontal_distribute, vertical_distribute
import logging
_log = logging.getLogger(__name__)


class slide(object):
    """
    Add a slide to the presentation.

    Parameters
    ----------

    title : str or None, optional
        Set the title of the slide (the default value is None)

    background : str, optional
        Background color of the slide (the default value is "white"). Accept svg color name or HTML hex value.

    layout: function or None, optional
        Function containing beampy modules that will be displayed as slide background.

        >>> slide(layout=my_function)

    """

    def __init__(self, title=None, **kwargs):

        # Add a slide to the global counter
        # if 'slide' in document._global_counter:
        #    document._global_counter['slide'] += 1
        #else:
        #    document._global_counter['slide'] = 0

        # Init group counter
        # document._global_counter['group'] = 0

        # check args from THEME
        self.args = check_function_args(slide, kwargs)

        # The id for this slide
        self.slide_num = len(Store)+1
        self.id = 'slide_%i' % self.slide_num
        # Set this slide as the curent slide (where components will be added)
        # document._curentslide = self.id
        Store.add_slide(self)

        # Change from dict to class
        self.tmpout = ''
        self.modules = []  # will store modules
        self.id_modules_auto_x = [] # will store modules with x='auto'
        self.id_modules_auto_y = [] # will store modules with y='auto'
        self.contents = {}
        self.element_keys = []
        self.cpt_anim = 0
        # self.num = self.slide_num
        self.title = title
        self.curwidth = document._width
        self.curheight = document._height
        self.num_layers = 0  # Store the number of layers in this slide

        # Store all outputs
        self.svgout = []
        self.svgdefout = []  # Store module definition for slide
        self.svgdefsid = []  # Store defs id
        self.htmlout = {}  # Html is a dict, each key dict is a layer htmlout[0] = [html, html, html] etc...
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'
        self.svglayers = {}  # Store slide final svg (without svg defs stored in self.svgdefout) for the given layer

        # Do we need to render the THEME layout on this slide
        self.render_layout = True

        # Add the slide to the document contents list
        #document._slides[self.id] = self

        # Store the current TOC position
        if len(document._TOC) > 0:
            self.TOCposition = document._TOC[-1]
        else:
            self.TOCposition = 0

        # Manage groups inside one slide the lower level of group is 0 and correspond
        # to the main slide
        # self.groupsid = {}
        self.cur_group_level = -1
        # g0 = group(x=0, y=0, width=document._width, height=document._height)

        # Store the current group id (managed by the
        # __enter__/__exit__ method of group class)
        self.cur_group_pos = 0
        # old self.cur_group_id
        # self.groupsid[0] = [g0.id]  # store groups id objects in this list

        if title is not None:
            from beampy.modules.title import title as bptitle
            self.title_element = bptitle(title)
            self.ytop = float(convert_unit(self.title.reserved_y))
        else:
            self.ytop = 0
            self.title_element = None

        # Add ytop to the slide main group
        # g0.yoffset = self.ytop

    def add_module(self, module):
        """Add a module to the list of modules in this slides.

        Parameters
        ----------

        module, beampy_module object:
            The module to add to the slide
        """

        # Add a module to the current slide
        self.modules += [module]

    def add_rendered(self, svg=None, svgdefs=None, html=None, js=None,
                     animate_svg=None, layer=0):
        _log.debug('Add rendered')

        if svg is not None:
            self.svgout += [svg]

        if svgdefs is not None:
            _log.debug('svgdefs')
            self.svgdefout += [svgdefs]

        if html is not None:
            if layer in self.htmlout:
                self.htmlout[layer] += [html]
            else:
                self.htmlout[layer] = [html]

        if js is not None:
            self.scriptout += [js]

        if animate_svg is not None:
            self.animout += [animate_svg]

    def reset_rendered(self):
        self.svgout = []
        self.svgdefout = []  # Store module definition for slide
        self.htmlout = {}  # Html is a dict, each key dict is a layer htmlout[0] = [html, html, html] etc...
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'
        self.svglayers = {}  # Store slide final svg (without svg defs stored in self.svgdefout) for the given layer

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Check layers inside this slide
        self.check_modules_layers()

    def check_modules_layers(self):
        """
        Function to check the consistency of layers in the slide.
        To do so:

        1- Get the number of layers

        2- Resolve string layers to replace 'max' statement with the slide number of layer
           expl: 'range(0-max-1)' or '[0,max]'

        3- Check that layers are consecutive numbers from 0 -> max
        """

        self.num_layers = get_maximum_layer(self.modules)
        layers_in_slide = unique_layers(self.modules, self.num_layers)
        _log.debug('List of layers %s ' % str(layers_in_slide))

    def show(self):
        from beampy.exports import display_matplotlib
        display_matplotlib(self.id, True)

    def build_layout(self):
        """
            Function to build the layout of the slide,
            elements defined in bacground inside the theme file
        """

        # Check if we have a background layout to render
        if self.render_layout:
            if self.args['layout'] is not None and 'function' in str(type(self.args['layout'])):

                set_curentslide(self.id)
                # Need to get the current group
                curgroup = self.contents[self.cur_group_id]

                # Need to store elements keys last index to retrieve elements added by theme layout function
                first_elem_i = len(self.element_keys)
                first_elem_in_group = len(curgroup.elementsid)

                # Run the layout function (which contains beampy modules)
                self.args['layout']()

                # Store elements_keys created and pop them to insert
                # them at the begining of the list (in the bakcground)
                created_element_keys = self.element_keys[first_elem_i:]
                self.element_keys = created_element_keys + self.element_keys[:first_elem_i]

                #Whe need to todo the same for the elements contained in the group
                curgroup.elementsid = curgroup.elementsid[first_elem_in_group:] + curgroup.elementsid[:first_elem_in_group]

                # Loop over elements to add them to all layers in the slide
                for eid in created_element_keys:
                    self.contents[eid].add_layers(list(range(self.num_layers+1)))

                #document._global_counter['slide'] = save_global_ct # restor the slide counter
                set_lastslide()


    def __repr__(self):
        """
        Convenient informations to display for slide when using str(slide)
        """
        ngroup = len(tuple(m for m in self.modules if m.type == 'group'))
        out = 'Slide <%i>\n' % self.slide_num
        out += '- %i modules [%i groups]' % (len(self.modules), ngroup)

        return out

    def render(self):
        print('-' * 20 + ' slide_%i ' % self.slide_num + '-' * 20)

        self.svgdefout = []
        self.svgdefsid = []
        self.svgout = {}
        self.svglayers = {}

        # Process x='auto'
        if len(self.id_modules_auto_x) > 0:
            horizontal_distribute([self.modules[mid] for mid in self.id_modules_auto_x],
                                  self.curwidth)

        # Process y='auto'
        if len(self.id_modules_auto_y) > 0:
            vertical_distribute([self.modules[mid] for mid in self.id_modules_auto_y],
                                self.curheight)

        # Loop over modules
        for i, mod in enumerate(self.modules):
            mod.compute_position()

            # Need to check if we already have the definition of this module
            # This is done globally by the render function
            # if mod.content_id not in self.svgdefsid:
                # self.svgdefout += [mod.svgdef]
                # self.svgdefsid += [mod.content_id]

            # Export svg use for this module
            for layer in mod.layers:
                if mod.type == 'group':
                    svguse = mod.svguse(layer)
                else:
                    svguse = mod.svguse

                if layer in self.svgout:
                    self.svgout[layer] += [svguse]
                else:
                    self.svgout[layer] = [svguse]

        for layer in self.svgout:
            self.svglayers[layer] = ''.join(self.svgout[layer])

        self.export_header()

    def newrender(self):
        """
        Render the slide content.
        - Transform module to svg or html
        - Loop over groups
        - Place modules
        - write the final svg
        """
        print('-' * 20 + ' slide_%i ' % self.num + '-' * 20)

        if self.title_element is not None:
            self.title_element.add_layers(list(range(self.num_layers+1)))

        # First loop over slide's modules to render them (to get height and width)
        # Todo: do that using multiprocessing
        for i, key in enumerate(self.element_keys):
            elem = self.contents[key]

            if elem.type != 'group':
                if not elem.rendered:
                    # Run the pre render method of each modules
                    elem.pre_render()
                    # print('main loop run_render')
                    elem.run_render()

                assert elem.width.value is not None
                assert elem.height.value is not None
                # print(elem.width, elem.height)
            else:
                # Run the pre render method for groups
                elem.pre_render()

        # Loop over group level (from the max -> 0)
        print('Number of group levels %i' % max(self.groupsid))

        for level in range(max(self.groupsid), -1, -1):

            for curgroupid in self.groupsid[level]:

                curgroup = self.contents[curgroupid]

                curgroup.compute_group_size()
                # print(curgroup.width, curgroup.height)

                # Render the current group (this export final module svg to slide storage)
                curgroup.render()

            if level == 0:
                # The last group (i.e the main frame need to be placed)
                curgroup.positionner.place((document._width, document._height))
                # Export the svg of the slide at a given layer in the slide.svglayers store
                for layer in curgroup.layers:
                    print('export layer %i'%layer)
                    # Check if the layer contain svg outputs (for instance video only layer could exists)
                    try:
                        self.svglayers[layer] = curgroup.export_svg_layer(layer)
                    except Exception as e:
                        # TODO ADD a log to this try
                        print('no svg for layer %i' % layer)


                #Need to deal with html module
                if document._output_format == 'html5':
                    for eid in curgroup.htmlid:
                        # print('Render html %s' % eid)
                        elem = self.contents[eid]
                        # Resolve absolute positionning
                        xgroupsf = sum([self.contents[g].positionner.x['final']
                                        for g in elem.groups_id])
                        ygroupsf = sum([self.contents[g].positionner.y['final']
                                        for g in elem.groups_id])
                        # print(xgroupsf, elem.positionner.x['final'], ygroupsf)
                        elem.positionner.x['final'] += xgroupsf
                        elem.positionner.y['final'] += ygroupsf
                        for layer in elem.layers:
                            htmlo = elem.export_html()
                            self.add_rendered(html=htmlo, layer=layer)

                # Add grid and fancy stuff...
                if document._guide:
                    available_height = document._height - self.ytop
                    out = ''
                    out += '<g><line x1="400" y1="0" x2="400" y2="600" style="stroke: #777"/></g>'
                    out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>' % (
                    self.ytop + available_height / 2.0, self.ytop + available_height / 2.0)
                    out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>' % (
                    self.ytop, self.ytop)
                    self.add_rendered(svg=out)

        self.export_header()

    def export_header(self):
        # Export the slide svg header
        svg_template = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
        <svg width='{width}px' height='{height}px' style='background-color: {bgcolor};'
        xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="full"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:cc="http://creativecommons.org/ns#"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        shape-rendering="geometricPrecision"
        >"""\

        header_template = svg_template.format(width=Store.get_layout()._width,
                                              height=Store.get_layout()._height,
                                              bgcolor=self.args['background'])
        self.svgheader = header_template
