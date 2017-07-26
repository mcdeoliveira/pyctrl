"""
This module provide logic blocks.
"""

import numpy
import math
from enum import IntEnum

from .. import block
from pyctrl import BlockType

# State

class State(IntEnum):
    HIGH = 1
    LOW = 0

# Blocks

class Compare(block.Filter, block.BufferBlock):
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
    r"""
    :py:class:`pyctrl.block.logic.CompareWithHysterisis` compares inputs with histerisis. 

    Produces an output with the result of the test
    
    .. math::
       :nowrap:

       \begin{align*}
       y[:m] = \left\{ \begin{array}{ll}
                  (u[m:] >= u[:m] + \gamma + \mu), & \text{if } \text{state}[:m] \\
                  (u[m:] >= u[:m] + \gamma - \mu), & \text{if } ! \text{state}[:m]
                \end{array} \right .
       \end{align*}

    and update the state as follows:

    .. math::

       \text{state}[:m] = \begin{cases}
                  1, & \text{if } \text{state} \, \& \, (u[m:] < u[:m] + \gamma + \mu) \\
                  0, & \text{if } \text{state} \, \& \, (u[m:] >= u[:m] + \gamma + \mu) \\
                  0, & \text{if } ! \text{state} \, \& \, (u[m:] >= u[:m] + \gamma - \mu) \\
                  1, & \text{if } ! \text{state} \, \& \, (u[m:] < u[:m] + \gamma - \mu)
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
        self.state = tuple(self.m*[State.HIGH])
        
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
                return (1, State.LOW)
            else:
                return (0, State.HIGH)
        else:
            if v1 - v2 >= self.threshold - self.hysterisis:
                return (1, State.LOW)
            else:
                return (0, State.HIGH)

    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super(Compare, self).write(*values)

        self.buffer, self.state = zip(*list(self.__test(v1,v2,s) for (v1,v2,s) in zip(self.buffer[self.m:], self.buffer[:self.m], self.state)))
        
class CompareAbs(block.Filter, block.BufferBlock):
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
    r"""
    :py:class:`pyctrl.block.logic.CompareAbsWithHysterisis` compares the absolute value of its inputs with Hysterisis. 
    
    Produces an output with the result of the test:
    
    .. math::

       y[:m] = \begin{cases}
                  (|u[:] - \alpha| <= \gamma - \mu), & \text{if } \text{state}[:] \\
                  (|u[:] - \alpha| <= \gamma + \mu), & \text{if } ! \text{state}[:]
                \end{cases}

    and update the state as follows:

    .. math::

       \text{state}[:m] = \begin{cases}
                  1, & \text{if } \text{state} \, \& \, (u[:] < \gamma + \mu) \\
                  0, & \text{if } \text{state} \, \& \, (u[:] >= \gamma + \mu) \\
                  0, & \text{if } ! \text{state} \, \& \, (u[:] >= \gamma - \mu) \\
                  1, & \text{if } ! \text{state} \, \& \, (u[:] < \gamma - \mu)
                \end{cases}

    Output is :py:data:`1` if test return True and :py:data:`0` otherwise.

    If :py:attr:`invert` is True performs the test:
    
    :math:`y[:] = (|u[:]| >= \gamma)`

    :param float threshold: the threshold :math:`\gamma` (default `0.5`)
    :param float offset: the offset :math:`\alpha` (default `0.0`)
    :param float hysterisis: the hysterisis :math:`\mu` (default `0.1`)
    :param bool invert: whether to invert the sign of the test
    """

    def __init__(self, **kwargs):

        offset = kwargs.pop('offset', 0)
        if not isinstance(offset, (int, float)):
            raise block.BlockException('offset must be int or float')
        self.offset = offset
        
        hysterisis = kwargs.pop('hysterisis', 0.1)
        if not isinstance(hysterisis, (int, float)):
            raise block.BlockException('hysterisis must be int or float')
        if hysterisis < 0:
            raise block.BlockException('hysterisis must be nonnegative')
        self.hysterisis = hysterisis

        # initialize state
        self.state = kwargs.pop('state', None)
        
        super().__init__(**kwargs)

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
        
        if 'offset' in kwargs:
            offset = kwargs.pop('offset', 0)
            if not isinstance(offset, (int, float)):
                raise block.BlockException('offset must be int or float')
            self.offset = offset
        
        super().set(**kwargs)

    def __test(self,v,s):
        if s:
            if numpy.fabs(v - self.offset) <= self.threshold + self.hysterisis:
                return (1, State.HIGH)
            else:
                return (0, State.LOW)
        else:
            if numpy.fabs(v - self.offset) <= self.threshold - self.hysterisis:
                return (1, State.HIGH)
            else:
                return (0, State.LOW)

    def __test_invert(self,v,s):
        if s:
            if numpy.fabs(v - self.offset) >= self.threshold - self.hysterisis:
                return (1, State.HIGH)
            else:
                return (0, State.LOW)
        else:
            if numpy.fabs(v - self.offset) >= self.threshold + self.hysterisis:
                return (1, State.HIGH)
            else:
                return (0, State.LOW)
            
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super(CompareAbs, self).write(*values)

        # initialize state?
        if self.state is None:
            self.state = tuple(len(self.buffer)*[State.HIGH])

        # perform test
        if self.invert:
            self.buffer, self.state = zip(*list(self.__test_invert(v,s) for (v,s) in zip(self.buffer, self.state)))
        else:
            self.buffer, self.state = zip(*list(self.__test(v,s) for (v,s) in zip(self.buffer, self.state)))

class Trigger(block.Filter, block.BufferBlock):
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
    :param bool state: initial state (default State.LOW)
    """
    
    def __init__(self, **kwargs):

        self.function = kwargs.pop('function', (lambda x: x))
        self.state = kwargs.pop('state', State.LOW)

        super().__init__(**kwargs)

    def reset(self):
        """
        Reset :py:class:`pyctrl.block.logic.Trigger` attribute :py:attr:`state` to False.
        """

        self.state = State.LOW
    
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
            self.state = State.HIGH
            self.buffer = values[1:]
        else:
            self.buffer = tuple((len(values)-1)*[0])

