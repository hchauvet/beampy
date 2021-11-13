#!/usr/bin/env python3

"""
Build a class which allows to do delayed operation in Python
"""
import operator

class DelayedOperations():
    """
    A class that will perform delayed operations.

    The class which use this class in it's operator methods (__add__, __sub__)
    need to implement the delayed version of this operations with the "d"
    prefix.

    Example:

    class MyThing():
        def __init__(self):
            self.value = 5

        def __dadd__(self, left, right):
            # Do the real operation
            return left + right

        def __add__(self, new):
            return DelayedOperations(self, self.__dadd__, self.value, new)


    aa = MyThing()

    cc = aa + 5 + aa/2

    result = cc.compute()

    """

    def __init__(self, cls, func, *args):
        self.cls = cls
        self.fun = [func]
        self.cpt_compute = 0
        self.args = list(args)

    def add_operation(self, newfunction, newvalue):
        """
        Add the operation defined by the newfunction and
        the newvalue to lists. Those lists will be used in compute method.
        """
        self.args += [newvalue]
        self.fun += [newfunction]

    def compute(self):
        """
        Perfome the stored operation and return the value defined in the parent
        class by prefixed __d methods (__dadd__, __dmul__, etc...)
        """
        left = self.args[0]
        right = self.args[1]
        self.backargs = self.args
        self.backfun = self.fun
        # args could be delayed class so we need to compute
        # them before using the operation function
        if isinstance(left, DelayedOperations):
            left = left.compute()
        if isinstance(right, DelayedOperations):
            right = right.compute()

        res = self.fun[self.cpt_compute](left, right)
        self.cpt_compute += 1

        if len(self.args)>2:
            self.args.pop(0)
            self.args[0] = res
            # need to store res for the last call of
            # the compute function
            res = self.compute()

        # Restore initial state
        self.args = self.backargs
        self.fun = self.backfun
        self.cpt_compute = 0

        return res

    def __add__(self, newvalue):
        self.add_operation(self.cls.__dadd__, newvalue)
        return self

    def __radd__(self, newvalue):
        self.add_operation(self.cls.__dradd__, newvalue)
        return self

    def __sub__(self, newvalue):
        self.add_operation(self.cls.__dsub__, newvalue)
        return self

    def __rsub__(self, newvalue):
        self.add_operation(self.cls.__drsub__, newvalue)
        return self

    def __mul__(self, newvalue):
        self.add_operation(self.cls.__dmul__, newvalue)
        return self

    def __rmul__(self, newvalue):
        self.add_operation(self.cls.__drmul__, newvalue)
        return self

    def __truediv__(self, newvalue):
        self.add_operation(self.cls.__dtruediv__, newvalue)
        return self

    def __rtruediv__(self, newvalue):
        self.add_operation(self.cls.__drtruediv__, newvalue)
        return self

    def __repra__(self):
        """Define a string representation for this delayed operation
        """

        left = self.args[0]
        right = self.args[1]
        op = self.fun[0]
        if op.__name__ == '__dadd__':
            op = '+'

        out = f'({left} {op} {right})'

        return out

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

        return f'({self.left} {op} {self.right})'
