import numpy
import math

from .. import block

# Blocks

class Abs(block.BufferBlock):

    def write(self, *values):

        self.buffer = tuple(map(math.fabs, values))
        

class DeadZone(block.BufferBlock):

    def __init__(self, X = 1, Y = 0, *vars, **kwargs):
        """Wrapper for the piecewise function:

          f(x) = { a x + b , x > X,
                 { a x - b , x < -X,
                 { c x     , -X <= x <= X

        where
        
          a = (100-Y)/(100-X) 
          b = 100(Y-X)/(100-X)
          c = Y/X
        
        This is a generalized dead-zone nonlinearity.
        The classic dead-zone nonlinearity has Y = 0.

        The inverse can be obtained by swapping the arguments:

             f = DeadZone(X, Y)   =>   inv(f) = DeadZone(Y, X)

        When X = 0 the coefficient c == NaN.
        """

        self.Y = Y
        self.X = X

        super().__init__(*vars, **kwargs)

        self._calculate_pars()

    def _calculate_pars(self):
      
        a = (100 - self.Y) / (100 - self.X)
        b = 100 * (self.Y - self.X) / (100 - self.X)
        if self.X != 0:
            c = self.Y / self.X
        elif self.X == self.Y:
            c = 1
        else:
            c = numpy.nan
        self._pars = (a,b,c)

    def get(self, keys = None):

        # call super
        return super().get(keys, exclude = ('_pars',))

    def set(self, key, value):
        
        if key == 'Y':
            self.Y = value
            self._calculate_pars()
        elif key == 'X':
            self.X = value
            self._calculate_pars()
        else:
            super().set(key, value)

    def write(self, *values):

        # Dead-zone compensation
        x = values[0]
        (a, b, c) = self._pars
        if x > self.X:
            self.buffer = (a*x+b, )
        elif x < -self.X:
            self.buffer = (a*x-b, )
        else: # -d <= x <= d
            self.buffer = (c*x, )

        return self.buffer

