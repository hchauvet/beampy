# -*- coding: utf-8 -*-
"""
Part of beampy project.

Placement class for relative placement of elements in slides
"""
from beampy.functions import dict_deep_update, gcs, convert_unit
from beampy.document import document
import operator
import sys

#Default dict for positioning alignement
DEFAULT_X = {'align': 'left', 'reference': 'slide', 'shift': 0,
             'unit': 'width', 'anchor': 'left'}
DEFAULT_Y = {'align': 'top', 'reference': 'slide', 'shift': 0,
             'unit': 'width', 'anchor': 'top'}


#Define function for alignement shortcuts.
def center(shift=0):

    out = {'anchor': 'middle', 'shift': shift}

    if isinstance(shift, str):
        out['shift'] = float(convert_unit(shift))
        out['unit'] = 'px'

    return out


def top(shift=0):

    out = {'anchor': 'top', 'shift': shift}

    if isinstance(shift, str):
        out['shift'] = float(convert_unit(shift))
        out['unit'] = 'px'

    return out


def bottom(shift=0):

    out = {'anchor': 'bottom', 'shift': shift}

    if isinstance(shift, str):
        out['shift'] = float(convert_unit(shift))
        out['unit'] = 'px'

    return out


def right(shift=0):

    out = {'anchor': 'right', 'shift': shift}

    if isinstance(shift, str):
        out['shift'] = float(convert_unit(shift))
        out['unit'] = 'px'

    return out


