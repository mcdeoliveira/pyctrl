"""
This module provides blocks for linear dynamic systems.
"""

import numpy
import itertools

from .. import block
from .. import system
from ctrl.system.tf import DTTF
from ctrl.system.ss import DTSS

# Blocks

class System(block.BufferBlock):
    """
    *System* is a wrapper for a time-invariant dynamic system model. 

    :param model: an instance of `ctrl.system.System`
    """
    
    def __init__(self, **kwargs):

        model = kwargs.pop('model', DTTF())
        assert isinstance(model, system.System)
        self.model = model

        # set mux by default
        if 'mux' not in kwargs:
            kwargs['mux'] = True
        elif not kargs.get('mux'):
            raise BlockException('System must have `mux` equal to `True`.')
            
        super().__init__(**kwargs)

    def set(self, **kwargs):
        """
        Set properties of `System` block.

        :param model: an instance of `ctrl.system.System`
        """
        
        if 'model' in kwargs:
            model = kwargs.pop('model')
            assert isinstance(model, system.System)
            self.model = model

        super().set(**kwargs)

    def reset(self):
        """
        Reset `System` block.

        Calls `model.set_output(0)`.
        """
        self.model.set_output(numpy.zeros(self.model.shape()[1]))
        
    def write(self, *values):
        """
        Update `model` and write to the private `buffer`.
        """

        # call super
        super().write(*values)
        
        self.buffer = (self.model.update(self.buffer[0]), )
        
class TimeVaryingSystem(block.BufferBlock):
    """
    *TimeVarying* is a wrapper for a time-varying dynamic system model.

    The first signal must be a clock.

    :param model: an instance of `ctrl.system.TVSystem`
    """

    def __init__(self, **kwargs):

        model = kwargs.pop('model', DTTF())
        assert isinstance(model, system.TVSystem)
        self.model = model

        # set mux by default
        if 'mux' not in kwargs:
            kwargs['mux'] = True
        elif not kargs.get('mux'):
            raise BlockException('System must have `mux` equal to `True`.')
        
        super().__init__(**kwargs)
        
    def set(self, **kwargs):
        """
        Set properties of `TimeVarying` block.

        :param model: an instance of `ctrl.system.TVSystem`
        """

        if 'model' in kwargs:
            model = kwargs.pop('model')
            assert isinstance(model, system.TVSystem)
            self.model = model

        super().set(**kwargs)

    def reset(self):
        """
        Reset `TimeVarying` block.

        Calls `model.set_output(0, 0)`.
        """
        self.model.set_output(0, numpy.zeros(self.model.shape()[1]))
        
    def write(self, *values):
        """
        Update `model` and write to the private `buffer`.

        The first signal must be a clock.
        """

        # call super
        super().write(*values)

        # update model
        # time comes first
        uk = self.buffer[0]
        self.buffer = (self.model.update(uk[0], uk[1:]), )

class Gain(block.BufferBlock):
    """
    *Gain* multiplies input by a constant gain, that is

    :math:`y = a u`,

    where :math:`a` is the gain.

    :param gain: multiplier (default `1`)
    """
    def __init__(self, **kwargs):

        gain = kwargs.pop('gain', 1)
        assert isinstance(gain, (int, float))
        self.gain = gain

        super().__init__(**kwargs)
    
    def set(self, **kwargs):
        """
        Set properties of `Gain` block.

        :param gain: multiplier
        """
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        super().set(**kwargs)

    def write(self, *values):
        """
        Writes product of `gain` times current input to the private `buffer`.
        """

        # call super
        super().write(*values)

        self.buffer = tuple(v * self.gain for v in self.buffer)

class Affine(block.BufferBlock):
    """
    *Affine* multiplies and offset input by a constant gain and offset, that is

    :math:`y = a u + b`,

    where :math:`a` is the gain and :math:`b` is the offset.

    :param gain: multiplier (default `1`)
    :param offset: offset (default `0`)
    """

    def __init__(self, **kwargs):

        gain = kwargs.pop('gain', 1)
        assert isinstance(gain, (int, float))
        self.gain = gain

        offset = kwargs.pop('offset', 0)
        assert isinstance(offset, (int, float))
        self.offset = offset

        super().__init__(**kwargs)
    
    def set(self, **kwargs):
        """
        Set properties of `Affine` block.

        :param gain: multiplier (default `1`)
        :param offset: offset (default `0`)
        """
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        if 'offset' in kwargs:
            self.gain = kwargs.pop('offset')

        super().set(**kwargs)

    def write(self, *values):
        """
        Writes product of `gain` times current input plus `offset` to
        the private `buffer`.
        """

        # call super
        super().write(*values)

        self.buffer = tuple(v*self.gain + self.offset for v in self.buffer)

