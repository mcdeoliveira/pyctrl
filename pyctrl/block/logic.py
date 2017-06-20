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

        self.buffer = tuple(int(v1 - v2 >= self.threshold) for (v1,v2) in zip(self.buffer[self.m:], self.buffer[:self.m]))

class CompareWithHysterisis(Compare):
    """
    :py:class:`pyctrl.block.logic.CompareWithHysterisis` compares inputs with histerisis. 

    Produces an output with the result of the test
    
    .. math::

       y[:m] = \begin{cases}
                  (u[m:] >= u[:m] + \gamma + \mu), & \text{if } \text{state}[:m] \\
                  (u[m:] >= u[:m] + \gamma - \mu), & \text{if } ! \text{state}[:m]
                \end{cases}

    and update the state as follows:

    .. math::

       \text{state}[:m] = \begin{cases}
                  1, & \text{if } \text{state} \& (u[m:] < u[:m] + \gamma + \mu) \\
                  0, & \text{if } \text{state} \& (u[m:] >= u[:m] + \gamma + \mu) \\
                  0, & \text{if } ! \text{state} \& (u[m:] >= u[:m] + \gamma - \mu) \\
                  1, & \text{if } ! \text{state} \& (u[m:] < u[:m] + \gamma - \mu)
                \end{cases}


    Output is :py:data:`1` if test return True and :py:data:`0` otherwise.

    :param float threshold: the threshold :math:`\gamma` (default `0`)
    :param float hysterisis: the hysterisis :math:`\mu` (default `0.1`)
    :param int m: number of inputs to test (default `1`)
    """
    
    def __init__(self, **kwargs):
        
        hysterisis = kwargs.pop('hysterisis', 0.1)
        if not isinstance(hysterisis, (int, float)):
            raise block.BlockException('hysterisis must be int or float')
        if hysterisis < 0:
            raise block.BlockException('hysterisis must be nonnegative')
        self.hysterisis = hysterisis
        
        super().__init__(**kwargs)

        # initialize state
        self.state = tuple(self.m*[1])
        
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.CompareWithHysterisis`.

        :param float threshold: threshold
        :param int m: number of inputs to combine
        :param float hysterisis: hysterisis
        :param kwargs kwargs: other keyword arguments
        """

        if 'hysterisis' in kwargs:
            hysterisis = kwargs.pop('hysterisis')
            if not isinstance(hysterisis, (int, float)):
                raise block.BlockException('hysterisis must be int or float')
            if hysterisis < 0:
                raise block.BlockException('hysterisis must be nonnegative')
            self.hysterisis = hysterisis
        
        super().set(**kwargs)
        
    def __test(self,v1,v2,s):
        if s:
            if v1 - v2 >= self.threshold + self.hysterisis:
                return (1, 0)
            else:
                return (0, 1)
        else:
            if v1 - v2 >= self.threshold - self.hysterisis:
                return (1, 0)
            else:
                return (0, 1)

    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super(Compare, self).write(*values)

        self.buffer, self.state = zip(*list(self.__test(v1,v2,s) for (v1,v2,s) in zip(self.buffer[self.m:], self.buffer[:self.m], self.state)))
        
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
            self.buffer = tuple(int(numpy.fabs(v) >= self.threshold) for v in self.buffer)
        else:
            self.buffer = tuple(int(numpy.fabs(v) <= self.threshold) for v in self.buffer)

class CompareAbsWithHysterisis(CompareAbs):
    """
    :py:class:`pyctrl.block.logic.CompareAbsWithHysterisis` compares the absolute value of its inputs with Hysterisis. 
    
    Produces an output with the result of the test
    
    :math:`y[:] = (|u[:]| <= \gamma)`

    .. math::

       y[:m] = \begin{cases}
                  (|u[:] <= \gamma - \mu), & \text{if } \text{state}[:] \\
                  (|u[:] <= \gamma + \mu), & \text{if } ! \text{state}[:]
                \end{cases}

    and update the state as follows:

    .. math::

       \text{state}[:m] = \begin{cases}
                  1, & \text{if } \text{state} \& (u[:] < \gamma + \mu) \\
                  0, & \text{if } \text{state} \& (u[:] >= \gamma + \mu) \\
                  0, & \text{if } ! \text{state} \& (u[:] >= \gamma - \mu) \\
                  1, & \text{if } ! \text{state} \& (u[:] < \gamma - \mu)
                \end{cases}

    Output is :py:data:`1` if test return True and :py:data:`0` otherwise.

    If :py:attr:`invert` is True performs the test:
    
    :math:`y[:] = (|u[:]| >= \gamma)`

    :param float threshold: the threshold :math:`\gamma` (default `0.5`)
    :param float hysterisis: the hysterisis :math:`\mu` (default `0.1`)
    :param bool invert: whether to invert the sign of the test
    """

    def __init__(self, **kwargs):

        hysterisis = kwargs.pop('hysterisis', 0.1)
        if not isinstance(hysterisis, (int, float)):
            raise block.BlockException('hysterisis must be int or float')
        if hysterisis < 0:
            raise block.BlockException('hysterisis must be nonnegative')
        self.hysterisis = hysterisis
        
        super().__init__(**kwargs)

        # initialize state
        self.state = None

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.CompareAbsWithHisterisis`.
 
        :param float threshold: the threshold :math:`\gamma` (default `0.5`)
        :param float hysterisis: the hysterisis :math:`\mu` (default `0.1`)
        :param bool invert: whether to invert the sign of the test
        :param kwargs kwargs: other keyword arguments
        """

        if 'hysterisis' in kwargs:
            hysterisis = kwargs.pop('hysterisis')
            if not isinstance(hysterisis, (int, float)):
                raise block.BlockException('hysterisis must be int or float')
            if hysterisis < 0:
                raise block.BlockException('hysterisis must be nonnegative')
            self.hysterisis = hysterisis
        
        super().set(**kwargs)

    def __test(self,v,s):
        if s:
            if v <= self.threshold - self.hysterisis:
                return (1, 0)
            else:
                return (0, 1)
        else:
            if v <= self.threshold + self.hysterisis:
                return (1, 0)
            else:
                return (0, 1)

    def __test_invert(self,v,s):
        if s:
            if v >= self.threshold + self.hysterisis:
                return (1, 0)
            else:
                return (0, 1)
        else:
            if v >= self.threshold - self.hysterisis:
                return (1, 0)
            else:
                return (0, 1)
            
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super(CompareAbs, self).write(*values)

        # initialize state?
        if self.state is None:
            self.state = tuple(len(self.buffer)*[1])

        # perform test
        if self.invert:
            self.buffer, self.state = zip(*list(self.__test_invert(v,s) for (v,s) in zip(self.buffer, self.state)))
        else:
            self.buffer, self.state = zip(*list(self.__test(v,s) for (v,s) in zip(self.buffer, self.state)))

class Trigger(block.BufferBlock):
    r"""
    :py:class:`pyctrl.block.logic.Trigger` can be used to switch signals on or off.
    
    Produces the output

    :math:`y[:-1] = \gamma \, u[1:]`

    where :math:`\gamma = 1` or :math:`\gamma = 0`.

    The value of :math:`\gamma` depends on the attribute
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
        Writes result of trigger to the private :py:attr:`buffer`.
        
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