class Event(block.Sink, block.BufferBlock):
    """
    :py:class:`pyctrl.block.logic.Event` runs actions based on event. 

    Produces no output but calls
    :py:meth:`pyctrl.block.logic.Event.rise_event` if

    :py:attr:`state` is :py:attr:`pyctrl.block.logic.State.LOW` and :math:`u[m:] >= high`

    or :py:meth:`pyctrl.block.logic.Event.fall_event` if

    :py:attr:`state` is :py:attr:`pyctrl.block.logic.State.HIGH` and :math:`u[m:] <= low`

    :param float low: the low threshold
    :param float high: the high threshold
    """

    def __init__(self, **kwargs):
        
        low = kwargs.pop('low', 0.2)
        if not isinstance(low, (int, float)):
            raise block.BlockException('low must be int or float')
        self.low = low
        
        high = kwargs.pop('high', 0.8)
        if not isinstance(high, (int, float)):
            raise block.BlockException('high must be int or float')
        self.high = high

        self.state = kwargs.pop('state', State.LOW)
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.Event`.

        :param float low: low threshold
        :param float high: high threshold
        :param state: state (HIGH or LOW)
        :param kwargs kwargs: other keyword arguments
        """

        if 'low' in kwargs:
            low = kwargs.pop('low')
            if not isinstance(low, (int, float)):
                raise block.BlockException('low must be int or float')
            self.low = low
        
        if 'high' in kwargs:
            high = kwargs.pop('high')
            if not isinstance(high, (int, float)):
                raise block.BlockException('high must be int or float')
            self.high = high

        if 'state' in kwargs:
            self.state = kwargs.pop('state')
            
        super().set(**kwargs)

    def rise_event(self):
        raise block.BlockException('Method rise_event has not been implemented')
        
    def fall_event(self):
        raise block.BlockException('Method fall_event has not been implemented')
    
    def write(self, *values):
        """
        Writes result of comparison to the private :py:attr:`buffer`.
        
        :param vararg values: values
        """

        # call super
        super().write(*values)

        if self.state is State.LOW and self.buffer[0] > self.high:
            # gone high
            self.state = State.HIGH
            self.rise_event()

        elif self.state is State.HIGH and self.buffer[0] < self.low:
            # gone low
            self.state = State.LOW
            self.fall_event()
        
class SetBlock(Event):
    """
    :py:class:`pyctrl.block.logic.SetBlock` set block based on event. 
    """

    def __init__(self, **kwargs):
        
        self.label = kwargs.pop('label')
        if not isinstance(self.label, (tuple, list)):
            self.label = (self.label,)

        if 'on_rise_and_fall' in kwargs:
            self.on_rise = kwargs.pop('on_rise_and_fall', {})
            self.on_fall = self.on_rise
        else:
            self.on_rise = kwargs.pop('on_rise', {})
            self.on_fall = kwargs.pop('on_fall', {})
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.logic.Event`.

        :param pyctrl.BlockType blocktype: block type (source, sink, filter, timer)
        :param kwargs kwargs: other keyword arguments
        """

        if 'label' in kwargs:
            self.label = kwargs.pop('label')
            if not isinstance(self.label, (tuple, list)):
                self.label = (self.label,)
        
        if 'on_rise_and_fall' in kwargs:
            self.on_rise = kwargs.pop('on_rise_and_fall', {})
            self.on_fall = self.on_rise
        else:
            if 'on_rise' in kwargs:
                self.on_rise = kwargs.pop('on_rise', {})
            if 'on_fall' in kwargs:
                self.on_fall = kwargs.pop('on_fall', {})
            
        super().set(**kwargs)

    def call(self, label, **kwargs):
        raise block.BlockException('Method call has not been implemented')
        
    def rise_event(self):

        if self.on_rise:
        
            # call set
            for l in self.label:
                self.call(l, **self.on_rise)
        
    def fall_event(self):

        if self.on_fall:

            # call set
            for l in self.label:
                self.call(l, **self.on_fall)

class SetFilter(SetBlock):

    def call(self, label, **kwargs):

        self.parent.set_filter(label, **kwargs)
    
class SetSource(SetBlock):

    def call(self, label, **kwargs):

        self.parent.set_source(label, **kwargs)

class SetSink(SetBlock):

    def call(self, label, **kwargs):

        self.parent.set_sink(label, **kwargs)

class SetTimer(SetBlock):

    def call(self, label, **kwargs):

        self.parent.set_timer(label, **kwargs)
        
