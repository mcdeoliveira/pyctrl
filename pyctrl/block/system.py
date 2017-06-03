"""
This module provides blocks for dynamic systems.
"""

import numpy
import itertools

from .. import block
from .. import system
from pyctrl.system.tf import DTTF
from pyctrl.system.ss import DTSS

# Blocks

class System(block.BufferBlock):
    """
    :py:class:`pyctrl.block.system.System` is a wrapper for a time-invariant dynamic system model.  

    Inputs of this block are always multiplexed.

    :param model: an instance of :py:class:`pyctrl.system.System`
    """
    
    def __init__(self, **kwargs):

        model = kwargs.pop('model', DTTF())
        if not isinstance(model, system.System):
            raise block.BlockException('model must be an instance of pyctrl.system.System.')
        self.model = model

        # set mux by default
        if 'mux' not in kwargs:
            kwargs['mux'] = True
        elif not kwargs.get('mux'):
            raise block.BlockException('System must have `mux` equal to `True`.')
            
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.system.System` block.

        :param model: an instance of :py:class:`pyctrl.system.System`
        """
        
        if 'model' in kwargs:
            model = kwargs.pop('model')
            if not isinstance(model, system.System):
                raise block.BlockException('model must be an instance of pyctrl.system.System.')
                
            self.model = model

        super().set(exclude, **kwargs)

    def reset(self):
        """
        Reset :py:class:`pyctrl.block.system.System` block.

        Calls :py:meth:`pyctrl.system.System.set_output` for :py:attr:`model` with 0.
        """
        self.model.set_output(numpy.zeros(self.model.shape()[1]))
        
    def write(self, *values):
        """
        Update :py:attr:`model` and write to the private :py:attr:`buffer`.

        :param vararg values: values
        """

        # call super
        super().write(*values)
        
        self.buffer = (self.model.update(self.buffer[0]), )
        
class TimeVaryingSystem(block.BufferBlock):
    """
    :py:class:`pyctrl.block.system.TimeVarying` is a wrapper for a time-varying dynamic system model.

    The first signal must be a clock.

    :param model: an instance of :py:class:`pyctrl.system.TVSystem`
    """

    def __init__(self, **kwargs):

        model = kwargs.pop('model', DTTF())
        if not isinstance(model, system.TVSystem):
            raise block.BlockException('model must be an instance of pyctrl.system.TVSystem.')
        self.model = model

        # set mux by default
        if 'mux' not in kwargs:
            kwargs['mux'] = True
        elif not kwargs.get('mux'):
            raise block.BlockException('System must have `mux` equal to `True`.')
        
        super().__init__(**kwargs)
        
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.system.TimeVarying` block.

        :param model: an instance of :py:class:`pyctrl.system.TVSystem`
        """

        if 'model' in kwargs:
            model = kwargs.pop('model')
            if not isinstance(model, system.TVSystem):
                raise block.BlockException('model must be an instance of pyctrl.system.TVSystem.')
            self.model = model

        super().set(exclude, **kwargs)

    def reset(self):
        """
        Reset :py:class:`pyctrl.block.system.TimeVarying` block.

        Calls :py:meth:`pyctrl.system.System.set_output` for :py:attr:`model` with :py:data:`(0,0)`.
        """
        self.model.set_output(0, numpy.zeros(self.model.shape()[1]))
        
    def write(self, *values):
        """
        Update :py:attr:`model` and write to the private :py:attr:`buffer`.

        The first signal must be a clock.

        :param vararg values: values
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
        if isinstance(gain, (list, tuple)):
            gain = numpy.array(gain)
        if not isinstance(gain, (int, float, numpy.ndarray)):
            raise block.BlockException('gain must be int, float or numpy array')
        if isinstance(gain, numpy.ndarray) and gain.ndim > 1:
            raise block.BlockException('gain must be 1D numpy array; use pyctrl.block.Dot for matrix gains')
        self.gain = gain

        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.system.Gain` block.

        :param gain: multiplier (default `1`)
        :param kwargs kwargs: other keyword arguments
        """

        if 'gain' in kwargs:
            gain = kwargs.pop('gain', 1)
            if isinstance(gain, (list, tuple)):
                gain = numpy.array(gain)
            if not isinstance(gain, (int, float, numpy.ndarray)):
                raise block.BlockException('gain must be int, float or numpy array')
            if isinstance(gain, numpy.ndarray) and gain.ndim > 1:
                raise block.BlockException('gain must be 1D numpy array; use pyctrl.block.Dot for matrix gains')
            self.gain = gain

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes product of :py:attr:`gain` times current input to the 
        private :py:attr:`buffer`.

        :param vararg values: values
        """

        # call super
        super().write(*values)

        self.buffer = tuple(v * self.gain for v in self.buffer)

class Affine(Gain):
    """
    *Affine* multiplies and offset input by a constant gain and offset, that is

    :math:`y = a u + b`,

    where :math:`a` is the gain and :math:`b` is the offset.

    :param float gain: multiplier (default `1`)
    :param float offset: offset (default `0`)
    """

    def __init__(self, **kwargs):

        offset = kwargs.pop('offset', 0)
        if isinstance(offset, (list, tuple)):
            offset = numpy.array(offset)
        if not isinstance(offset, (int, float, numpy.ndarray)):
            raise block.BlockException('offset must be int, float or numpy array')
        if isinstance(offset, numpy.ndarray) and offset.ndim > 1:
            raise block.BlockException('offset must be 1D numpy array')
        self.offset = offset

        super().__init__(**kwargs)
    
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.system.Affine` block.

        :param float gain: multiplier (default `1`)
        :param float offset: offset (default `0`)
        :param kwargs kwargs: other keyword arguments
        """

        if 'offset' in kwargs:
            offset = kwargs.pop('offset', 0)
            if isinstance(offset, (list, tuple)):
                offset = numpy.array(offset)
            if not isinstance(offset, (int, float, numpy.ndarray)):
                raise block.BlockException('offset must be int, float or numpy array')
            if isinstance(offset, numpy.ndarray) and offset.ndim > 1:
                raise block.BlockException('offset must be 1D numpy array')
            self.offset = offset

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes product of :py:attr:`gain` times current input plus :py:attr:`offset` to
        the private :py:attr:`buffer`.

        :param vararg values: values
        """

        # call super
        block.BufferBlock.write(self, *values)

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

    def get(self, *keys, exclude = ()):

        # call super excluding time and last
        return super().get(*keys, exclude = exclude + ('time', 'last'))

    def set(self, exclude = (), **kwargs):

        # call super excluding time and last
        return super().set(exclude + ('time', 'last'), **kwargs)
    
    def write(self, *values):
        """
        Writes finite difference derivative to the private :py:attr:`buffer`.

        The first signal must be a clock.

        :param vararg values: values
        """

        # call super
        super().write(*values)
        
        #print('values = {}'.format(values))

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
    :py:class:`pyctrl.system.Feedback` creates a general feedback connection for a given :py:attr:`block`, that is

    .. math::

        y = G e, \quad e = \gamma u[m:] + \rho u[:m],

    where :math:`G` represents the :py:attr:`block`, :math:`\gamma` and :math:`\rho` are a constant gains, and :math:`m` is the number of inputs and references.

    For the default configuration the first :math:`m` signals are measurements and the last :math:`m` signals are references under standard unit negative feedback.

    :param block: an instance of :py:class:`pyctrl.block.Block`
    :param gamma: a constant gain (default `1`)
    :param rho: a constant gain (default `-1`)
    :param m: number of inputs (default `1`)
    """

    def __init__(self, **kwargs):

        self.block = kwargs.pop('block', block.ShortCircuit())
        self.gamma = kwargs.pop('gamma', 1)
        self.rho = kwargs.pop('rho', -1)
        self.m = kwargs.pop('m', 1)

        super().__init__(**kwargs)
    
    def reset(self):
        """
        Reset `Feedback` block.

        Calls `block.reset()`.
        """
        self.block.reset()

    def write(self, *values):
        """
        Writes feedback signal to the private :py:attr:`buffer`.

        :param vararg values: values
        """

        # call super
        super().write(*values)
        
        # calculate error
        error = tuple(self.gamma*r+self.rho*y for (r,y) in zip(self.buffer[self.m:], self.buffer[:self.m]))

        # call block
        self.block.write(*error)
        
        # then read
        self.buffer = self.block.read()

class Average(block.BufferBlock):
    r"""
    :py:class:`pyctrl.block.system.Average` calculates the (weighted) average of all inputs, that is

    :math:`y = \sum_{i = 0}^{m-1} w[i] u[i]`,

    where :math:`w` is a vector of weights

    :param weights: weights (default :math:`1/m`)
    """

    def __init__(self, **kwargs):

        self.weights = kwargs.pop('weights', None)
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
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
                
        super().set(exclude, **kwargs)

    def write(self, *values):
        """
        Writes average of the current input to the private :py:attr:`buffer`.

        :param vararg values: list of values
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


