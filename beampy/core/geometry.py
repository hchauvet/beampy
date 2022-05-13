# -*- coding: utf-8 -*-
"""
Part of beampy project.

Placement class for relative placement of elements in slides
"""
from beampy.core.store import Store
from beampy.core.functions import convert_unit
from beampy.core.delayedoperations import Delayed
import operator
import sys

#Default dict for positioning alignement
DEFAULT_X = {'align': 'left', 'reference': 'slide', 'shift': 0,
             'unit': 'width', 'anchor': 'left'}
DEFAULT_Y = {'align': 'top', 'reference': 'slide', 'shift': 0,
             'unit': 'height', 'anchor': 'top'}


#Define function for alignement shortcuts.
def center(shift=0):

    out = {'anchor': 'center', 'shift': shift}

    return out


def top(shift=0):

    out = {'anchor': 'top', 'shift': shift}

    return out


def bottom(shift=0):

    out = {'anchor': 'bottom', 'shift': shift}

    return out


def right(shift=0):

    out = {'anchor': 'right', 'shift': shift}

    return out


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
        sumheight = sumheight.value

        if sumheight > available_size:
            print('Warning alignement elements overflow given height %s'%(available_size))

        available_space = (available_size - offset) - sumheight
        dy = available_space/float( len(all_height) + 1 )

        curpos = dy + offset

        for elemt in element_list:

            if curslide is None:
                elem = elemt
            else:
                elem = curslide.contents[elemt]

            H = elem.positionner.height.value

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
        sumwidth = sumwidth.value

        if sumwidth > available_size:
            print('Warning alignement elements overflow given width %s'%(available_size))

        available_space = (available_size - offset) - sumwidth
        dx = available_space/float(len(all_width)+1)

        curpos = dx + offset
        for elemt in element_list:

            if curslide is None:
                elem = elemt
            else:
                elem = curslide.contents[elemt]

            W = elem.positionner.width.value

            elem.positionner.x['shift'] = curpos
            elem.positionner.x['unit'] = 'px'
            elem.positionner.x['align'] = 'left'

            curpos += dx + W


class Position():
    """Define Position and operation on position, allow deferred operation
    """

    def __init__(self, beampymodule, value, axis='x'):
        """Create a Position object with a given value.

        Parameters
        ----------

        - beampymodule, object:
            The beampy module which use this Length.

        - value, int or float or str:
            The initial value of the length. could be a string with physical unit.

        - axis, str in ['x' or 'y'] (optional):
            The direction of this position (default: 'x'). Is used to convert
            position given as percentage, to select the width ('x') or height ('y').
        """

        self._value = value
        self.bpmodule = beampymodule
        self.axis = axis

    def converter(self, value):
        """Convert the position to a numerical value.

        Different case for value parameter:

        - Position instance: return it's value as a raw value for % to be computed when needed
        - string:
            - ends with '%': convert with the curwidth, or curheight depending
              on the axis
            - 'XXcm' : convert units to pixel
        - float:
            - > 1.0 use the value
            - < 1.0 convert with the curwidth or curheight depending
                on the axis
        - list or tupple:
            - use the first (when axis == 'x') or the second (when axis == 'y')
        """
        if isinstance(value, (Position, Length)):
            #  For position don't trigger the computation, this is done by 
            #  the compute_position methods of beampy_module class
            value = value._value

        if isinstance(value, (list, tuple)):
            if self.axis == 'x':
                value = value[0]
            if self.axis == 'y':
                value = value[1]

        if isinstance(value, str):

            # Manage the X% size with local size or default width/height of the theme
            if value.endswith('%'):
                value = relative_length(value, self.axis)
            elif value == 'center':
                value = center_on_available_space(self)
            else:
                value = convert_unit(value)

            assert isinstance(value, (int, float)), f"I was unable to convert your position {type(value)} to a number!"

        elif isinstance(value, float):
            if value < 1.0 and value > 0:
                value = int(round(relative_length(value, self.axis), 0))
            else:
                value = int(round(value, 0))

        return value

    @property
    def value(self):
        """Get the value, compute it if needed()
        """
        if isinstance(self._value, Delayed):
            try:
                res = self._value.compute()
            except Exception as e:
                print('Unable to compute value for module', self.bpmodule)
                print('ERROR:')
                print(e)
        else:
            res = self.converter(self._value)

        return res

    @value.setter
    def value(self, nvalue):
        self._value = nvalue

    @property
    def raw_value(self):
        """Return the raw value stored in _value withour triggering the
        computation.
        """
        return self._value

    @property
    def is_relative(self):
        """Return True if the raw value is type(str) and ends with %
        """

        if isinstance(self.raw_value, str) and self.raw_value.endswith('%'):
            return True

        if isinstance(self.raw_value, float) and self.raw_value <= 1 and self.raw_value > 0:
            return True

        return False

    @property
    def relative_value(self):
        """Return the relative value as a float
        """

        if self.is_relative:
            if isinstance(self.raw_value, str):
                return float(self.raw_value.replace('%', ''))/100

            return self.raw_value
        else:
            raise ValueError("This Position is not a relative position %s" % self.raw_value)

    @property
    def is_defined(self):
        """Return true or false if the _value is None or other
        """
        if self._value is None:
            return False

        return True
    
    def __add__(self, newvalue):
        res = Delayed(operator.add, self.converter)(self, newvalue)
        return Position(self.bpmodule, res, self.axis)

    def __radd__(self, newvalue):
        res = Delayed(operator.add, self.converter)(newvalue, self)
        return Position(self.bpmodule, res, self.axis)

    def __sub__(self, newvalue):
        res = Delayed(operator.sub, self.converter)(self, newvalue)
        return Position(self.bpmodule, res, self.axis)

    def __rsub__(self, newvalue):
        res = Delayed(operator.sub, self.converter)(newvalue, self)
        return Position(self.bpmodule, res, self.axis)

    def __mul__(self, newvalue):
        res = Delayed(operator.mul, self.converter)(self, newvalue)
        return Position(self.bpmodule, res, self.axis)

    def __rmul__(self, newvalue):
        res = Delayed(operator.mul, self.converter)(newvalue, self)
        return Position(self.bpmodule, res, self.axis)

    def __truediv__(self, newvalue):
        res = Delayed(operator.truediv, self.converter)(self, newvalue)
        return Position(self.bpmodule, res, self.axis)

    def __rtruediv__(self, newvalue):
        res = Delayed(operator.truediv, self.converter)(newvalue, self)
        return Position(self.bpmodule, res, self.axis)

    def __repr__(self):
        return f'{self._value}'

    def __eq__(self, other):
        return self._value == other


