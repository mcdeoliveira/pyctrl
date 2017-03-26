import random

from .. import block

class RandomUniform(block.Block):

    def __init__(self, **kwargs):

        self.a = kwargs.pop('a', 0)
        self.b = kwargs.pop('b', 1)
        self.seed = kwargs.pop('seed', None)

        super().__init__(**kwargs)

        self.reset()

    def reset(self):
        
        if self.seed is not None:
            random.seed(self.seed)

    def set(self, exclude = (), **kwargs):
        
        if 'a' in kwargs:
            self.a = kwargs.pop('a')

        if 'b' in kwargs:
            self.b = kwargs.pop('b')

        if 'seed' in kwargs:
            self.seed = kwargs.pop('seed')
            self.reset()
        
        super().set(exclude, **kwargs)

    def read(self):

        return (random.uniform(self.a, self.b), )

class RandomGaussian(block.Block):

    def __init__(self, **kwargs):

        self.mu = kwargs.pop('mu', 0)
        self.sigma = kwargs.pop('sigma', 1)
        self.seed = kwargs.pop('seed', None)

        super().__init__(**kwargs)
        
        self.reset()

    def reset(self):
        
        if self.seed is not None:
            random.seed(self.seed)

    def set(self, exclude = (), **kwargs):
        
        if 'mu' in kwargs:
            self.mu = kwargs.pop('mu')

        if 'sigma' in kwargs:
            self.sigma = kwargs.pop('sigma')

        if 'seed' in kwargs:
            self.seed = kwargs.pop('seed')
            self.reset()

        super().set(exclude, **kwargs)

    def read(self):

        return (random.gauss(self.mu, self.sigma), )