class Differentiator(block.BufferBlock):
    r"""
    *Differentiator* differentiates the input, that is

    :math:`y = {\displaystyle \frac{u_k - u_{k-1}}{t_k - t_{k-1}}} \approx \dot{u}`.

    The first signal must be a clock.
    """

    def __init__(self, **kwargs):
        
        self.time = -1
        self.last = ()

        super().__init__(**kwargs)

    def get(self, keys = None):

        # call super excluding time and last
        return super().get(keys, exclude = ('time', 'last'))
    
    def write(self, *values):
        """
        Writes finite difference derivative to the private `buffer`.

        The first signal must be a clock.
        """

        # call super
        super().write(*values)
        
        #print('values = {}'.format(values))

        assert len(self.buffer) > 1
        t = self.buffer[0]
        x = self.buffer[1:]

        #print('t = {}'.format(t))
        #print('x = {}'.format(x))

        if self.time > 0:
            dt = t - self.time
        else:
            dt = 0
        #print('dt = {}'.format(dt))
        
        if dt > 0:
            self.time, self.last, self.buffer = t, x, \
                [(n-o)/dt for n,o in zip(x, self.last)]
        else:
            self.time, self.last, self.buffer = t, x, \
                [0*v for v in x]

class Feedback(block.BufferBlock):
    r"""
    *Feedback* creates a feedback connection for a given `block`, that is

    :math:`y = G e, \quad e = \gamma u[m:] - u[:m]`,

    where :math:`G` represents the `block`, `gamma` is a constant gain, and `m` is the number of inputs and references.

    The first `m` signals are inputs and the last `m` signals are references.

    :param block: an instance of `ctrl.block.Block`
    :param gamma: a constant gain (default `1`)
    :param m: number of inputs (default `1`)
    """

    def __init__(self, **kwargs):

        self.block = kwargs.pop('block', block.ShortCircuit())
        self.gamma = kwargs.pop('gamma', 1)
        self.m = kwargs.pop('m', 1)

        super().__init__(**kwargs)
    
    def reset(self):
        """
        Reset `Feedback` block.

        Calls `block.reset()`.
        """
        self.block.reset()

    def set(self, **kwargs):
        """
        Set properties of `Feedback` block.

        :param block: an instance of `ctrl.block.Block`
        :param gamma: a constant gain
        :param m: number of inputs
        """
        
        if 'block' in kwargs:
            self.block = kwargs.pop('block')
            
        if 'gamma' in kwargs:
            self.gamma = kwargs.pop('gamma')
            
        if 'm' in kwargs:
            self.gamma = kwargs.pop('m')

        super().set(**kwargs)

    def write(self, *values):
        """
        Writes feedback signal to the private `buffer`.
        """

        # call super
        super().write(*values)
        
        # calculate error
        error = tuple(self.gamma*y-r for (y,r) in zip(self.buffer[self.m:], self.buffer[:self.m]))

        # call block
        self.block.write(*error)
        
        # then read
        self.buffer = self.block.read()

class Average(block.BufferBlock):
    """
    *Average* calculates the (weighted) average of all inputs, that is

    :math:`y = \sum_{i = 0}^{m-1} w[i] u[i]`,

    where :math:`w` is a vector of weights

    :param weights: weights (default `1/m`)
    """

    def __init__(self, **kwargs):

        self.weights = kwargs.pop('weights', None)
        
        super().__init__(**kwargs)

    def set(self, **kwargs):
        """
        Set properties of `Sum` block.

        :param weights: multiplier
        """
        
        if 'weights' in kwargs:
            weights = kwargs.pop('weights')
            if weights is not None:
                self.weights = numpy.array(weights)
            else:
                self.weights = None
                
        super().set(**kwargs)

    def write(self, *values):
        """
        Writes average of the current input to the private `buffer`.

        :param values: list of values
        :return: tuple with scaled input
        """

        # call super
        super().write(*values)
        
        if not self.buffer:
            self.buffer = (0, )
        elif self.weights is not None:
            self.buffer = (numpy.average(self.buffer, axis=0, weights=self.weights), )
        else:
            self.buffer = (numpy.average(self.buffer, axis=0), )


class Sum(block.BufferBlock):
    """
    *Sum* adds all inputs and multiplies the result by a constant gain, that is

    :math:`y = a \sum_{i = 0}^{m-1} u[m]`,

    where :math:`a` is the gain.

    :param gain: multiplier (default `1`)
    """

    def __init__(self, **kwargs):

        self.gain = kwargs.pop('gain', 1)
        
        super().__init__(**kwargs)

    def set(self, **kwargs):
        """
        Set properties of `Sum` block.

        :param gain: multiplier
        """
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        super().set(**kwargs)

    def write(self, *values):
        """
        Writes product of `gain` times the sum of the current input to the private `buffer`.

        :param values: list of values
        :return: tuple with scaled input
        """
        # call super
        super().write(*values)
        
        self.buffer = (self.gain * numpy.sum(self.buffer, axis=0), )
        

class Subtract(block.BufferBlock):
    r"""
    *Subtract* subtracts first input as in

    :math:`y = a \sum_{i = 1}^{m-1} u[m] - u[0]`,

    where :math:`a` is the gain.

    :param gain: multiplier (default `1`)
    """

    def __init__(self, **kwargs):

        self.gain = kwargs.pop('gain', 1)
        
        super().__init__(**kwargs)

    def set(self, **kwargs):
        """
        Set properties of `Sum` block.

        :param gain: multiplier
        """
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        super().set(**kwargs)

    def write(self, *values):
        """
        Writes product of `gain` times the difference of the current input to the private `buffer`.

        :param values: list of values
        :return: tuple with scaled input
        """

        # call super
        super().write(*values)
        
        if self.buffer:
            # flip first entry
            self.buffer = (-self.buffer[0],) + self.buffer[1:]

        # calculate sum
        self.buffer = (self.gain * numpy.sum(self.buffer, axis=0), )
