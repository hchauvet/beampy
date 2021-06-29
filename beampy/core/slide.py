#!/usr/bin/env python3

"""
The slide class of the beampy project:
"""
from beampy.core.document import document
from beampy.core.functions import (check_function_args, convert_unit,
                                   set_curentslide, set_lastslide)
from beampy.core.group import group
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
        if 'slide' in document._global_counter:
            document._global_counter['slide'] += 1
        else:
            document._global_counter['slide'] = 0

        # Init group counter
        document._global_counter['group'] = 0

        # check args from THEME
        self.args = check_function_args(slide, kwargs)

        # The id for this slide
        self.slide_num = document._global_counter['slide']
        self.id = 'slide_%i' % self.slide_num
        # Set this slide as the curent slide (where components will be added)
        document._curentslide = self.id

        # Change from dict to class
        self.tmpout = ''
        self.contents = {}
        self.element_keys = []
        self.cpt_anim = 0
        self.num = document._global_counter['slide']+1
        self.title = title
        self.curwidth = document._width
        self.curheight = document._height
        self.num_layers = 0  # Store the number of layers in this slide

        # Store all outputs
        self.svgout = []
        self.svgdefout = []  # Store module definition for slide
        self.htmlout = {}  # Html is a dict, each key dict is a layer htmlout[0] = [html, html, html] etc...
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'
        self.svglayers = {}  # Store slide final svg (without svg defs stored in self.svgdefout) for the given layer

        # Do we need to render the THEME layout on this slide
        self.render_layout = True

        # Add the slide to the document contents list
        document._slides[self.id] = self

        # Store the current TOC position
        if len(document._TOC) > 0:
            self.TOCposition = document._TOC[-1]
        else:
            self.TOCposition = 0

        # Manage groups inside one slide the lower level of group is 0 and correspond
        # to the main slide
        self.groupsid = {}
        self.cur_group_level = -1
        g0 = group(x=0, y=0, width=document._width, height=document._height)
        # Store the current group id (managed by the
        # __enter__/__exit__ method of group class)
        self.cur_group_id = g0.id
        self.groupsid[0] = [g0.id]  # store groups id objects in this list

        if title is not None:
            from beampy.modules.title import title as bptitle
            self.title_element = bptitle(title)
            self.ytop = float(convert_unit(self.title.reserved_y))
        else:
            self.ytop = 0
            self.title_element = None

        # Add ytop to the slide main group
        g0.yoffset = self.ytop

    def add_module(self, module_id, module_content):
        # Add a module to the current slide
        # logging.debug('Add module %s to slide %s' % (str(module_content.type), self.id))

        self.element_keys += [module_id]
        self.contents[module_id] = module_content

        # Check if it's a new group or not
        # print(self.groupsid, self.cur_group_level)
        if module_content.type != 'group':
            _log.debug('Module %s added to group %s' % (str(module_content.name), self.cur_group_id))
            self.contents[self.cur_group_id].add_elements_to_group(module_id, module_content)
            # Add the id of the group to the module
            self.contents[module_id].group_id = self.cur_group_id
            # Todo[improvement]: register the group tree for a given module not just the last group
        else:
            # print("add group %s with id %s" % (str(module_content), module_id))
            if module_content.grouplevel > 0:
                # Add this group id to the previous group
                if module_content.parentid is not None:
                    _log.debug("Add parent (id=%s) for %s(%s)" % (module_content.parentid, module_content.name, module_id))
                    self.contents[module_content.parentid].add_elements_to_group(module_id, module_content)

                # Record group tree in groupsid dict
                if module_content.grouplevel not in self.groupsid:
                    self.groupsid[module_content.grouplevel] = [module_id]
                else:
                    self.groupsid[module_content.grouplevel] += [module_id]

            logging.debug('Element %s added to slide'%(str(module_content.name)))

    def remove_module(self, module_id):
        # Remove a module
        self.element_keys.pop(self.element_keys.index(module_id))
        # Remove the module from it's group
        gid = self.contents[module_id].group_id
        self.contents[gid].remove_element_in_group(module_id)
        # Remove the module from contents main store
        self.contents.pop(module_id)

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

        # Get the max layers
        for mid in self.element_keys:
            module = self.contents[mid]

            # When the range of layer is defined as a string (usual
            # with an unknown maximum), take the start value as
            # maximum layer
            if isinstance(module.layers, str):
                start = int(module.layers.split(',')[0].replace('range(',''))
                maxmodulelayers = start
            else:
                maxmodulelayers = max(module.layers)

            if maxmodulelayers > self.num_layers:
                self.num_layers = maxmodulelayers

        # Resolve 'range(0, max, 1)'
        layers_in_slide = []
        for mid in self.element_keys:
            module = self.contents[mid]

            # Resolve string args 'max' in layers
            if isinstance(module.layers, str):
                if 'range' in module.layers:
                    lmax = self.num_layers + 1
                else:
                    lmax = self.num_layers

                module.add_layers(eval(module.layers.replace('max', str(lmax))))

            # Check the consecutivity of layers
            for layer in module.layers:
                if layer not in layers_in_slide:
                    layers_in_slide += [layer]

        layers_in_slide = sorted(layers_in_slide)
        if layers_in_slide != list(range(0, self.num_layers+1)):
            raise ValueError('Layers are not consecutive. I got %s, I should have %s'%(str(layers_in_slide),
                                                                                       str(list(range(0, self.num_layers+1)))))

        # Propagate layer of modules inside groups
        for mid in self.element_keys:
            if self.contents[mid].type == 'group':
                _log.debug('Run propagate layer for %s' % str(self.contents[mid].name))
                self.contents[mid].propagate_layers()

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

        header_template = svg_template.format(width=document._width,
                                              height=document._height,
                                              bgcolor=self.args['background'])
        self.svgheader = header_template
