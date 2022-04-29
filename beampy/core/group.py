#!/usr/bin/env python3

"""
Class that define beampy groups. It's a class that derives from module base class.
"""
from beampy.core.store import Store
from beampy.core.document import document
from beampy.core.content import Content
from beampy.core.geometry import (distribute, horizontal_distribute,
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

        # Store modules that need to be "automatically placed" inside the group
        self.id_modules_auto_x = []
        self.id_modules_auto_y = []
        if self.modules is None:
            self.modules = []

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

        print('group w,h', self.width, self.height)
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

        print('group w,h', self.width, self.height)

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
        if hasattr(self, 'data') and 'svgdef' in self.data:
            self.data['svgdef'] = svgin
        else:
            self.data = {'svgdef': svgin}

    def svguse(self, layer):
        """Rewrite the method for group, as it should take in consideration
        layers!
        """
        assert self._final_x is not None, f"{self.name} final X position is None for\n{self}"
        assert self._final_y is not None, f"final Y position is None for\n{self}"

        return f'<use x="{self._final_x}" y="{self._final_y}" xlink:href="#{self.content_id}_{self.slide_id}_{layer}"/>'

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
        if len(layer_divs)>0:
            divout = [f'<div id="group"',
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
        self.layers_in_group = unique_layers(self.modules, self.group_num_layers,
                                             check_consistancy=True)
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


class group_old(beampy_module):
    """Group Beampy modules together and manipulate them as a group

    Parameters
    ----------

    elements_to_group : None or list of beampy.base_module, optional
        List of Beampy module to put inside the group (the default is None).
        This argument allows to group Beampy modules, when `group` is not used
        with the python :py:mod:`with` expression.

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the group (the default is 'center'). See
        positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the group (the default is 'auto'). See
        positioning system of Beampy.

    width : int or float or None, optional
       Width of the group (the default is None, which implies that the width
       is computed to fit the group contents width).

    height : int or float or None, optional
       Height of the group (the default is None). When height is None the
       height is computed to fit the group contents height.

    background : str or None, optional
       Svg color name of the background color for the group (the default is None).

    perentid : str or None, optional
        Beampy id of the parent group (the default is None). This parentid is
        given automatically by Beampy render.


    .. note::

       When the position of a group (`x`, `y`) are relative to a parent group
       and that the parent group has `width`=None or `height`=None and
       positions `x` or `y` equal to 'auto' or 'center', the render will use
       the `slide.curwidth` as `width` and the `document._height` as height.
       This will produce unexpected positioning of child group.


    """

    def __init__(self, elements_to_group=None, x='center', y='auto',
                 width=None, height=None, background=None, parentid=None,
                 parent_slide_id=None, opengroup=True):

        # Store the input of the module
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background = background
        self.type = 'group'
        self.content = None
        self.xoffset = 0
        self.yoffset = 0
        self.grouplevel = 0

        # To store elements id to group
        self.elementsid = []
        # To store output ids for render (below/above)
        self.exports_id = []

        self.element_keys = []
        self.autoxid = []
        self.autoyid = []
        self.manualid = []
        self.htmlid = [] # Store html module id

        self.content_layer = {} # Store group rendered svg content by layers

        # Get the id of the slide
        if parent_slide_id is None:
            # slide = document._slides[gcs()]
            slide = Store.get_current_slide()
        else:
            self.parent_slide_id = parent_slide_id
            slide = Store.get_slide(self.parend_slide_id)
            #slide = document._slides[self.parent_slide_id]

        if elements_to_group is not None:
            opengroup = False

        # Add the parentid if level is more than 0
        if slide.cur_group_level >= 0:
            self.parentid = slide.contents[slide.groupsid[slide.cur_group_level][-1]].id

        #slide.cur_group_level += 1
        self.grouplevel = slide.cur_group_level + 1
        if opengroup:
            slide.cur_group_level = self.grouplevel

        # Add classic register to the slide
        super().__init__(self.x, self.y, self.width, self.height, None, self.type)
        #self.register(auto_render=False)
        self.group_id = self.id
        # Set the parent position
        if parentid is None:
            self.parentpos = self.get_position()

        self.init_width = self.width
        self.init_height = self.height

        if elements_to_group is not None:
            # print('TODO: Need to remove these elements from previous group!')
            for e in elements_to_group:
                #slide.remove_module(e.id)
                self.add_elements_to_group(e.id, e)

                if e.group_id is not None:
                    slide.contents[e.group_id].remove_element_in_group(e.id)

                e.group_id = self.id


    def reset_outputs(self):
        """
        Rewrite the reset_outputs function of beampy_module to add content_layer.
        """
        self.svgout = None  # The output of the render
        self.htmlout = None  # We can store also html peace of code
        self.jsout = None  # Store javascript if needed
        self.animout = None  # Store multiple rasters for animation
        self.rendered = False
        self.exported = False

        self.content_layer = {} #Remove group content_layer outputs

    def __enter__(self):
        # Is the slide group level correctly set?
        if Store.get_slide(self.slide_id).cur_group_level != self.grouplevel:
            #print('Change cur_group_level')
            Store.get_slide(self.slide_id).cur_group_level = self.grouplevel

        _log.debug('Enter a new group %s with level: %i' % (self.id,
                                                            self.grouplevel))

        # Set the id to of the current group to this group id
        Store.get_slide(self.slide_id).cur_group_id = self.id
        # Check if we need to update the curwidth of slide
        if self.width.is_defined:
            Store.get_slide(self.slide_id).curwidth = self.width.value
        else:
            self.width.value = Store.get_slide(self.slide_id).curwidth

        # For the height check if a height is given in the group
        if self.height.is_defined:
            Store.get_slide(self.slide_id).curheight = self.height.value

        return self

    def __exit__(self, type, value, traceback):
        _log.debug('Exit group %s' % self.id)
        if self.grouplevel >= 1:
            Store.get_slide(self.slide_id).cur_group_level = self.grouplevel - 1

        # Check if we need to update the curwidth of slide to the parent group
        if self.parentid is not None and Store.get_slide(self.slide_id).contents[self.parentid].width.is_defined:
            Store.get_slide(self.slide_id).curwidth = Store.get_slide(self.slide_id).contents[self.parentid].width.value

        # Check if we need to update the curheight of slide to the parent group
        if self.parentid is not None and Store.get_slide(self.slide_id).contents[self.parentid].height.is_defined:
            Store.get_slide(self.slide_id).curheight = Store.get_slide(self.slide_id).contents[self.parentid].height.value

        # Get the id of the parentgroup as the cur_group_id
        Store.get_slide(self.slide_id).cur_group_id = self.parentid

        _log.debug('Set current group level to %i'%document._slides[self.slide_id].cur_group_level)

        # Compute group size
        # self.compute_group_size()

    def add_layers(self, layerslist):
        self.layers = layerslist

    def propagate_layers(self):
        """
        Function to recusivly propagate the layers to group elements
        :return:
        """
        slide = Store.get_slide(self.slide_id)

        for eid in self.elementsid:
            # logging.debug('Element to propagate layer %s ' % str(slide.contents[eid].name))
            for layer in self.layers:
                if layer not in slide.modules[eid].layers and layer > min(slide.modules[eid].layers):
                    _log.debug('add layer %i to %s' % (layer, slide.modules[eid].name))
                    slide.modules[eid].layers += [layer]

            # Clean layer of elements lower than the minimum of group layer
            for elayer in slide.modules[eid].layers:
                if elayer < min(self.layers):
                    slide.modules[eid].layers.pop(slide.modules[eid].layers.index(elayer))

            # If the elements it's an group with should call the same method to do the recursion
            if slide.modules[eid].type == 'group':
                slide.modules[eid].propagate_layers()

    def add_elements_to_group(self, element):
        #Function to register elements inside the group
        is_auto = False
        eid = element.get_position()
        self.elementsid += [eid]
        self.exports_id += [eid]

        if element.x == 'auto':
            self.autoxid += [eid]
            is_auto = True

        if element.y == 'auto':
            self.autoyid += [eid]
            is_auto = True

        if not is_auto:
            self.manualid += [eid]

        if element.type == 'html':
            self.htmlid += [eid]

    def remove_element_in_group(self, elementid):
        """
        Function to remove element from the group key stores

        :param elementid: The id of the module to remove
        """

        for store in (self.autoxid, self.autoyid, self.manualid,self.htmlid, self.elementsid, self.exports_id):
            if elementid in store:
                store.pop(store.index(elementid))

    def add_svg_content(self, layer, svg):
        # create or append the content_layer store with the given svg

        if layer in self.content_layer:
            self.content_layer[layer] += [svg]
        else:
            self.content_layer[layer] = [svg]

        # Add layer level to group if it's not already created
        if layer not in self.layers:
            self.layers += [layer]

    def compute_group_size(self):
        """
        Function to compute the size of a given group

        Update the size with self.update_size(width, height) at the end
        """

        # Check group given size
        if self.init_width is None:
            auto_width = document._width
        else:
            auto_width = self.width.value

        if self.init_height is None:
            auto_height = document._height
        else:
            auto_height = self.height.value

        # First look at auto positionning for elements in groups
        # Check if their is autox or autoy placement
        if len(self.autoxid) > 0:
            distribute(self.autoxid, 'hspace', auto_width,
                       offset=self.xoffset,
                       curslide=document._slides[self.slide_id])

        if len(self.autoyid) > 0:
            distribute(self.autoyid, 'vspace', auto_height,
                       offset=self.yoffset,
                       curslide=document._slides[self.slide_id])

        # Place the module with these distributed postions
        for elem in self.autoxid + self.autoyid + self.manualid:
            # Check if the element have already be placed (html could be part of serveral groups level)
            if 'final' not in document._slides[self.slide_id].contents[elem].positionner.x:
                document._slides[self.slide_id].contents[elem].positionner.place((auto_width, auto_height),
                                                                                 self.yoffset)

        # Compute the real group size if no size (width or height) are given in group args
        if self.init_width is None :

            allxw = []

            for eid in self.elementsid:
                ewidth = document._slides[self.slide_id].contents[eid].positionner.width
                """
                # Should not happen
                if ewidth.value is None:
                    print('Run render from compute_group_size to get width')
                    ewidth.run_render()
                """

                ewidth = ewidth.value
                if ewidth is None:
                    print('Width not known for:')
                    print(document._slides[self.slide_id].contents[eid])
                    sys.exit(0)

                allxw += [(document._slides[self.slide_id].contents[eid].positionner.x['final'],
                           ewidth) ]

            minx = min([i[0] for i in allxw])
            maxx = max([i[0]+i[1] for i in allxw])

            width = maxx - minx
            # print('group width %f'%width)
            self.width.value = width

            # Need to reloop over groups elements to increment dx
            # as they have been positionned with slide width
            for eid in self.elementsid:
                document._slides[self.slide_id].contents[eid].positionner.x['final'] -= minx

        if self.init_height is None:

            allyh = []

            for eid in self.elementsid:

                eheight = document._slides[self.slide_id].contents[eid].height
                """
                # Should not happen
                if eheight.value is None:
                    print('Run render from compute_group_size to get height')
                    eheight.run_render()
                """
                eheight = eheight.value

                if eheight is None:
                    print('Height not known for:')
                    print(document._slides[self.slide_id].contents[eid])
                    sys.exit(0)

                allyh += [(document._slides[self.slide_id].contents[eid].positionner.y['final'],
                           eheight) ]

            miny = min([i[0] for i in allyh])
            maxy = max([i[0]+i[1] for i in allyh])
            height = maxy - miny
            # print('group height %f'%height)
            self.height.value = height

            # Need to reloop over groups elements to increment dy
            # as they have been positionned with slide height
            for eid in self.elementsid:
                document._slides[self.slide_id].contents[eid].positionner.y['final'] -= miny

        self.update_size(self.width, self.height)

    def render(self):
        """
            group render
        """

        slide = document._slides[self.slide_id]
        self.content = []

        # Loop over these elements id to export their svg code
        for eid in self.exports_id:

            elem = slide.contents[eid]

            if elem.type == 'group':
                for layer in elem.layers:
                    if layer in elem.content_layer:
                        self.add_svg_content(layer, elem.export_svg_layer(layer))

            else:
                if elem.svgout is not None:
                    if not elem.exported:
                        if elem.type == 'html':
                            if document._output_format != 'html5':
                                slide.add_rendered(svgdefs=elem.export_svg_def())
                                elem.exported = True
                        else:
                            slide.add_rendered(svgdefs=elem.export_svg_def())
                            elem.exported = True

                    for layer in elem.layers:
                        # Check if it's an html element, we need to only output svg for svg format not html
                        if elem.type == 'html':
                            if document._output_format != 'html5':
                                self.add_svg_content(layer, '<use xlink:href="#{id}"></use>'.format(id=elem.id))
                        else:
                            self.add_svg_content(layer, '<use xlink:href="#{id}"></use>'.format(id=elem.id))

            if elem.jsout is not None:
                slide.add_rendered(js=elem.jsout)

            if elem.animout is not None and document._output_format == 'html5':
                if not elem.exported:
                    tmpanim = elem.export_animation()
                    slide.add_rendered(animate_svg=tmpanim)
                    elem.exported = True

                for layer in elem.layers:
                    self.add_svg_content(layer, elem.export_animation_layer(layer))


            # For html objects, they need absolute positionning because they are not included in svg group
            if elem.type == 'html' and elem.htmlout is not None and self.grouplevel > 0:
                # Store the group_id that contains this html
                elem.groups_id += [self.id]
                # remove auto/center args from x and y
                elem.x = '%ipx'%elem.positionner.x['final']
                elem.y = '%ipx'%elem.positionner.y['final']
                # Add the element to the parentgroup
                slide.contents[self.parentid].add_elements_to_group(elem.id, elem)

        self.rendered = True

    def export_svg_content_layer(self, layer):
        """
        Function to export group content for a given layer to svg
        :param layer:
        :return:
        """

        if self.background is not None:
            pre_rect = '<rect width="%s" height="%s" style="fill:%s;" />'%(self.width.value,
             self.height.value, self.background)
        else:
            pre_rect = ''

        output = pre_rect + ''.join(self.content_layer[layer])

        return output

    def export_svg_layer(self, layer):

        out = '<g transform="translate(%s,%s)" class="%s" data-layer="%i">' % (self.positionner.x['final'],
                                                                               self.positionner.y['final'],
                                                                               self.name, layer)

        out += self.export_svg_content_layer(layer)

        if document._text_box:
            out += """<rect x="0"  y="0" width="%s" height="%s"
              style="stroke:#009900;stroke-width: 1;stroke-dasharray: 10 5;
              fill: none;" />""" % (self.positionner.width.value,
                                    self.positionner.height.value)

        if self.svg_decoration != '':
            out += self.svg_decoration.format(width=self.positionner.width.value,
                                              height=self.positionner.height.value)

        out += '</g>'

        return out