class Length():
    """Define length and operation on length, allow deferred operation
    """

    def __init__(self, value, axis='x'):
        """Create a Length object with a given value.

        Parameters
        ----------

        - value, int or float or str:
            The initial value of the length. could be a string with physical unit.

        - axis, str in ['x' or 'y'] (optional):
            The direction of this position (default: 'x'). Is used to convert
            position given as percentage, to select the width ('x') or height ('y').

        """

        self._value = value
        self.axis = axis
        self._cached_result = None

    def converter(self, value):
        """Convert the position to a numerical value.

        Different case for value parameter:

        - Position instance: return it's value
        - string:
            - ends with '%': convert with the curwidth, or curheight depending on the axis
            - 'XXcm' : convert units to pixel
        """

        if isinstance(value, (Length, Position)):
            # trigger the computation of the value
            value = value.value

        if isinstance(value, str):

            # Manage the X% size with local size or default width/height of the theme
            if value.endswith('%'):
                value = relative_length(value, self.axis)
            else:
                value = convert_unit(value)

            assert isinstance(value, (int, float)), f"I was unable to convert your length {type(value)} to a number!"

        elif isinstance(value, float):
            if value <= 1.0 and value > 0:
                value = int(round(relative_length(value, self.axis), 0))
            else:
                value = int(round(value, 0))

        return value

    @property
    def value(self):
        """Get the value, compute it if needed()
        """

        if isinstance(self._value, Delayed):
            if self._cached_result is None:
                # print('-> compute length', self._cached_result)
                self._cached_result = self._value.compute()

            res = self._cached_result
        else:
            res = self.converter(self._value)

        return res

    @value.setter
    def value(self, nvalue):
        self._value = nvalue
        self._cached_result = None

    @property
    def raw_value(self):
        """Return the raw value stored in _value withour triggering the
        computation.
        """
        return self._value

    @property
    def is_relative(self):
        """Return True if the raw value is type(str) and ends with %
        """

        if isinstance(self.raw_value, str) and self.raw_value.endswith('%'):
            return True

        if isinstance(self.raw_value, float) and self.raw_value <= 1 and self.raw_value > 0:
            return True

        return False

    @property
    def relative_value(self):
        """Return the relative value as a float
        """

        if self.is_relative:
            if isinstance(self.raw_value, str):
                return float(self.raw_value.replace('%', ''))/100

            return self.raw_value
        else:
            raise ValueError("This length is not a relative length %s" % self.raw_value)

    @property
    def is_defined(self):
        """Return True if self._value is not None
        """

        if self._value is None:
            return False

        return True

    def __add__(self, newvalue):
        res = Delayed(operator.add, self.converter)(self, newvalue)
        return Length(res, self.axis)

    def __radd__(self, newvalue):
        res = Delayed(operator.add, self.converter)(newvalue, self)
        return Length(res, self.axis)

    def __sub__(self, newvalue):
        res = Delayed(operator.sub, self.converter)(self, newvalue)
        return Length(res, self.axis)

    def __rsub__(self, newvalue):
        res = Delayed(operator.sub, self.converter)(newvalue, self)
        return Length(res, self.axis)

    def __mul__(self, newvalue):
        res = Delayed(operator.mul, self.converter)(self, newvalue)
        return Length(res, self.axis)

    def __rmul__(self, newvalue):
        res = Delayed(operator.mul, self.converter)(newvalue, self)
        return Length(res, self.axis)

    def __truediv__(self, newvalue):
        res = Delayed(operator.truediv, self.converter)(self, newvalue)
        return Length(res, self.axis)

    def __rtruediv__(self, newvalue):
        res = Delayed(operator.truediv, self.converter)(newvalue, self)
        return Length(res, self.axis)

    def __repr__(self):
        return f'{self._value}'

    def __eq__(self, other):
        return self._value == other