class positionner():

    def __init__(self, x, y, width, height, elem_id):
        """
            This class need position x and y of the element

            width and height is the size of the svg or html object (need to be
            updated after rendering)

            x, y: could be a dict, a float or a string

            Default position dict:
            ======================

                {'align': 'left', 'reference': 'slide', 'shift': 0, 'unit': 'rel'}

                align: define the alignement for the coordinate
                       ('center' (page centering),'left','right','middle',
                       'top','bottom')
                reference: 'relative' element for placement or 'slide' relative to slide
                           'slide' for placement refenreced on slide
                shift: the value of the shift
                unit: 'width': relative to page (or group) width
                      'height': relative to page (or group) height
                      'cm', 'pt', 'px': shift value unit
                anchor: 'left', 'right', 'middle', 'top', 'bottom', define the anchor on the object bounding-box
        """

        # Create and id (positition in the dict of this element)
        self.id = elem_id
        self.slideid = gcs()
        try:
            self.id_index = document._slides[self.slideid].element_keys.index(self.id)
        except IndexError:
            print('Element not found in document._content[gcs()].element_keys')
            self.id_index = -1

        self.update_size(width, height)

        # Make copy if x and y are dict input
        if type(x) == type(dict()):
            self.x = x.copy()
        else:
            self.x = x

        if type(y) == type(dict()):
            self.y = y.copy()
        else:
            self.y = y

        # print({"id":self.id,'y':self.y})
        # print(self.x)
        # Need to convert x, y to a standart dict
        self.convert_position()

        # Compute elements anchors
        self.compute_anchors()

    def update_size(self, width, height):
        """
            Update width and height to computed ones by the element render.

            If width is less than 1px, use it as a percentage of the width
        """

        try:
            self.width = float(width)
        except:
            self.width = None

        try:
            self.height = float(height)
        except:
            self.height = None

        if self.width is not None and self.width < 1.0:
            self.width *= document._width

    def compute_anchors(self):
        """
            Compute the anchors for the element self.left self.right self.top and self.bottom
        """

        # Bottom
        self.bottom = anchor('bottom', self.id)
        # top
        self.top = anchor('top', self.id)
        # left
        self.left = anchor('left', self.id)
        # right
        self.right = anchor('right', self.id)
        # center
        self.center = anchor('center', self.id)

    def convert_position(self):

        # Function to convert position of an element
        tmpx = DEFAULT_X.copy()
        tmpy = DEFAULT_Y.copy()
        slidects = document._slides[self.slideid].contents

        # Get the previous content if it exist (to us "+xx" or "-yy" in x, y coords)
        if self.id_index > 0:
            prev_ct = slidects[document._slides[self.slideid].element_keys[self.id_index - 1]]
        else:
            prev_ct = None

        # Check if x or y are only floats
        if isinstance(self.x, float) or isinstance(self.x, int):
            tmpx['shift'] = self.x

        elif isinstance(self.x, dict):
            tmpx = dict_deep_update(tmpx, self.x)

        elif isinstance(self.x, str):

            converted = False

            if '+' in self.x:
                self.x = convert_unit(self.x.replace('+', ''))
                # Make relative placement
                if prev_ct is not None:
                    dict_old = prev_ct.positionner.right + float(self.x)
                    tmpx = dict_deep_update(tmpx, dict_old)
                else:
                    tmpx['shift'] = float(self.x)

                tmpx['unit'] = 'px'
                converted = True

            if '-' in self.x:
                self.x = convert_unit(self.x.replace('-', ''))
                # Make relative placement
                if prev_ct is not None:
                    dict_old = prev_ct.positionner.left - float(self.x)
                    tmpx = dict_deep_update(tmpx, dict_old)
                else:
                    tmpx['shift'] = float(self.x)
                tmpx['unit'] = 'px'
                converted = True


            if self.x in ['auto', 'center']:
                tmpx['shift'] = 0
                tmpx['align'] = self.x
                converted = True

            if not converted:
                try:
                    tmpx['shift'] = float(convert_unit(self.x))
                    tmpx['unit'] = 'px'
                except:
                    print('[Error] x position is incorect string format')
                    print(self.x)

        else:
            print("[Error] x position need to be a float or a dict")

        if isinstance(self.y, float) or isinstance(self.y, int):
            tmpy['shift'] = self.y

        elif isinstance(self.y, dict):
            tmpy = dict_deep_update(tmpy, self.y)

        elif isinstance(self.y, str):

            converted = False
            if '+' in self.y:
                self.y = convert_unit(self.y.replace('+', ''))
                # Make relative placement
                if prev_ct is not None:
                    dict_old = prev_ct.positionner.bottom + float(self.y)
                    tmpy = dict_deep_update(tmpy, dict_old)
                else:
                    tmpy['shift'] = float(self.y)

                tmpy['unit'] = 'px'
                converted = True

            if '-' in self.y:
                self.y = convert_unit(self.y.replace('-', ''))
                # Make relative placement
                if prev_ct is not None:
                    dict_old = prev_ct.positionner.top - float(self.y)
                    tmpy = dict_deep_update(tmpy, dict_old)
                else:
                    tmpy['shift'] = float(self.y)
                tmpy['unit'] = 'px'
                converted = True

            if self.y in ['auto', 'center']:
                tmpy['shift'] = 0
                tmpy['align'] = self.y
                converted = True

            if not converted:
                try:
                    tmpy['shift'] = float(convert_unit(self.y))
                    tmpy['unit'] = 'px'
                except:
                    print('[Error] y position is incorect string format')
                    print(self.y)

        else:
            print("[Error] y position need to be a float or an int or a dict")


        # Store the dict for positions
        self.x = tmpx
        self.y = tmpy

        # Force unit to be pixel for x > 1
        if self.x['shift'] > 1.0 and self.x['unit'] in ('width', 'height'):
            self.x['unit'] = 'px'

        # Force unit to be pixel for y > 1
        if self.y['shift'] > 1.0 and self.y['unit'] in ('width', 'height'):
            self.y['unit'] = 'px'

        # Convert position unit to pt
        if self.x['unit'] in ['cm', 'pt', 'mm']:
            self.x['shift'] = float( convert_unit( '%f%s'%(self.x['shift'], self.x['unit']) ) )

        if self.y['unit'] in ['cm', 'pt', 'mm']:
            self.y['shift'] = float( convert_unit( '%f%s'%(self.y['shift'], self.y['unit']) ) )

        if type(self.width) == type(str()):
            self.width = float( convert_unit(self.width) )

        if type(self.height) == type(str()):
            self.height = float( convert_unit(self.height) )

    def place(self, available_size, ytop=0):
        """
            Method to place the given element. This method is used by renders.py in
            the place_content function

            available_size: (width, heith) is the page or group width and height

            ytop[default 0]: is the y offset (used to center verticaly taking into
                             account the title)

        """

        # Container size
        available_width, available_height = available_size


        # Check if we need to compute the shift as a % of the container
        if available_width is not None:
            if self.x['unit'] == 'width':
                self.x['shift'] *= available_width

            if self.y['unit'] == 'width':
                self.y['shift'] *= available_width

        if available_height is not None:
            if self.x['unit'] == 'height':
                self.x['shift'] *= available_height

            if self.y['unit'] == 'height':
                self.y['shift'] *= available_height

        #Centering element on slide or group
        if self.x['align'] == 'center':
            self.x['final'] = element_centering(self.width, available_width) + self.x['shift']

        if self.y['align'] == 'center':
            self.y['final'] = element_centering(self.height,
                                                available_height - ytop,
                                                pos_init=ytop) + self.y['shift']

        #Place element that are aligned left 
        if self.x['reference'] == 'slide':
            if self.x['align'] == 'left':
                self.x['final'] = self.x['shift']

            if self.x['align'] == 'right':
                # self.x['final'] = (available_width - self.width) - self.x['shift']
                self.x['final'] = (available_width) - self.x['shift']

            if self.x['align'] == 'middle':
                self.x['final'] = self.x['shift'] + self.width/2.

        if self.y['reference'] == 'slide':
            if self.y['align'] == 'top':
                self.y['final'] = self.y['shift']

            if self.y['align'] == 'bottom':
                self.y['final'] = available_height - self.y['shift']

            if self.y['align'] == 'middle':
                self.y['final'] = self.y['shift'] + self.height/2.

        # Relative positioning
        if self.x['reference'] == 'relative':
            self.x['final'] = relative_placement(self.x['ref_id'], self.x, 'x')

        if self.y['reference'] == 'relative':
            self.y['final'] = relative_placement(self.y['ref_id'], self.y, 'y')

        #reduce number of floating values and set align and unit to top-left in pixel
        self.x['final'] = round(self.x['final'], 1)
        self.y['final'] = round(self.y['final'], 1)

        # Compute the shift due to object anchors
        if self.x['anchor'] == 'right':
            # print('right', self.width)
            self.x['final'] -= self.width

        if self.x['anchor'] == 'middle':
            # print('x middle', self.width)
            self.x['final'] -= self.width/2.0

        if self.y['anchor'] == 'bottom':
            # print('bottom', self.height)
            self.y['final'] -= self.height

        if self.y['anchor'] == 'middle':
            # print('y middle', self.height)
            self.y['final'] -= self.height/2.0

    def guess_size_for_group(self):
        """Function to guess parent group final position to place elements relatively
        to this group.
        """

        if 'final' not in self.x:
            if self.width is None:
                cur_width = document._slides[self.slideid].curwidth

                print('''Warning: Relative "x" placement to parent group without
                width could gives unexpected results. Width: %i is used.''' %
                      cur_width)

                self.width = cur_width

            if self.x == 'auto':
                print('''Warning: Relative "x" placement to a parent group with
                auto-positioning! This will lead to unexpected results!''')

        if 'final' not in self.y:
            if self.height is None:
                cur_height = document._height

                print('''Warning: Relative "y" placement to parent group without
                width could gives unexpected results. Width: %i is used.''' %
                      cur_height)

                self.height = cur_height

            if self.y == 'auto':
                print('''Warning: Relative "y" placement to a parent group with
                auto-positioning! This will lead to unexpected results!''')


