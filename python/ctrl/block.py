class BlockException(Exception):
    pass

class Block:
    
    def __init__(self, enabled  = True):
        self.enabled = enabled

    def is_enabled(self):
        return self.enabled
        
    def set_enabled(self, enabled  = True):
        self.enabled = enabled

    def reset(self):
        pass

    def read(self):
        raise BlockException('This block does not support read')

    def write(self, values):
        raise BlockException('This block does not support write')

class Printer(Block):

    def __init__(self, *vars, **kwargs):

        self.endln = kwargs.pop('endln', '\n')
        self.format_ = kwargs.pop('format', '{:12.2f}')
        self.join_ = kwargs.pop('join', ' ')

        super().__init__(*vars, **kwargs)
    
    def write(self, values):

        print(self.join_.join(self.format_.format(val) for val in values), 
              end=self.endln)

import random

class RandomUniform(Block):

    def __init__(self, *vars, **kwargs):

        self.a = kwargs.pop('a', 0)
        self.b = kwargs.pop('b', 1)

        super().__init__(*vars, **kwargs)

    def read(self):
        return (random.uniform(self.a, self.b), )

class RandomGaussian(Block):

    def __init__(self, *vars, **kwargs):

        self.mu = kwargs.pop('a', 0)
        self.sigma = kwargs.pop('b', 1)

        super().__init__(*vars, **kwargs)

    def read(self):
        return (random.gauss(self.mu, self.sigma), )
