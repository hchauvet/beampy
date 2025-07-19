#!/usr/bin/env python3

"""
Class that define beampy groups. It's a class that derives from module base class.
"""
from beampy.core.store import Store
from beampy.core.document import document
from beampy.core.content import Content
from beampy.core.geometry import (horizontal_distribute,
                                  vertical_distribute)
from beampy.core.module import beampy_module
from beampy.core.layers import (unique_layers, get_maximum_layer,
                                stringlayers_to_int)
from beampy.core.functions import gcs
import sys

import logging
_log = logging.getLogger(__name__)


class group(beampy_module):

    def __init__(self, x=None, y=None, width=None, height=None, margin=None,
                 modules=None, background=None, **kwargs):
        """Group beampy elements to manipulate them as a single beampy_module

        Parameters:
        -----------

        Example:
        --------
        """

        self.init_width = width
        self.init_height = height

        # Init this as a module
        super().__init__(x, y, width, height, margin, 'group', **kwargs)
        # Update the default arguments
        self.update_signature()

        # Add arguments as attributes
        self.set(background=background)
        self.theme_exclude_args = ['modules']
        self.apply_theme()

        # Check in the store if their is a parent group object
        self.parent = None
        if Store.isgroup():
            self.parent = Store.group()
        else:
            if Store.get_current_slide_id() is not None:
                self.parent = Store.get_current_slide()

        # Need to compute relative length for group
        if self.width.is_relative:
            self.width = self.width.value
        if self.height.is_relative:
            self.height = self.height.value

        Store.set_group(self)

        self.modules = modules
        self.modules_order = modules
        # Store modules that need to be "automatically placed" inside the group
        self.id_modules_auto_x = []
        self.id_modules_auto_y = []

        if self.modules is None:
            self.modules = []
            self.modules_order = []

        if len(self.modules) > 0:
            self.__exit__()

    def add_content(self, content, content_type):
        """Rewrite add_content method for groups
        """
        pass

    def add_module(self, bp_module):
        """Add the module to the group
        """
        self.modules += [bp_module]
        self.modules_order += [bp_module]

    def render(self):
        """
        Render the group modules and create an svg group
        """

        svgout = {}

        # Create a new content with all those modules
        content = '('+', '.join([m.signature for m in self.modules])+')'
        self._content = Content(content, 'svg',
                                self.width.value,
                                self.height.value,
                                self.name)


        # Manage width = None, height = None
        # When width is None compute the total width of elements in the group
        if self.init_width is None:
            if Store.get_current_slide_id() is None:
                w = Store.theme('document')['width']
                print('Set width to the one defined in Theme for document ', w)
            else:
                w = Store.get_current_slide().curwidth

            self.width = w

        if self.init_height is None:
            if Store.get_current_slide_id() is None:
                h = Store.theme('document')['height']
                print('Set height to the one defined in Theme for document', h)
            else:
                h = Store.get_current_slide().curheight

            self.height = h

        # Process auto X
        if len(self.id_modules_auto_x) > 0:
            horizontal_distribute([self.modules[mid] for mid in self.id_modules_auto_x],
                                   self.width.value)

        # Process auto Y
        if len(self.id_modules_auto_y) > 0:
            vertical_distribute([self.modules[mid] for mid in self.id_modules_auto_y],
                                self.height.value)

        # Loop over modules
        for i, mod in enumerate(self.modules):
            # Compute the final position of the module
            mod.compute_position()

            # Need to export animation for the group
            if len(mod.animout) > 0:
                # Recursion for group in a group
                if mod.type == 'group':
                    self.animout += mod.animout
                else:
                    self.animout += [ mod.export_animation() ]

        # Need to re-compute the width and height of the group
        # from the "frozen" width/height (called content_width/content_height)
        if self.init_width is None:
            g_width = self.group_width()
            self.width = g_width

            # Need to set the origine of the modules as we change te width
            xmin = self.xmin()
            for m in self.modules:
                m._final_x -= xmin

        if self.init_height is None:
            g_height = self.group_height()
            self.height = g_height

            # Need to set the origine of the modules as we change te width
            ymin = self.ymin()
            for m in self.modules:
                m._final_y -= ymin

        # Export to data each group for the different layers
        self.svgdef = 'Defined on export'
        self.content_width = self.width.value
        self.content_height = self.height.value

        # Fix the width and height
        self.width = self.width.value
        self.height = self.height.value

        # For group we define the signature after the renderering
        # to include the list of modules
        self.update_signature(modules=self.modules)

    def export_svgdef(self) -> dict:
        """Dynamically export svgdef for each modules in the group.
        Return a dictionnary of list of svgdef indexed by layer

        svgdef in a group is a recursive export of module svg <use> tags.
        """

        # TODO: remove empty svguse, and take care of svguse needed for html_svgalt
        svgout = {}
        for mod in self.modules:
            for layer in mod.layers:
                if mod.type == 'group':
                    svguse = mod.svguse(layer)
                else:
                    # Need to take care of svganimate here
                    if len(mod.animout) > 0:
                        svguse = mod.export_animation_layer(layer)
                    else:
                        svguse = mod.svguse

                if layer in svgout:
                    svgout[layer] += [svguse]
                else:
                    svgout[layer] = [svguse]

        # Add the last layer of modules svguse to the group layer above the
        # maximum of modules layers.
        max_layer = max(svgout.keys())
        for layer in self.layers:
            if layer > max_layer:
                svgout[layer] = svgout[max_layer]

        return svgout

    @property
    def svgdef(self):
        if 'svgdef' in self.data:
            svgdef = self.export_svgdef()
            out = [f'<g id=\"{self.content_id}_{self.slide_id}_{layer}\" class="group">'+self.svg_decoration+f'{"".join(svgdef[layer])}'+'</g>' for layer in svgdef]
            out_id = [f'{self.content_id}_{self.slide_id}_{layer}' for layer in svgdef]
            return out_id, out

        return None, None

    @svgdef.setter
    def svgdef(self, svgin):
        """Rewrite svgdef setter for group
        """
        if self.data is not None and 'svgdef' in self.data:
            self.data['svgdef'] = svgin
        else:
            self.data = {'svgdef': svgin}

    def svguse(self, layer):
        """Rewrite the method for group, as it should take in consideration
        layers!
        """
        assert self._final_x is not None, f"{self.name} final X position is None for\n{self}"
        assert self._final_y is not None, f"final Y position is None for\n{self}"

        svg_box = ''
        if self.show_box_model:
            # The content box
            svg_box = f'<rect x="{self._final_x+self.margin.left}" y="{self._final_y+self.margin.top}" width="{self.width.value}px" height="{self.height.value}px" style="stroke:red; fill:none;"/>'
            # The margin box
            svg_box += f'<rect x="{self._final_x}" y="{self._final_y}" width="{self.total_width.value}px" height="{self.total_height.value}px" style="stroke:green; fill:none;"/>'

        return f'<use x="{self._final_x+self.margin.left}" y="{self._final_y+self.margin.top}" xlink:href="#{self.content_id}_{self.slide_id}_{layer}"/>{svg_box}'

    def html(self, layer):
        """Rewrite html property of module as a function to export all html
        'div' contained in group modules. This function is recursive as if we
        have a group inside the modules the same function is called back.

        Take care to not export empty group
        """

        layer_divs = []
        for mod in self.modules:
            if layer in mod.layers:
                if mod.type == 'html':
                    modhtml = mod.html
                    if modhtml is not None:
                        layer_divs += [modhtml]

                if mod.type == 'group':
                    gphtml = mod.html(layer)
                    if gphtml != '':
                        layer_divs += [gphtml]

        divout = []
        if len(layer_divs) > 0:
            divout = ['<div id="group"',
                      'style="position:absolute;',
                      f'top:{self._final_y}px;',
                      f'left:{self._final_x}px;',
                      f'width:{self.content_width}px;',
                      f'height:{self.content_height}px;',
                      '">']
            divout += layer_divs
            divout += ['</div>']

        return ''.join(divout)

    def group_width(self, modules=None):
        """Compute the width of the group based on the module inside the group.
        group modules should have been positionned prior to compute the
        group_size.

        return the computed width
        """

        if modules is None:
            modules = self.modules

        modules_x = [m._final_x for m in modules]
        modules_right = [m.right.value for m in modules]

        xmin = min(modules_x)
        xmax = max(modules_right)

        assert xmax >= xmin

        return xmax-xmin

    def group_height(self, modules=None):
        """Compute the height of the group based on the module inside the group.
        group modules should have been positionned prior to compute the
        group_size.

        return the computed height
        """

        if modules is None:
            modules = self.modules

        modules_y = [m._final_y for m in modules]
        modules_bottom = [m.bottom.value for m in modules]

        ymin = min(modules_y)
        ymax = max(modules_bottom)

        assert ymax >= ymin

        return ymax-ymin

    def xmin(self, modules=None):
        """Get the minimum horizontal direction of the group.
        group_modules should be positionned first.
        """

        if modules is None:
            modules = self.modules

        return min((m._final_x for m in modules))

    def xmax(self, modules=None):
        """Get the maximum horizontal direction of the group.
        group_modules should be positionned first.
        """

        if modules is None:
            modules = self.modules

        return max((m._final_x for m in modules))

    def ymin(self, modules=None):
        """Get the minimum vertical direction of the group.
        group_modules should be positionned first.
        """

        if modules is None:
            modules = self.modules

        return min((m._final_y for m in modules))

    def ymax(self, modules=None):
        """Get the maximum vertical direction of the group.
        group_modules should be positionned first.
        """

        if modules is None:
            modules = self.modules

        return max((m._final_y for m in modules))

    def __enter__(self):

        # Set the curwidth to the width of the group if it set to a numerial value
        curslide = Store.get_current_slide()
        if curslide is not None:
            self._old_curslide_width = curslide.curwidth
            self._old_curslide_height = curslide.curheight

            if self.width.is_defined:
                curslide.curwidth = self.width.value

            if self.height.is_defined:
                curslide.curheight = self.height.value

        return self

    def __exit__(self, otype, ovalue, otraceback):

        # Convert string layer and check group module layers consistancy
        self.check_modules_layers()

        # Render the group
        self.render()

        # Update the group layers
        self.update_group_layers()

        # Restore parent group in the Store
        if isinstance(self.parent, group):
            Store.set_group(self.parent)
        else:
            Store.set_group(None)

        # Restore curwidth and curheight
        curslide = Store.get_current_slide()
        if curslide is not None:
            curslide.curwidth = self._old_curslide_width
            curslide.curheight = self._old_curslide_height

    def check_modules_layers(self):
        """
        Function to check the consistency of layers in the slide.
        To do so:

        1- Get the number of layers

        2- Resolve string layers to replace 'max' statement with the slide number of layer
           expl: 'range(0-max-1)' or '[0,max]'

        3- Check that layers are consecutive numbers from 0 -> max
        """

        self.group_num_layers = get_maximum_layer(self.modules)
        self.layers_in_group = unique_layers(self.modules,
                                             self.group_num_layers,
                                             check_consistancy=False)
        _log.debug('List of layers %s ' % str(self.layers_in_group))

    def update_group_layers(self):
        """Update the layer of modules inside the group to add the minimum value
        of the group layer.
        At the end set the group.layers to unique layers in the group
        """

        #  Find the minimum layer of the current group
        #  Check the type of layer for the group
        if isinstance(self.layers, str):
            # If it's type "range(min,'max',step)" extract the min of the range using regexp
            if self.parent is not None:
                maxlayer = get_maximum_layer(self.parent.modules)
            else:
                # When the parent is None (group outside of slide or an
                # other group), the minimum layer is 0
                maxlayer = 0

            group_layers = stringlayers_to_int(self.layers, maxlayer)
        else:
            group_layers = self.layers

        min_layer = min(group_layers)

        # Add this minimum to all layers inside the group
        all_layers = []
        for module in self.modules:
            tmp_layers = [l+min_layer for l in module.layers]

            # Add group layers not defined in the module
            for l in group_layers:
                if l not in tmp_layers and l > max(tmp_layers):
                    tmp_layers += [l]

            # Update this to the module layers list
            tmp_layers = sorted(set(tmp_layers))
            module.add_layers(tmp_layers)
            all_layers += tmp_layers

        # Update the group layer to list of uniq and sorted module layers
        new_group_layers = sorted(set(all_layers))
        self.add_layers(new_group_layers)

    def change_module_position(self, current_pos: int, destination_pos: int):
        '''
        Move the module in the list of modules of the slide. This also update
        the id_modules_auto_x, and id_modules_auto_y lists

        Parameters:

        - current_pos: int,
            The position of the module to be moved

        - destination_pos: int,
            The position to move the module to
        '''

        # remove the module
        cur_module = self.modules_order.pop(current_pos)
        # add it to it's new position
        self.modules_order.insert(destination_pos, cur_module)