class anchor:
    def __init__(self, atype, elem_id):
        """
            Define the anchor class:
            atype [top, left, bottom, center]
            elem_id the id of the current element
        """

        self.type = atype

        self.element_id = elem_id
        self.slide_id = document._global_counter['slide']
        #Create a new position dictionnary
        self.position = {"reference": "relative",
                         "ref_id": (self.element_id, self.slide_id),
                         "ref_anchor": self.type}

    def __add__(self, new_value):
        self.position['math'] = "+"
        self.parse_newvalue(new_value)

        return self.position.copy()

    def __sub__(self, new_value):
        self.position['math'] = "-"
        self.parse_newvalue(new_value)

        return self.position.copy()

    def parse_newvalue(self, new_value):
        """
            New_value can be a string like "+5cm" or a float 0.4 or a new dict
            like {"shift": 0, "align": 'left'}
        """
        #print(type(new_value))
        if isinstance(new_value, str):
            self.position['shift'] = float(convert_unit(new_value))
            self.position['unit'] = 'px'

        elif isinstance(new_value, float) or isinstance(new_value, int):
            self.position['shift'] = new_value

        elif isinstance(new_value, dict):
            self.position = dict_deep_update(new_value.copy(), self.position)

        else:
            print('Invalid relative coordinate type!')


def element_centering(object_size, container_size, pos_init=0):
    """
        Function to center and object on the container_size

        final position:
            pos_init + available_space/2
    """

    if container_size > object_size:
        available_space = (container_size - object_size)
        #print available_space, object_width
        pos_new = pos_init + (available_space/2)
    else:
        pos_new = pos_init

    return pos_new


