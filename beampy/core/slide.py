#!/usr/bin/env python3

"""
The slide class of the beampy project:
"""
from beampy.core.store import Store
from beampy.core.document import document
from beampy.core.functions import (check_function_args, convert_unit,
                                   set_curentslide, set_lastslide)
from beampy.core._svgfunctions import export_svgdefs
from beampy.core.group import group
from beampy.core.layers import unique_layers, get_maximum_layer
from beampy.core.geometry import horizontal_distribute, vertical_distribute

from string import Template
import json
from io import StringIO
from pathlib import Path
from tempfile import gettempdir

import logging
import sys

try:
    from IPython import get_ipython
    from IPython.display import display
    _IPY_ = get_ipython()
except:
    _IPY_ = None

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

    def __init__(self, title=None, slide_num=None, **kwargs):

        # Add a slide to the global counter
        # if 'slide' in document._global_counter:
        #    document._global_counter['slide'] += 1
        # else:
        #    document._global_counter['slide'] = 0

        # Init group counter
        # document._global_counter['group'] = 0

        # check args from THEME
        self.args = check_function_args(slide, kwargs)

        # The id for this slide
        if slide_num is None:
            self.slide_num = len(Store)+1
        else:
            if slide_num > len(Store)+1:
                raise IndexError(f'slide_num should be <= {len(Store)+1}')
            else:
                self.slide_num = slide_num

        self.id = 'slide_%i' % self.slide_num
        # Set this slide as the curent slide (where components will be added)
        # document._curentslide = self.id

        # Change from dict to class
        self.tmpout = ''
        self.modules = []  # will store modules
        self.id_modules_auto_x = []  # will store modules with x='auto'
        self.id_modules_auto_y = []  # will store modules with y='auto'
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
        # Html is a dict, each key dict is a layer htmlout[0] = [html, html, html] etc...
        self.htmllayer = {}
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'
        # Store slide final svg (without svg defs stored in self.svgdefout) for the given layer
        self.svglayers = {}

        # Do we need to render the THEME layout on this slide
        self.render_layout = True

        # Add the slide to the Store
        Store.add_slide(self)

        # Add the slide to the document contents list
        #document._slides[self.id] = self

        # Store the current TOC position
        # TODO: Re-implement TOC !!!
        #if len(document._TOC) > 0:
        #    self.TOCposition = document._TOC[-1]
        #else:
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
        # Html is a dict, each key dict is a layer htmlout[0] = [html, html, html] etc...
        self.htmlout = {}
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'
        # Store slide final svg (without svg defs stored in self.svgdefout) for the given layer
        self.svglayers = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # Check layers inside this slide
        self.check_modules_layers()

        if _IPY_ is not None:
            display(self)

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

    def _repr_html_(self):
        """ Ipython special html export,
        render the slide as HTML inside an iframe
        """
        from IPython.display import IFrame, clear_output

        # Save the slide html to a tmp folder
        tmp_html_file = Path('./').joinpath('beampy_cache_ipython')
        if not tmp_html_file.is_dir():
            tmp_html_file.mkdir(parents=True)

        tmp_html_file = tmp_html_file.joinpath(f'BP_slide_{self.id}.html')
        with open(tmp_html_file, 'w') as f:
            f.write(self.to_html())

        clear_output()

        return IFrame(tmp_html_file, '100%', 400)._repr_html_()

    def render(self, svgaltdef=False):
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
        self.layers_content['all'] = {'js': []}

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
                        # For svgaltdef add a svg use for this element id
                        if svgaltdef and mod.svgaltdef is not None:
                            self.layers_content[layer]['svg'] += [mod.svguse]        

                    self.layers_content[layer][mod.type] += [content]

        # Join the modules content for each layers
        for layer in self.layers_content:
            if layer == 'all':
                self.layers_content[layer]['js'] = ''.join(
                    self.layers_content[layer]['js'])
            else:
                self.layers_content[layer]['html'] = ''.join(
                    self.layers_content[layer]['html'])
                self.layers_content[layer]['svg'] = ''.join(
                    self.layers_content[layer]['svg'])

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

    def to_html(self) -> str:
        """
        Process this slide, and create an HTML string or file with only this slide.

        Return a string with a valid HTML
        """

        # First render the slide
        self.render()

        # TODO: create an optimizer to only export glyphs used in this slide
        #       this could be done using regex to get id starting with "gXXX"
        # Export glyphs
        glyphs_store = ('<svg id="glyph_store"><defs>'
                        '{glyphs}'
                        '</defs></svg>')
        glyphs_store = glyphs_store.format(glyphs=''.join(
            (g['svg'] for g in Store.get_all_glyphs().values())))

        exported_defs_id = []
        svg_defs, tmp_id = export_svgdefs(
            self.modules, exported_id=exported_defs_id)

        # Beampy use json to make reference to a given slide-layer in the HTML/JS world.
        slide_id = 'slide_0'
        tmpout = {slide_id: {'svg': [],
                             'layers_nums': self.num_layers,
                             'svg_header': self.svgheader,
                             'svg_footer': self.svgfooter}
                  }

        layer_defs = ''
        html_modules = ''
        for layer in range(self.num_layers+1):
            if layer in self.layers_content:
                svg_layer_content = self.layers_content[layer]['svg']
                html_layer_content = self.layers_content[layer]['html']
                if html_layer_content != '':
                    html_modules += ''.join([f'<div id="html_store_slide_0-{layer}"',
                                             'style="position:absolute;top:0px;left:0px;',
                                             'display:none;">',
                                             html_layer_content,
                                             '</div>'])
            else:
                # create an empty content (usefull when only html are present in one slide)
                svg_layer_content = ''

            layer_defs += f"<g id='slide_0-{layer}'>{svg_layer_content}</g>"
            tmpout[slide_id]['svg'] += [
                f'<use xlink:href="#slide_0-{layer}"/>']

        if self.animout is not None:
            tmpout[slide_id]['svganimates'] = {}
            headers = []
            for ianim, data in enumerate(self.animout):
                headers += [data['header']]
                data.pop('header')
                tmpout[slide_id]['svganimates'][data['anim_num']] = data

            # Add cached images to global_store
            # old comparision headers != []
            if len(headers) > 0:
                # OLD .decode('utf-8', errors='replace') after join for py2
                tmp = ''.join(headers)
                layer_defs += f"{tmp}"

        if self.scriptout is not None:
            tmpscript = {slide_id: ''.join(self.scriptout)}
        else:
            tmpscript = None

        # the defs part of svg
        global_defs = glyphs_store + \
            f'<svg><defs>{svg_defs}\n{layer_defs}</defs></svg>'

        # Load statics parts
        # Read style (use python3 string Template)
        with open(Store._beampy_dir.joinpath('statics', 'beampy.css'), 'r') as f:
            css = Template(f.read())

        # Read jquery
        with open(Store._beampy_dir.joinpath('statics', 'jquery.js'), 'r') as f:
            jquery = f.read()

        # read html header
        with open(Store._beampy_dir.joinpath('statics', 'header_V2.html'), 'r') as f:
            html_header = Template(f.read())

        # read html footer
        with open(Store._beampy_dir.joinpath('statics', 'footer_V2.html'), 'r') as f:
            footer = Template(f.read())

        # read beampyjs
        with open(Store._beampy_dir.joinpath('statics', 'beampy.js'), 'r') as f:
            beampyjs = f.read()

        # Create the html output file
        document = Store.get_layout()
        htmltheme = document._theme['document']['html']
        css = css.substitute(width=document._width,
                             height=document._height,
                             background_color=htmltheme['background_color'])

        # Add jquery and css to html header
        html_content = html_header.substitute(jquery=jquery,
                                              css=css)

        # Add svg defs to the html
        html_content += global_defs
        # Add html modules div to the html
        html_content += html_modules

        # Create a json file of all slides javascript defs
        jsonfile = StringIO()
        json.dump(tmpout, jsonfile, indent=None)
        jsonfile.seek(0)
        # eval this json file in javascript
        html_content += f'<script>slides=eval(({jsonfile.read()}));</script>'

        # Add javascript added by users in beampy to the html
        # TODO: re-implement js-output for beampy-V1
        special_js = ''

        # Add the footer of
        html_content += footer.substitute(beampy=beampyjs)

        # write cache file
        if Store.cache() is not None:
            Store.cache().save()

        return html_content
