import numpy
import math

from .. import block

# Blocks

class ControlledCombination(block.BufferBlock):
    r"""
    *ControlledCombination* implements the combination:

    .. math::

        y = \alpha u[1:m+1] + (1 - \alpha) u[m+1:], \quad \alpha = \frac{u[0]}{K}

    where :math:`K` is a gain multiplier.
    
    :param gain: multiplier (default `1`)
    :param m: number of inputs to combine (default `1`)
    """
    
    def __init__(self, **kwargs):

        self.gain = kwargs.pop('gain', 1)
        self.m = kwargs.pop('m', 1)

        super().__init__(**kwargs)
    
    def write(self, *values):
        """
        Writes combination of inputs to the private `buffer`.
        """

        # call super
        super().write(*values)

        assert len(self.buffer) == 1 + 2 * self.m
        alpha = self.buffer[0] / self.gain;
        self.buffer = tuple((1-alpha) * v for v in self.buffer[1:self.m+1]) \
                      + tuple(alpha * v for v in self.buffer[self.m+1:])

class ControlledGain(block.BufferBlock):
    r"""
    *ControlledGain* implements the controlled gain:

    .. math::

        y = u[0] u[1:]
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
    
    def write(self, *values):

        """
        Writes product of gain times inputs to the private `buffer`.
        """

        # call super
        super().write(*values)
        
        assert len(self.buffer) > 1
        self.buffer = tuple(self.buffer[0] * v for v in self.buffer[1:])

class DeadZone(block.BufferBlock):
    r"""
    *DeadZone* implements the piecewise function:

    .. math::

        y = f_{XY}(u) = \begin{cases} 
            a u + b, & u > X, \\ 
            a u - b, & u < -X, \\
            c u, & -X \leq u \leq X
        \end{cases}

    where
        
    .. math::

        a &= \frac{100-Y}{100-X} \\
        b &= 100 \frac{Y-X}{100-X} \\
        c &= \frac{Y}{X}
        
    This is a generalized dead-zone nonlinearity.

    The classic dead-zone nonlinearity has :math:`Y = 0`.

    The inverse can be obtained by swapping the arguments, that is

    .. math::
        
        f_{XY}^{-1} = f_{YX}^{}

    When :math:`X = 0` then :math:`c` is `NaN`.
    """

    def __init__(self, **kwargs):

        self.Y = kwargs.pop('Y', 0)
        self.X = kwargs.pop('X', 1)

        super().__init__(**kwargs)

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

    def get(self, *keys, exclude = ()):

        # call super
        return super().get(*keys, exclude = exclude + ('_pars',))

    def set(self, exclude = (), **kwargs):

        changes = False
        
        if 'Y' in kwargs:
            self.Y = kwargs.pop('Y')
            changes = True

        if 'X' in kwargs:
            self.X = kwargs.pop('X')
            changes = True

        if changes:
            self._calculate_pars()
            
        super().set(exclude + ('_pars',), **kwargs)

    def _deadzone(self, a, b, c, x):
        if x > self.X:
            return a*x+b
        elif x < -self.X:
            return a*x-b
        else: # -d <= x <= d
            return c*x
        
    def write(self, *values):

        # call super
        super().write(*values)
        
        # Dead-zone compensation
        (a, b, c) = self._pars
        # x = self.buffer[0]
        # if x > self.X:
        #     self.buffer = (a*x+b, )
        # elif x < -self.X:
        #     self.buffer = (a*x-b, )
        # else: # -d <= x <= d
        #     self.buffer = (c*x, )

        self.buffer = tuple(self._deadzone(a,b,c,x) for x in self.buffer)

