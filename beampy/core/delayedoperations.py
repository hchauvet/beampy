#!/usr/bin/env python3

"""
Build a class which allows to do delayed operation in Python
"""
import operator

class Delayed():
    """Perform delayed operation (defined in python operator) with recursion.
    A converter function could be used to convert the argmument of operation
    function.

    Exemple
    -------

    a = Delayed(operator.add)(5, 6)
    res = a.compute()

    b = a + 10 / 5
    print(b)
    res = b.compute()
    """

    def __init__(self, function, converter=None):
        """Define the delayed object

        Parameters
        ----------

        function: python callable
            The function to be used when compute is called

        converter: python callable (optional)
            The function used to convert each arguments of the function before
            send them to the function.
        """

        self.function = function
        self.converter = converter
        self.args = None

    def __call__(self, left, right):
        """Argument to be called with the defined self.function

        Parameters:
        -----------

        - left: any
             The left argument of the operation
        - right: any
             The right argument of the operation
        """

        self.left = left
        self.right = right

        return self
    
    def compute(self):
        """Run the operation on the left and right
        """

        left = self.left
        right = self.right

        # Do the recursion
        if isinstance(left, Delayed):
            left = left.compute()
        if isinstance(right, Delayed):
            right = right.compute()

        # Convert left and right
        if self.converter is not None:
            left = self.converter(left)
            right = self.converter(right)

        res = self.function(left, right)

        # Check if the result is still a delayed function
        if isinstance(res, Delayed):
            res = res.compute()

        return res

    def __add__(self, newvalue):
        return Delayed(operator.add, self.converter)(self, newvalue)

    def __radd__(self, newvalue):
        return Delayed(operator.add, self.converter)(newvalue, self)
    
    def __sub__(self, newvalue):
        return Delayed(operator.sub, self.converter)(self, newvalue)

    def __rsub__(self, newvalue):
        return Delayed(operator.sub, self.converter)(newvalue, self)

    def __mul__(self, newvalue):
        return Delayed(operator.mul, self.converter)(self, newvalue)

    def __rmul__(self, newvalue):
        return Delayed(operator.mul, self.converter)(newvalue, self)

    def __truediv__(self, newvalue):
        return Delayed(operator.truediv, self.converter)(self, newvalue)

    def __rtruediv__(self, newvalue):
        return Delayed(operator.truediv, self.converter)(newvalue, self)

    def __repr__(self):

        op = '?'
        op_table={'add': '+',
                  'truediv': '/',
                  'sub': '-',
                  'mul': '*'}

        opname = self.function.__name__.replace('__', '')
        if opname in op_table:
            op = op_table[opname]

        lv = self.left
        rv = self.right

        return f'({lv} {op} {rv})'
