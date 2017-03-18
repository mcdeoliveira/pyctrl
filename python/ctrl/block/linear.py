"""
This module provides blocks for linear dynamic systems.
"""

import numpy

from .. import block
from ctrl.system.tf import DTTF, SISOSystem
from ctrl.system.ss import DTSS, MIMOSystem
from ctrl.system.tv import TVSystem

# Blocks

class SISO(block.BufferBlock):
    """
    *SISO* is a wrapper for a single-input-single-output dynamic
    system model. 

    :param model: an instance of `ctrl.system.SISOSystem`
    """
    
    def __init__(self, model = DTTF(), *vars, **kwargs):

        assert isinstance(model, SISOSystem)
        self.model = model

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of `SISO` block.

        :param model: an instance of `ctrl.system.SISOSystem`
        """
        
        if 'model' in kwargs:
            model = kwargs.pop('model')
            assert isinstance(model, SISOSystem)
            self.model = model

        super().set(**kwargs)

    def reset(self):
        """
        Reset `SISO` block.

        Calls `model.set_output(0)`.
        """

        self.model.set_output(0)
        
    def write(self, *values):
        """
        Writes current output of `model` to the private `buffer`.

        :param values: list of values of length equal to one
        :return: tuple with current model output
        """

        assert len(values) == 1
        self.buffer = (self.model.update(values[0]), )

class MIMO(block.BufferBlock):
    """
    *MIMO* is a wrapper for a multi-input-multi-output dynamic
    system model. 

    :param model: an instance of `ctrl.system.MIMOSystem`
    """

    def __init__(self, model = DTSS(), *vars, **kwargs):
        """
        Wrapper for state-space model as a Block
        """

        self.model = model
        assert isinstance(self.model, MIMOSystem)

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of `MIMO` block.

        :param model: an instance of `ctrl.system.MIMOSystem`
        """

        if 'model' in kwargs:
            model = kwargs.pop('model')
            assert isinstance(model, MIMOSystem)
            self.model = model

        super().set(**kwargs)

    def reset(self):
        """
        Reset `MIMO` block.

        Calls `model.set_state(0 * model.get_state())`.
        """
        self.model.set_state(0 * self.model.get_state())
        
    def write(self, *values):
        """
        Writes current output of `model` to the private `buffer`.

        :param values: list of values
        :return: tuple with current model output
        """

        # convert input to array
        uk = numpy.hstack(values)

        # update model
        self.buffer = self.model.update(uk).tolist()

class TimeVarying(block.BufferBlock):
    """
    *TimeVarying* is a wrapper for a multi-input-multi-output dynamic
    time-varying system model.

    :param model: an instance of `ctrl.system.TVSystem`
    """

    def __init__(self, model = TVSystem(), *vars, **kwargs):

        assert isinstance(model, TVSystem)
        self.model = model

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of `TimeVarying` block.

        :param model: an instance of `ctrl.system.TVSystem`
        """

        if 'model' in kwargs:
            model = kwargs.pop('model')
            assert isinstance(model, TVSystem)
            self.model = 'model'

        super().set(**kwargs)

    def reset(self):
        """
        Reset `TimeVarying` block.

        Calls `model.set_state(0 * model.get_state())`.
        """
        self.model.set_state(0 * self.model.get_state())
        
    def write(self, *values):
        """
        Writes current output of `model` to the private `buffer`.

        :param values: list of values
        :return: tuple with current model output
        """

        # time comes first 
        tk = values[0]

        # convert input to array
        uk = numpy.hstack(values[1:])

        # update model
        self.buffer = self.model.update(tk, uk).tolist()

class Gain(block.BufferBlock):
    """
    *Gain* multiplies input by a constant gain.

    :param gain: multiplier (default `1`)
    """
    def __init__(self, gain = 1, *vars, **kwargs):

        assert isinstance(gain, (int, float))
        self.gain = gain

        super().__init__(*vars, **kwargs)
    
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

        :param values: list of values
        :return: tuple with scaled input
        """

        self.buffer = tuple(v*self.gain for v in values)

class Affine(block.BufferBlock):
    """
    *Affine* offset and multiplies input by a constant gain.

    :param gain: multiplier (default `1`)
    :param offset: offset (default `0`)
    """

    def __init__(self, gain = 1, offset = 0, *vars, **kwargs):

        assert isinstance(gain, (int, float))
        self.gain = gain

        assert isinstance(offset, (int, float))
        self.offset = offset

        super().__init__(*vars, **kwargs)
    
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

        :param values: list of values
        :return: tuple with scaled input
        """

        self.buffer = tuple(v*self.gain + self.offset for v in values)

class ShortCircuit(block.BufferBlock):
    """
    *ShortCircuit* copies input to the output.
    """

    def write(self, *values):
        """
        Writes current input to the private `buffer`.

        :param values: list of values
        :return: copy of input
        """

        self.buffer = values

class Constant(block.Block):

    def __init__(self, value = 1, *vars, **kwargs):

        assert isinstance(value, (int, float))
        self.value = value

        super().__init__(*vars, **kwargs)
    
    def read(self):

        return (self.value, )

class Differentiator(block.BufferBlock):

    def __init__(self, *vars, **kwargs):
        """Differentiator
        inputs: clock, signal
        output: derivative
        """
        
        self.time = -1
        self.last = ()

        super().__init__(*vars, **kwargs)

    def get(self, keys = None):

        # call super
        return super().get(keys, exclude = ('time', 'last'))
    
    def write(self, *values):

        #print('values = {}'.format(values))

        t = values[0]
        x = values[1:]

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

    def __init__(self, block = ShortCircuit(), gamma = 1, *vars, **kwargs):
        """
        Feedback connection:
            u = block (error), 
        error = gamma * ref - y
        
        inputs = (y, ref)
        output = (u, )
        """
        self.block = block
        self.gamma = gamma

        super().__init__(*vars, **kwargs)
    
    def reset(self):

        self.block.reset()

    def set(self, **kwargs):
        
        if 'block' in kwargs:
            self.block = kwargs.pop('block')

        if 'gamma' in kwargs:
            self.gamma = kwargs.pop('gamma')

        super().set(**kwargs)

    def write(self, *values):

        # write error to block
        self.block.write(self.gamma * values[1] - values[0])
        
        # then read
        self.buffer = self.block.read()

class Sum(block.BufferBlock):

    def __init__(self, gain = 1., *vars, **kwargs):
        """
        Sum:
            y = \sum_{k = 1}^n u_k
        
        inputs = u
        output = y
        """

        self.gain = gain
        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        
        if 'gain' in kwargs:
            self.gain = float(kwargs.pop('gain'))

        super().set(**kwargs)

    def write(self, *values):

        #(sum(v) for v in values)
        self.buffer = (self.gain*sum(map(numpy.array, values)), )

class Subtract(block.BufferBlock):

    def __init__(self, *vars, **kwargs):
        """
        Sum:
            y = u[1] - u[0]
        
        inputs = u
        output = y
        """

        super().__init__(*vars, **kwargs)
    
    def write(self, *values):

        self.buffer = (values[1]-values[0], )
