"""
This module provide logic blocks.
"""

import numpy
import math

from .. import block

# Blocks

class Compare(block.BufferBlock):
    """
    :py:class:`pyctrl.block.logic.Compare` compares inputs. 

    Produces an output with the result of the test
    
    :math:`y[:m] = (u[m:] >= u[:m] + \gamma)`

    Output is :py:data:`1` if test return True and :py:data:`0` otherwise.

    :param float threshold: the threshold :math:`\gamma` (default `0`)
    :param int m: number of inputs to test (default `1`)
    """
    
    def __init__(self, **kwargs):
        
        threshold = kwargs.pop('threshold', 0)
        if not isinstance(threshold, (int, float)):
            raise block.BlockException('threshold must be int or float')
        self.threshold = threshold
        
        m = kwargs.pop('m', 1)
        if not isinstance(m, int):
            raise block.BlockException('m must be int')
        self.m = m
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.Compare`.

        :param float threshold: threshold
        :param int m: number of inputs to combine
        :param kwargs kwargs: other keyword arguments
        """

        if 'threshold' in kwargs:
            threshold = kwargs.pop('threshold')
            if not isinstance(threshold, (int, float)):
                raise block.BlockException('threshold must be int or float')
            self.threshold = threshold
        
        if 'm' in kwargs:
            m = kwargs.pop('m', 1)
            if not isinstance(m, int):
                raise block.BlockException('m must be int')
            self.m = m

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super().write(*values)

        self.buffer = tuple(int(v1 - v2 >= self.threshold) for (v1,v2) in zip(values[self.m:], values[:self.m]))

class CompareAbs(block.BufferBlock):
    """
    :py:class:`pyctrl.block.logic.CompareAbs` compares the absolute value of its inputs. 
    
    Produces an output with the result of the test
    
    :math:`y[:] = (|u[:]| <= \gamma)`

    Output is :py:data:`1` if test return True and :py:data:`0` otherwise.

    If :py:attr:`invert` is True performs the test:
    
    :math:`y[:] = (|u[:]| >= \gamma)`

    :param float threshold: the threshold :math:`\gamma` (default `0.5`)
    :param bool invert: whether to invert the sign of the test
    """

    def __init__(self, **kwargs):

        threshold = kwargs.pop('threshold', 0.5)
        if not isinstance(threshold, (int, float)):
            raise block.BlockException('threshold must be int or float')
        self.threshold = threshold
        
        self.invert = kwargs.pop('invert', False)

        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.CompareAbs`.
 
        :param float threshold: the threshold :math:`\gamma` (default `0.5`)
        :param bool invert: whether to invert the sign of the test
        :param kwargs kwargs: other keyword arguments
        """

        if 'threshold' in kwargs:
            threshold = kwargs.pop('threshold')
            if not isinstance(threshold, (int, float)):
                raise block.BlockException('threshold must be int or float')
            self.threshold = threshold
        
        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super().write(*values)

        if self.invert:
            self.buffer = tuple(int(numpy.fabs(v) >= self.threshold) for v in values)
        else:
            self.buffer = tuple(int(numpy.fabs(v) <= self.threshold) for v in values)

class Trigger(block.BufferBlock):
    r"""
    :py:class:`pyctrl.block.logic.Trigger` can be used to switch signals on or off.
    
    Produces the output

    :math:`y[1:] = \gamma \, u[1:]`

    where :math:`\gamma = 1` or :math:`\gamma = 0`.

    The value of :math:`\gamma` depends on the attribure
    :py:attr:`state` as follows

    .. math::

       \gamma = \begin{cases}
                  1, & \text{if } \text{state} \, \& \, f(u[0]) \\
                  0, & \text{if } ! \text{state}
                \end{cases}

    Once :math:`f(u[0])` becomes True :py:attr:`state` is set to True
    and must be reset manually.
    
    :param function: test function (default identity)
    :param bool state: initial state (default False)
    """
    
    def __init__(self, **kwargs):

        self.function = kwargs.pop('function', (lambda x: x))
        self.state = kwargs.pop('state', False)

        super().__init__(**kwargs)

    def reset(self):
        """
        Reset :py:class:`pyctrl.block.logic.Trigger` attribute :py:attr:`state` to False.
        """

        self.state = False
    
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super().write(*values)
        
        if self.state:
            self.buffer = values[1:]
        elif self.function(values[0]):
            self.state = True
            self.buffer = values[1:]
        else:
            self.buffer = tuple((len(values)-1)*[0])