def relative_length(length, axis='x', fallback_size=(1280, 720)):
    """Compute relative length, and return it's value in pixel.

    Parameters:
    -----------

    - length, str or float:
        The relative length to compute, should en with % or be lower than 1.0 if
        given as a float.

    - axis, str in ['x', 'y'] (optional):
        The direction 'x' = 'width' and 'y' = 'heigth' used to compute the
        finale size. (the default is 'x')

    - fallback_size, list of int (optional):
        The size used when their is no current width/height available (i.e. when
        a module are created outside of a slide). (default is (1280, 720))
    """

    assert axis in ['x', 'y'], "Axis should be 'x' or 'y'"
    assert len(fallback_size) == 2, "Fallback size should be (xx, xx) with xx an int"

    # Get the availale space
    if axis == 'x':
        if Store.get_current_slide_id() is None:
            if Store.isgroup() and Store.group().width.is_defined:
                if Store.group().width.is_relative:
                    space = Store.group().width.relative_value
                    space *= fallback_size[0]
                else:
                    space = Store.group().width.value
            else:
                space = fallback_size[0]
                print('TODO: read Theme layout width, use fallback %i' % space)
        else:
            if Store.isgroup() and Store.group().width.is_defined:
                if Store.group().width.is_relative:
                    space = Store.group().width.relative_value
                    space *= Store.get_current_slide().curwidth
                else:
                    space = Store.group().width.value
            else:
                space = Store.get_current_slide().curwidth
    else:
        if Store.get_current_slide_id() is None:
            if Store.isgroup() and Store.group().height.is_defined:
                if Store.group().height.is_relative:
                    space = Store.group().height.relative_value
                    space *= fallback_size[1]
                else:
                    space = Store.group().height.value
            else:
                space = fallback_size[1]
                print('TODO: read Theme layout height, use fallback %i' % space)
        else:
            if Store.isgroup() and Store.group().height.is_defined:
                if Store.group().height.is_relative:
                    space = Store.group().height.relative_value
                    space *= fallback_size[1]
                else:
                    space = Store.group().height.value
            else:
                space = Store.get_current_slide().curheight

    if isinstance(length, str) and length.endswith('%'):
        ratio = float(length.replace('%', ''))/100.0
    elif isinstance(length, float) and length <= 1.0 and length > 0:
        ratio = length
    else:
        raise ValueError("Could not compute %s as a relative length" % length)

    out = int(ratio * space)

    return out


