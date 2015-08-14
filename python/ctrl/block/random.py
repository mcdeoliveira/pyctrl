import random

from .. import block

class RandomUniform(block.Block):

    def __init__(self, a = 0, b = 1, seed = None, *vars, **kwargs):

        self.a = a
        self.b = b
        self.seed = seed

        self.reset()

        super().__init__(*vars, **kwargs)

    def reset(self):
        
        if self.seed is not None:
            random.seed(self.seed)

    def set(self, **kwargs):
        
        if 'a' in kwargs:
            self.a = kwargs.pop('a')

        if 'b' in kwargs:
            self.b = kwargs.pop('b')

        if 'seed' in kwargs:
            self.seed = kwargs.pop('seed')
            self.reset()
        
        super().set(**kwargs)

    def read(self):

        return (random.uniform(self.a, self.b), )

class RandomGaussian(block.Block):

    def __init__(self, mu = 0, sigma = 1, seed = None, *vars, **kwargs):

        self.mu = mu
        self.sigma = sigma
        self.seed = seed

        self.reset()

        super().__init__(*vars, **kwargs)

    def reset(self):
        
        if self.seed is not None:
            random.seed(self.seed)

    def set(self, **kwargs):
        
        if 'mu' in kwargs:
            self.mu = kwargs.pop('mu')

        if 'sigma' in kwargs:
            self.sigma = kwargs.pop('sigma')

        if 'seed' in kwargs:
            self.seed = kwargs.pop('seed')
            self.reset()

        super().set(**kwargs)

    def read(self):

        return (random.gauss(self.mu, self.sigma), )
