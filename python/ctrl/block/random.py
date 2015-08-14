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

    def set(self, key, value = None):
        
        if key == 'a':
            self.a = value
        elif key == 'b':
            self.b = value
        elif key == 'seed':
            self.seed = value
            self.reset()
        else:
            super().set(key, value)

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

    def set(self, key, value = None):
        
        if key == 'mu':
            self.mu = value
        elif key == 'sigma':
            self.sigma = value
        elif key == 'seed':
            self.seed = value
            self.reset()
        else:
            super().set(key, value)

    def read(self):

        return (random.gauss(self.mu, self.sigma), )