def center_on_available_space(position, fallback_size=(1280, 720)):
    """Function to center the given position of beampy_module on the avalaible
    space, either curwidth, curheight (or use the fallback_size).

    Parameters:
    -----------

    - Positions, Position object:
        The position to center

    - fallback_size, tuple or list of int:
        The size used if curwidth and curheight are not available.

    """

    if position.axis == 'x':
        if Store.get_current_slide_id() is None:
            if Store.isgroup() and Store.group().width.is_defined:
                space = Store.group().width.value
            else:
                space = fallback_size[0]
                print('TODO: read Theme layout width, use fallback %i' % space)
        else:
            if Store.isgroup() and Store.group().width.is_defined:
                space = Store.group().width.value
            else:
                space = Store.get_current_slide().curwidth

        out_pos = space/2 - position.bpmodule.width/2

    else:
        if Store.get_current_slide_id() is None:
            if Store.isgroup() and Store.group().height.is_defined:
                space = Store.group().height.value
            else:
                space = fallback_size[1]
                print('TODO: read Theme layout height, use fallback %i' % space)
        else:
            if Store.isgroup() and Store.group().height.is_defined:
                space = Store.group().height.value
            else:
                space = Store.get_current_slide().curheight

        out_pos = space/2 - position.bpmodule.height/2

    return out_pos.value


def horizontal_distribute(beampy_modules, available_space):
    """Equally distribute beampy_modules horizontally over the available space
    and update their x Position objects with a pixel position.

    Parameters:
    -----------

    - beampy_modules, list of beampy_module objects:
        Modules to be distributed horizontally.

    - available_space, int:
        The size available to compute the distance between two adjacent modules.
    """

    widths = [m.total_width for m in beampy_modules]

    total_width = sum(widths).value

    if total_width > available_space:
        print('Horizontal overflow of elements (%i px to distribute in %i)' % (total_width, available_space))

    dx = (available_space-total_width) if total_width <= available_space else 0
    dx = round(dx / (len(beampy_modules)+1), 0)

    beampy_modules[0].x = dx + beampy_modules[0].margin[3]
    for i, bpm in enumerate(beampy_modules[1:]):
        bpm.x = beampy_modules[i].right + dx + bpm.margin[3]


def vertical_distribute(beampy_modules, available_space):
    """Equally distribute beampy_modules vertically over the available space
    and update their y Position objects with a pixel position.

    Parameters:
    -----------

    - beampy_modules, list of beampy_module objects:
        Modules to be distributed vertically.

    - available_space, int:
        The size available to compute the distance between two adjacent modules.
    """

    heights = [m.total_height for m in beampy_modules]

    total_height = sum(heights).value

    if total_height > available_space:
        print('Vertical overflow of elements (%i px to distribute in %i)' % (total_height, available_space))

    dy = (available_space-total_height) if total_height <= available_space else 0
    dy = round(dy / (len(beampy_modules)+1), 0)

    beampy_modules[0].y = dy + beampy_modules[0].margin[0]
    for i, bpm in enumerate(beampy_modules[1:]):
        bpm.y = beampy_modules[i].bottom + dy + bpm.margin[0]



class Margins():

    def __init__(self, margins):
        """ 
        Convert a given margin into a list of 4 Length objects [top, right, bottom, left]

        Parameters:
        -----------

        - margin: int, float, str of a list of int, float, or str,
            When given as a simple number (int, float or str), the [top,
            right, bottom, left] margins will be equales.
            
            When given as a list of size 2, the left, right will be equal to the first
            number and the top, bottom to the second one.

            When given as a list of size 4, it will set each number to, [top,
            right, bottom, left]
        """

        self._init_margins = margins
        self._margins = None

        if isinstance(margins, (str, float, int)):
            self._margins = [Length(margins, 'y'), Length(margins, 'x')] * 2

        elif isinstance(margins, (list, tuple)):
            if len(margins) == 2:
                self._margins = [Length(margins[0], 'y'),
                                Length(margins[1], 'x')] * 2
            elif len(margins) == 4:
                self._margins = [Length(margins[0], 'y'),
                                Length(margins[1], 'x'),
                                Length(margins[2], 'y'),
                                Length(margins[3], 'x')]
            else:
                raise TypeError("The size of margin list should be 2 or 4, not %s" % len(margin))
        elif margins is None:
            # This allow theme set of the margin
            self._margins = None
        else:
            raise TypeError("The margin should be a list or a number or a string or None")

    def __len__(self):
        return 4

    def __getitem__(self, pos):
        return self._margins[pos].value

    @property
    def left(self):
        if self._margins is None:
            return None

        return self._margins[1].value

    @property
    def top(self):
        if self._margins is None:
            return None
            
        return self._margins[0].value

    @property
    def right(self):
        if self._margins is None:
            return None
            
        return self._margins[3].value

    @property
    def bottom(self):
        if self._margins is None:
            return None
            
        return self._margins[2].value

    @property
    def raw_value(self):
        return self._init_margins