def relative_placement(prev_element_id, curpos, axis):
    """
        Compute relative placement

        return final position on the given axis
    """

    prev_elem, prev_slide = prev_element_id
    #print({"prev_id":prev_elem,"prev_type": document._contents['slide_%i'%prev_slide]['contents'][prev_elem]['type']})

    #Add litteral operation : + or - in curpos['math']
    if curpos['math'] == '-':
        op = operator.sub
    else:
        op = operator.add


    # get the relative element dict for the given axis
    if axis == 'x':
        oldpos = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.x

    if axis == 'y':
        oldpos = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.y

    if 'final' not in oldpos:
        # Special case for group, try to guess the parent group width and height
        if document._slides['slide_%i'%prev_slide].contents[prev_elem].type == 'group':
            oldpos_final = 0
            document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.guess_size_for_group()
        else:
            raise ValueError('Relative placement error: \nReference element:\n%s\nThis element have no final position' %
                             str(document._slides['slide_%i' % prev_slide].contents[prev_elem])
                             )

    else:
        oldpos_final = oldpos['final']

    oldwidth = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.width
    oldheight = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.height

    if curpos['ref_anchor'] == 'left' and axis == 'x':
        newpos = op(oldpos_final, curpos['shift'])

    if curpos['ref_anchor'] == 'right' and axis == 'x':
        newpos = op((oldpos_final + oldwidth), curpos['shift'])

    if curpos['ref_anchor'] == 'center':
        if axis == "x":
            newpos = op((oldpos_final + oldwidth/2.), curpos['shift'])

        if axis == "y":
            newpos = op((oldpos_final + oldheight/2.), curpos['shift'])

    if curpos['ref_anchor'] == 'top' and axis == 'y':
        newpos = op(oldpos_final, curpos['shift'])

    if curpos['ref_anchor'] == 'bottom' and axis == 'y':
        newpos = op((oldpos_final + oldheight), curpos['shift'])

    return newpos


def align(positionner_list, alignement):
    """
        Function to align all given elements defined by their positionner.

        alignement:

        'left': align left
        'right': align right
        'xcenter': align center (verticaly)
        'ycenter': align center (horizontaly)
        'baseline': if all elements are text align their baseline
        'top': align top
        'bottom': align bottom

    """

    print('TODO')

def distribute(element_list, mode, available_size, offset=0, curslide=None):
    '''
        Distribute the given elements list along the slide using the given
        mode

        element_list:
            A list of beampy module (if curslide is none)
            A list of beampy module keys, in this case curslide must be the
            curent slide where module are stored


        mode:
            'hspace': horizontal spacing from the center of each elements
            'vspace': vertical spacing from the center of each elements

        offset:
            gives the first offset of the slide (due to the title for instance)

        curslide [None]:
            If curslide is not None the element_list must refers to elements keys
            surch that

            curslide.content[elemnt_list[0]] is a beampy module

    '''

    if mode == 'vspace':

        if curslide is None:
            all_height = [elem.positionner.height for elem in element_list]
        else:
            all_height = [curslide.contents[elemk].positionner.height for elemk in element_list]

        # print(all_height)
        sumheight = sum(all_height)

        if sumheight > available_size:
            print('Warning alignement elements overflow given height %s'%(available_size))

        available_space = (available_size - offset) - sumheight
        dy = available_space/float(len(all_height)+1)

        curpos = dy + offset
        for elemt in element_list:

            if curslide is None:
                elem = elemt
            else:
                elem = curslide.contents[elemt]

            H = elem.positionner.height

            elem.positionner.y['shift'] = curpos
            elem.positionner.y['unit'] = 'px'
            elem.positionner.y['align'] = 'top'

            curpos += dy + H

    elif mode == 'hspace':

        if curslide is None:
            all_width = [elem.positionner.width for elem in element_list]
        else:
            all_width = [curslide.contents[elemk].positionner.width for elemk in element_list]

        sumwidth = sum(all_width)

        if sumwidth > available_size:
            print('Warning alignement elements overflow given width %s'%(available_size))

        available_space = available_size - sumwidth
        dx = available_space/float(len(all_width)+1)

        curpos = dx
        for elemt in element_list:

            if curslide is None:
                elem = elemt
            else:
                elem = curslide.contents[elemt]

            W = elem.positionner.width

            elem.positionner.x['shift'] = curpos
            elem.positionner.x['unit'] = 'px'
            elem.positionner.x['align'] = 'left'

            curpos += dx + W
