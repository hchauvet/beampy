#!/usr/bin/env python3

"""
Class that define beampy groups. It's a class that derives from module base class.
"""
from beampy.core.document import document
from beampy.core.geometry import distribute
from beampy.core.module import beampy_module
from beampy.core.functions import gcs
import sys

import logging
_log = logging.getLogger(__name__)


class group(beampy_module):
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
        self.content = []
        self.xoffset = 0
        self.yoffset = 0
        self.parentid = parentid # Store the id of the parent group
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
            slide = document._slides[gcs()]
        else:
            self.parent_slide_id = parent_slide_id
            slide = document._slides[self.parent_slide_id]

        if elements_to_group is not None:
            opengroup = False

        # Add the parentid if level is more than 1
        if slide.cur_group_level >= 0:
            self.parentid = slide.contents[slide.groupsid[slide.cur_group_level][-1]].id

        #slide.cur_group_level += 1
        self.grouplevel = slide.cur_group_level + 1
        if opengroup:
            slide.cur_group_level = self.grouplevel

        # Add classic register to the slide
        self.register(auto_render=False)
        self.group_id = self.id

        self.init_width = self.positionner.width.value
        self.init_height = self.positionner.height.value

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
        if document._slides[self.slide_id].cur_group_level != self.grouplevel:
            #print('Change cur_group_level')
            document._slides[self.slide_id].cur_group_level = self.grouplevel

        _log.debug('Enter a new group %s with level: %i' % (self.id,
                                                            self.grouplevel))

        # Set the id to of the current group to this group id
        document._slides[self.slide_id].cur_group_id = self.id
        # Check if we need to update the curwidth of slide
        if self.width.value is not None:
            document._slides[self.slide_id].curwidth = self.width.value
        else:
            self.width.value = document._slides[self.slide_id].curwidth

        # For the height check if a height is given in the group
        if self.height.value is not None:
            document._slides[self.slide_id].curheight = self.height.value

        return self

    def __exit__(self, type, value, traceback):
        _log.debug('Exit group %s' % self.id)
        if self.grouplevel >= 1:
            document._slides[self.slide_id].cur_group_level = self.grouplevel - 1

        # Check if we need to update the curwidth of slide to the parent group
        if self.parentid is not None and document._slides[self.slide_id].contents[self.parentid].width.value is not None:
            document._slides[self.slide_id].curwidth = document._slides[self.slide_id].contents[self.parentid].width.value

        # Check if we need to update the curheight of slide to the parent group
        if self.parentid is not None and document._slides[self.slide_id].contents[self.parentid].height.value is not None:
            document._slides[self.slide_id].curheight = document._slides[self.slide_id].contents[self.parentid].height.value

        # Get the id of the parentgroup as the cur_group_id
        document._slides[self.slide_id].cur_group_id = self.parentid

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
        slide = document._slides[self.slide_id]

        for eid in self.elementsid:
            # logging.debug('Element to propagate layer %s ' % str(slide.contents[eid].name))
            for layer in self.layers:
                if layer not in slide.contents[eid].layers and layer > min(slide.contents[eid].layers):
                    _log.debug('add layer %i to %s' % (layer, slide.contents[eid].name))
                    slide.contents[eid].layers += [layer]

            # Clean layer of elements lower than the minimum of group layer
            for elayer in slide.contents[eid].layers:
                if elayer < min(self.layers):
                    slide.contents[eid].layers.pop(slide.contents[eid].layers.index(elayer))

            # If the elements it's an group with should call the same method to do the recursion
            if slide.contents[eid].type == 'group':
                slide.contents[eid].propagate_layers()

    def add_elements_to_group(self, eid, element):
        #Function to register elements inside the group
        is_auto = False
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