class Set(block.BufferBlock):
    """
    :py:class:`pyctrl.block.logic.Set` set block when input changes. 

    :param str event: type of event: `rise`, `fall`, or `both` (default `rise`)
    :param block: an instance of :py:class:`pyctrl.block.Block`
    :param kwargs: keyword parameters to set
    """
    
    def __init__(self, **kwargs):
        
        self.event = kwargs.pop('event', 'rise')
        self.block = kwargs.pop('block', None)
        self.kwargs = kwargs.pop('kwargs', None)
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.Set`.

        :param str event: type of event: `rise`, `fall`, or `both` (default `rise`)
        :param block: an instance of :py:class:`pyctrl.block.Block`
        :param kwargs: keyword parameters to set
        """

        if 'event' in kwargs:
            event = kwargs.pop('event')
            if event not in set('rise','fall','both'):
                raise block.BlockException("event must be 'rise', 'fall', or 'both'")
            self.event = event
        
        if 'block' in kwargs:
            block = kwargs.pop('block')
            if block and block not isinstance(block, block.Block):
                raise block.BlockException("block must be and instance of pyctrl.block.Block")
            self.block = block

        if 'kwargs' in kwargs:
            _kwargs = kwargs.pop('kwargs')
            if _kwargs and _kwargs not isinstance(_kwargs, dict):
                raise block.BlockException("kwargs must be a dictionary")
            self.kwargs = _kwargs
            
        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super().write(*values)

        self.buffer = tuple(int(v1 - v2 >= self.threshold) for (v1,v2) in zip(self.buffer[self.m:], self.buffer[:self.m]))
