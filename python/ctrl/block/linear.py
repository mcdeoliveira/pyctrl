import numpy

from .. import block
from ctrl.system.tf import DTTF, SISOSystem
from ctrl.system.ss import DTSS, MIMOSystem
from ctrl.system.tv import TVSystem

# Blocks

class SISO(block.BufferBlock):

    def __init__(self, model = DTTF(), *vars, **kwargs):
        """
        Wrapper for transfer-function model as a Block
        """

        self.model = model
        assert isinstance(self.model, SISOSystem)

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        
        if 'model' in kwargs:
            self.model = kwargs.pop('model')
            assert isinstance(self.model, SISOSystem)

        super().set(**kwargs)

    def reset(self):

        self.model.set_output(0)
        
    def write(self, *values):

        self.buffer = (self.model.update(values[0]), )

class MIMO(block.BufferBlock):

    def __init__(self, model = DTSS(), *vars, **kwargs):
        """
        Wrapper for state-space model as a Block
        """

        self.model = model
        assert isinstance(self.model, MIMOSystem)

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        
        if 'model' in kwargs:
            self.model = kwargs.pop('model')
            assert isinstance(self.model, MIMOSystem)

        super().set(**kwargs)

    def reset(self):

        self.model.state *= 0
        
    def write(self, *values):

        # convert input to array
        if numpy.isscalar(values[0]):
            uk = numpy.array(list(values))
        else:
            uk = numpy.hstack(values)
        #print('uk = {}'.format(uk))

        # convert output to list
        yk = self.model.update(uk)

        self.buffer = (yk,)

class TimeVarying(block.BufferBlock):

    def __init__(self, model = DTSS(), *vars, **kwargs):
        """
        Wrapper for state-space model as a Block
        """

        self.model = model
        assert isinstance(self.model, TVSystem)

        self.t = kwargs.pop('t', -1)

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        
        if 'model' in kwargs:
            self.model = kwargs.pop('model')
            assert isinstance(self.model, TVSystem)

        super().set(**kwargs)

    def reset(self):

        self.t = -1
        self.model.state *= 0
        
    def write(self, *values):

        #print('values = {}'.format(values))

        # time comes first 
        tk = values[0]
        #print('tk = {}'.format(tk))

        # convert input to array
        if numpy.isscalar(values[1]):
            uk = numpy.array([values[1]])
        else:
            uk = numpy.array(values[1])
        #print('uk = {}'.format(uk))

        # initialize model
        if self.t < 0 or self.model.t0 >= tk:

            self.model.t0 = tk

        # update model
        yk = self.model.update(tk, uk)
        #print('yk = {}'.format(yk))

        # save time
        self.t = tk

        # convert output to list
        self.buffer = (yk, )

class Gain(block.BufferBlock):

    def __init__(self, gain = 1, *vars, **kwargs):

        assert isinstance(gain, (int, float))
        self.gain = gain

        super().__init__(*vars, **kwargs)
    
    def set(self, **kwargs):
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        super().set(**kwargs)

    def write(self, *values):

        self.buffer = tuple(v*self.gain for v in values)

class Affine(block.BufferBlock):

    #
    # output = gain * input + offset
    #

    def __init__(self, gain = 1, offset = 0, *vars, **kwargs):

        assert isinstance(gain, (int, float))
        self.gain = gain

        assert isinstance(offset, (int, float))
        self.offset = offset

        super().__init__(*vars, **kwargs)
    
    def set(self, **kwargs):
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        if 'offset' in kwargs:
            self.gain = kwargs.pop('offset')

        super().set(**kwargs)

    def write(self, *values):

        self.buffer = tuple(v*self.gain + self.offset for v in values)

class ShortCircuit(block.BufferBlock):

    def write(self, *values):

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

    def __init__(self, *vars, **kwargs):
        """
        Sum:
            y = \sum_{k = 1}^n u_k
        
        inputs = u
        output = y
        """

        super().__init__(*vars, **kwargs)
    
    def write(self, *values):

        #(sum(v) for v in values)
        self.buffer = (sum(map(numpy.array, values)), )

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
        