class Sum(Gain):
    """
    :py:class:`pyctrl.block.system.Sum` adds all inputs and multiplies the result by a constant gain, that is

    :math:`y = a \sum_{i = 0}^{m-1} u[m]`,

    where :math:`a` is the gain.

    :param float gain: multiplier (default `1`)
    """

    def write(self, *values):
        """
        Writes product of `gain` times the sum of the current input to the private `buffer`.

        :param vararg values: list of values
        :return: tuple with scaled input
        """
        # call super
        super(Gain, self).write(*values)
        
        self.buffer = (self.gain * numpy.sum(self.buffer, axis=0), )
        

class Subtract(Gain):
    r"""
    :py:class:`pyctrl.block.system.Subtract` subtracts first input as in

    :math:`y = a \sum_{i = 1}^{m-1} u[m] - u[0]`,

    where :math:`a` is the gain.

    :param float gain: multiplier (default `1`)
    """

    def write(self, *values):
        """
        Writes product of `gain` times the difference of the current input to the private `buffer`.

        :param vararg values: list of values
        :return: tuple with scaled input
        """

        # call super
        super(Gain, self).write(*values)
        
        if self.buffer:
            # flip first entry
            self.buffer = (-self.buffer[0],) + self.buffer[1:]

        # calculate sum
        self.buffer = (self.gain * numpy.sum(self.buffer, axis=0), )
