import numpy
import math

from .. import block

# Blocks

class ControlledCombination(block.BufferBlock):
    r"""
    :py:class:`pyctrl.block.nl.ControlledCombination` implements the combination:

    :math:`y = \alpha \, u[1:m+1] + (1 - \alpha) \, u[m+1:], \quad \alpha = \frac{u[0]}{K}`

    where :math:`K` is a gain multiplier.
    
    :param float gain: multiplier (default `1`)
    :param int m: number of inputs to combine (default `1`)
    """
    def __init__(self, **kwargs):

        gain = kwargs.pop('gain', 1)
        if not isinstance(gain, (int, float)):
            raise block.BlockException('gain must be int or float')
        self.gain = gain
        
        m = kwargs.pop('m', 1)
        if not isinstance(m, int):
            raise block.BlockException('m must be int')
        self.m = m
        
        super().__init__(**kwargs)
    
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.nl.ControlledCombination`.

        :param float gain: multiplier (default `1`)
        :param int m: number of inputs to combine (default `1`)
        :param kwargs kwargs: other keyword arguments
        """

        if 'gain' in kwargs:
            gain = kwargs.pop('gain')
            if not isinstance(gain, (int, float)):
                raise block.BlockException('gain must be int or float')
            self.gain = gain
        
        if 'm' in kwargs:
            m = kwargs.pop('m', 1)
            if not isinstance(m, int):
                raise block.BlockException('m must be int')
            self.m = m

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes combination of inputs to the private :py:attr:`buffer`.

        :param vararg values: list of values
        """

        # call super
        super().write(*values)

        alpha = self.buffer[0] / self.gain;
        self.buffer = tuple((1-alpha) * v for v in self.buffer[1:self.m+1]) \
                      + tuple(alpha * v for v in self.buffer[self.m+1:])

class ControlledGain(block.BufferBlock):
    r"""
    :py:class:`pyctrl.block.nl.ControlledGain` implements the controlled gain:

    :math:`y = u[:m] u[m:]`

    :param int m: number of inputs to control (default `1`)
    """

    def __init__(self, **kwargs):

        m = kwargs.pop('m', 1)
        if not isinstance(m, int):
            raise block.BlockException('m must be int')
        self.m = m
        
        super().__init__(**kwargs)
    
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.nl.ControlledGain`.

        :param int m: number of inputs to combine (default `1`)
        :param kwargs kwargs: other keyword arguments
        """

        if 'm' in kwargs:
            m = kwargs.pop('m', 1)
            if not isinstance(m, int):
                raise block.BlockException('m must be int')
            self.m = m

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes product of gain times inputs to the private :py:attr:`buffer`.

        :param vararg values: list of values
        """

        # call super
        super().write(*values)
        
        self.buffer = tuple(g*v for (g,v) in zip(self.buffer[:self.m], self.buffer[self.m:]))

class DeadZone(block.BufferBlock):
    r"""
    :py:class:`pyctrl.block.nl.DeadZone` implements the piecewise function:

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

    The inverse can be obtained by swapping the arguments, that is :math:`f_{XY}^{-1} = f^{}_{YX}`.

    When :math:`X = 0` then :math:`c` is :py:data:`NaN`.

    :param float X: parameter :math:`X` (default `1`)
    :param float Y: parameter :math:`Y` (default `0`)
    """

    def __init__(self, **kwargs):

        Y = kwargs.pop('Y', 0)
        if not isinstance(Y, (int, float)):
            raise block.BlockException('Y must be int or float')
        self.Y = Y

        X = kwargs.pop('X', 1)
        if not isinstance(X, (int, float)):
            raise block.BlockException('X must be int or float')
        self.X = X

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
        """
        Set properties of :py:class:`pyctrl.block.nl.DeadZone`.

        :param float X: parameter :math:`X`
        :param float Y: parameter :math:`Y`
        :param kwargs kwargs: other keyword arguments
        """

        changes = False
        
        if 'Y' in kwargs:
            Y = kwargs.pop('Y')
            if not isinstance(Y, (int, float)):
                raise block.BlockException('Y must be int or float')
            self.Y = Y
            changes = True

        if 'X' in kwargs:
            X = kwargs.pop('X')
            if not isinstance(X, (int, float)):
                raise block.BlockException('X must be int or float')
            self.X = X
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
        """
        Writes the intput transformed by the dead-zone to the private :py:attr:`buffer`.

        :param vararg values: list of values
        """

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

