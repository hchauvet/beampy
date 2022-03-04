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
        self.htmllayer = {}  # Html is a dict, each key dict is a layer htmlout[0] = [html, html, html] etc...
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'
        self.svglayers = {}  # Store slide final svg (without svg defs stored in self.svgdefout) for the given layer

        # Do we need to render the THEME layout on this slide
        self.render_layout = True

        # Add the slide to the Store
        Store.add_slide(self)

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

        # TODO: The reserved space for the title should be taken from the THEME
        if title is not None:
            from beampy.modules.title import title as bptitle
            self.title_element = bptitle(title)[:]
            # self.ytop = float(convert_unit(self.title.reserved_y))
            # self.ytop = self.title_element.height.value
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

    def __repr__(self):
        """
        Convenient informations to display for slide when using str(slide)
        """
        ngroup = len(tuple(m for m in self.modules if m.type == 'group'))
        out = 'Slide <%i>\n' % self.slide_num
        out += '- %i modules [%i groups]' % (len(self.modules), ngroup)

        return out

    def render(self, add_html_svgalt=False):
        """Compute the final position of each modules in the slide and add the
        final module content to the self.layers_content dictionnary. This
        dictionnary is formarted as follow:

        self.layers_content = {layer: {'html': ''.join([module.html]),
                                       'svg': ''.join([module.svguse]) },
                               'all': {'js': ''.join(module.javascript)}}
        """

        print('-' * 20 + ' slide_%i ' % self.slide_num + '-' * 20)

        # Init the dictionnary to get the final data
        self.layers_content = {}

        # Init content common to all layers
        self.layers_content['all']  = {'js': []}

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

                #  Initialise dictionnary for given layer
                if layer not in self.layers_content:
                    self.layers_content[layer] = {'html': [],
                                                  'svg': []}

                if mod.type == 'group':
                    #  Group could contains "html" and "svg" modules, and they
                    #  have a specific function to export their content.
                    svg_content = mod.svguse(layer)
                    self.layers_content[layer]['svg'] += [svg_content]

                    html_content = mod.html(layer)
                    self.layers_content[layer]['html'] += [html_content]
                else:
                    if mod.type == 'svg':
                        content = mod.svguse

                    if mod.type == 'html':
                        content = mod.html
                        # For html_svgalt add a svg use for this element id
                        if add_html_svgalt and mod.html_svgalt is not None:
                            self.layers_content[layer]['svg'] += [mod.svguse]

                    self.layers_content[layer][mod.type] += [content]


        # Join the modules content for each layers
        for layer in self.layers_content:
            if layer == 'all':
                self.layers_content[layer]['js'] = ''.join(self.layers_content[layer]['js'])
            else:
                self.layers_content[layer]['html'] = ''.join(self.layers_content[layer]['html'])
                self.layers_content[layer]['svg'] = ''.join(self.layers_content[layer]['svg'])



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
        svg_template = ('<?xml version="1.0" encoding="utf-8" standalone="no"?> '
        '<svg width="{width}px" height="{height}px" '
        'style="background-color:{bgcolor};" '
        'version="1.1" baseProfile="full" '
        'xmlns="http://www.w3.org/2000/svg" '
        'xmlns:svg="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:ev="http://www.w3.org/2001/xml-events" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:cc="http://creativecommons.org/ns#" '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
        'xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        'shape-rendering="geometricPrecision" '
        '>'
        '<rect width="{width}px" height="{height}px" fill="{bgcolor}"/>')

        header_template = svg_template.format(width=Store.get_layout()._width,
                                              height=Store.get_layout()._height,
                                              bgcolor=self.args['background'])
        self.svgheader = header_template
