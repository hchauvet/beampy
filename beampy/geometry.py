# -*- coding: utf-8 -*-
"""
Part of beampy project.

Placement class for relative placement of elements in slides
"""
from beampy.functions import dict_deep_update, gcs, convert_unit
from beampy.document import document
import operator
import sys

DEFAULT_X = {'align': 'left', 'reference': 'slide', 'shift': 0, 'unit': 'width'}
DEFAULT_Y = {'align': 'top', 'reference': 'slide', 'shift': 0, 'unit': 'width'}

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
                reference: relative element for placement or 'slide' relative to slide
                shift: the value of the shift
                unit: 'width': relative to page (or group) width
                      'height': relative to page (or group) height
                      'cm', 'pt', 'px': shift value unit
        """

        #Create and id (positition in the dict of this element)
        self.id = elem_id
        try:
            self.id_index = document._slides[gcs()].element_keys.index(self.id)
        except:
            print('Element not found in document._content[gcs()]')
            self.id_index = -1 #Content not stored in slide contents (like group)

        self.width = width
        self.height = height


        #Make copy if x and y are dict input
        if type(x) == type(dict()):
            self.x = x.copy()
        else:
            self.x = x

        if type(y) == type(dict()):
            self.y = y.copy()
        else:
            self.y = y

        #print({"id":self.id,'y':self.y})
        #print(self.x)
        #Need to convert x, y to a standart dict
        self.convert_position()

        #Compute elements anchors
        self.compute_anchors()

    def update_size(self, width, height):
        """
            Update width and height to computed ones by the element render.
        """

        self.width = float(width)
        self.height = float(height)

    def compute_anchors(self):
        """
            Compute the anchors for the element self.left self.right self.top and self.bottom
        """

        #Bottom
        self.bottom = anchor('bottom', self.id)
        #top
        self.top = anchor('top', self.id)
        #left
        self.left = anchor('left', self.id)
        #right
        self.right = anchor('right', self.id)
        #center
        self.center = anchor('center', self.id)


    def convert_position(self):

        #Function to convert position of an element
        tmpx = DEFAULT_X.copy()
        tmpy = DEFAULT_Y.copy()
        slidects = document._slides[gcs()].contents

        #Get the previous content if it exist (to us "+xx" or "-yy" in x, y coords)
        if self.id_index > 0:
            prev_ct = slidects[document._slides[gcs()].element_keys[self.id_index - 1]]
        else:
            prev_ct = None

        #Check if x or y are only floats
        if type(self.x) == type(float()) or type(self.x) == type(int()):
            tmpx['shift'] = self.x

        elif type(self.x) == type(dict()):
            tmpx = dict_deep_update(tmpx, self.x)

        elif type(self.x) == type(str()):

            converted = False

            if '+' in self.x:
                self.x = convert_unit( self.x.replace('+','') )
                #Make relative placement
                if prev_ct != None:
                    dict_old = prev_ct['positionner'].right + float( self.x )
                    tmpx = dict_deep_update(tmpx, dict_old)
                else:
                    tmpx['shift'] = float( self.x )

                tmpx['unit'] = 'px'
                converted = True

            if '-' in self.x:
                self.x = convert_unit( self.x.replace('-','') )
                #Make relative placement
                if prev_ct != None:
                    dict_old = prev_ct.positionner.left - float( self.x )
                    tmpx = dict_deep_update(tmpx, dict_old)
                else:
                    tmpx['shift'] = float( self.x )
                tmpx['unit'] = 'px'
                converted = True


            if self.x in ['auto', 'center']:
                tmpx['shift'] = 0
                tmpx['align'] = self.x
                converted = True

            if not converted:
                try:
                    tmpx['shift'] = float( convert_unit(self.x) )
                    tmpx['unit'] = 'px'
                except:
                    print('[Error] x position is incorect string format')
                    print(self.x)

        else:
            print("[Error] x position need to be a float or a dict")


        if type(self.y) == type(float()) or type(self.y) == type(int()):
            tmpy['shift'] = self.y

        elif type(self.y) == type(dict()):
            tmpy = dict_deep_update(tmpy, self.y)

        elif type(self.y) == type(str()):

            converted = False
            if '+' in self.y:
                self.y = convert_unit( self.y.replace('+','') )
                #Make relative placement
                if prev_ct != None:
                    dict_old = prev_ct.positionner.bottom + float(self.y)
                    tmpy = dict_deep_update(tmpy, dict_old)
                else:
                    tmpy['shift'] = float( self.y )

                tmpy['unit'] = 'px'
                converted = True

            if '-' in self.y:
                self.y = convert_unit( self.y.replace('-','') )
                #Make relative placement
                if prev_ct != None :
                    dict_old = prev_ct.positionner.top - float(self.y)
                    tmpy = dict_deep_update(tmpy, dict_old)
                else:
                    tmpy['shift'] = float( self.y )
                tmpy['unit'] = 'px'
                converted = True

            if self.y in ['auto', 'center']:
                tmpy['shift'] = 0
                tmpy['align'] = self.y
                converted = True

            if not converted:
                try:
                    tmpy['shift'] = float( convert_unit(self.y) )
                    tmpy['unit'] = 'px'
                except:
                    print('[Error] y position is incorect string format')
                    print self.y
        else:
            print("[Error] y position need to be a float or an int or a dict")


        #Store the dict for positions
        self.x = tmpx
        self.y = tmpy

        #Convert position unit to pt
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

        #Container size
        available_width, available_height = available_size


        #Check if we need to compute the shift as a % of the container
        if available_width != None:
            if self.x['unit'] == 'width':
                self.x['shift'] *= available_width

            if self.y['unit'] == 'width':
                self.y['shift'] *= available_width

        if available_height != None:
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
                self.x['final'] = (available_width - self.width) - self.x['shift']

            if self.x['align'] == 'middle':
                self.x['final'] = self.x['shift'] + self.width/2.

        if self.y['reference'] == 'slide':
            if self.y['align'] == 'top':
                self.y['final'] = self.y['shift']

            if self.y['align'] == 'bottom':
                self.y['final'] = available_height - self.y['shift']

            if self.y['align'] == 'middle':
                self.y['final'] = self.y['shift'] + self.height/2.


        #Relative positionning
        if self.x['reference'] == 'relative':
            self.x['final'] = relative_placement(self.x['ref_id'], self.x, 'x')

            #add shift to match alignement of the object
            if self.x['align'] == 'right':
                self.x['final'] -= self.width

            if self.x['align'] == 'middle':
                self.x['final'] -= self.width/2.

        if self.y['reference'] == 'relative':
            self.y['final'] = relative_placement(self.y['ref_id'], self.y, 'y')

            if self.y['align'] == 'bottom':
                self.y['final'] -= self.height

            if self.y['align'] == 'middle':
                self.y['final'] -= self.height/2.

        #reduce number of floating values
        self.x['final'] = round( self.x['final'], 1 )
        self.y['final'] = round( self.y['final'], 1 )


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
        self.position = { "reference": "relative",
                      "ref_id": (self.element_id, self.slide_id),
                      "ref_anchor": self.type }

    def __add__(self, new_value):
        self.position['math'] = "+"
        self.parse_newvalue(new_value)

        return self.position.copy()

    def __sub__(self, new_value):
        self.position['math'] = "-"
        self.parse_newvalue( new_value )

        return self.position.copy()

    def parse_newvalue(self, new_value):
        """
            New_value can be a string like "+5cm" or a float 0.4 or a new dict
            like {"shift": 0, "align": 'left'}
        """
        #print(type(new_value))
        if type(new_value) == type(str()):
            self.position['shift'] = float( convert_unit(new_value) )
            self.position['unit'] = 'px'

        elif type(new_value) == type(float()) or type(new_value) == type(int()):
            self.position['shift'] = new_value

        elif type(new_value) == type(dict()):
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

    #get the relative element dict for the given axis
    if axis == 'x':
        oldpos = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.x

    if axis == 'y':
        oldpos = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.y

        #print("oldpos y", oldpos)

    oldwidth = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.width
    oldheight = document._slides['slide_%i'%prev_slide].contents[prev_elem].positionner.height

    if curpos['ref_anchor'] == 'left' and axis == 'x':
        newpos = op(oldpos['final'], curpos['shift'])

    if curpos['ref_anchor'] == 'right' and axis == 'x':
        newpos = op( (oldpos['final'] + oldwidth), curpos['shift'] )

    if curpos['ref_anchor'] == 'center':
        if axis == "x":
            newpos = op( (oldpos['final'] + oldwidth/2.), curpos['shift'] )

        if axis == "y":
            newpos = op( (oldpos['final'] + oldheight/2.), curpos['shift'] )

    if curpos['ref_anchor'] == 'top' and axis == 'y':
        newpos = op(oldpos['final'], curpos['shift'])

    if curpos['ref_anchor'] == 'bottom' and axis == 'y':
        newpos = op( (oldpos['final'] + oldheight), curpos['shift'] )

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
