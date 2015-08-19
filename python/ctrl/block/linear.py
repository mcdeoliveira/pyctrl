import numpy

from .. import block
from ctrl.system.tf import DTTF

# Blocks

class TransferFunction(block.BufferBlock):

    def __init__(self, model = DTTF(), *vars, **kwargs):
        """
        Wrapper for TransferFunction as a Block
        """

        self.model = model

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        
        if 'model' in kwargs:
            self.model = kwargs.pop('model')

        super().set(**kwargs)

    def reset(self):

        self.model.set_output(0)
        
    def write(self, values):

        self.buffer = (self.model.update(values[0]), )

class Gain(block.BufferBlock):

    def __init__(self, gain = 1, *vars, **kwargs):

        assert isinstance(gain, (int, float))
        self.gain = gain

        super().__init__(*vars, **kwargs)
    
    def set(self, **kwargs):
        
        if 'gain' in kwargs:
            self.gain = kwargs.pop('gain')

        super().set(**kwargs)

    def write(self, values):

        self.buffer = tuple(value*self.gain for value in values)

class ShortCircuit(block.BufferBlock):

    def write(self, values):

        self.buffer = tuple(values)

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
        return super().get(keys, exclude = ('time','last'))
    
    def write(self, values):

        #print('values = {}'.format(values))

        t = values[0]
        x = values[1:]
        if self.time > 0:
            dt = t - self.time
        else:
            dt = 0
        
        if dt > 0:
            self.time, self.last, self.buffer = t, x, \
                [(n-o)/dt for n,o in zip(x, self.last)]
        else:
            self.time, self.last, self.buffer = t, x, (len(x))*[0.]

class Feedback(block.BufferBlock):

    def __init__(self, block = ShortCircuit(), gamma = 100, *vars, **kwargs):
        """
        Feedback connection:
            u = block (error), 
        error = gamma * ref - y
        
        inputs = (y, ref)
        output = (u, )
        """
        self.block = block
        self.gamma = gamma/100

        super().__init__(*vars, **kwargs)
    
    def set(self, **kwargs):
        
        if 'block' in kwargs:
            self.block = kwargs.pop('block')

        if 'gamma' in kwargs:
            self.gamma = kwargs.pop('gamma')/100

        super().set(**kwargs)

    def write(self, values):

        # write error to block
        self.block.write((self.gamma * values[1] - values[0], ))
        
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
    
    def write(self, values):

        self.buffer = (sum(values), )
