import numpy.random

from .. import block

class Uniform(block.BufferBlock):
    """
    :py:class:`pyctrl.block.random.Uniform` produces an output with random entries uniformly distributed between :py:attr:`low` and :py:attr:`high`.

    :py:class:`pyctrl.block.random.Uniform` uses :py:meth:`numpy.random.uniform`.

    :param float low: lowest value (default `0`)
    :param float high: highest value (default `1`)
    :param int m: number of output (default `1`)
    :param seed: seed (default None)
    """
    def __init__(self, **kwargs):

        self.low = kwargs.pop('low', 0)
        self.high = kwargs.pop('high', 1)

        m = kwargs.pop('m', 1)
        if not isinstance(m, int):
            raise block.BlockException('m must be int')
        self.m = m
        
        self.seed = kwargs.pop('seed', None)

        super().__init__(**kwargs)

        self.reset()

    def reset(self):
        """
        Resets :py:class:`pyctrl.block.random.Uniform` by reseeding generator.
        """
        
        if self.seed is not None:
            numpy.random.seed(self.seed)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.random.Uniform`.

        :param float low: lowest value
        :param float high: highest value
        :param int m: number of outputs
        :param seed: seed
        """
        
        if 'low' in kwargs:
            self.low = kwargs.pop('low')

        if 'high' in kwargs:
            self.high = kwargs.pop('high')

        if 'm' in kwargs:
            m = kwargs.pop('m', 1)
            if not isinstance(m, int):
                raise block.BlockException('m must be int')
            self.m = m
        
        if 'seed' in kwargs:
            self.seed = kwargs.pop('seed')
            self.reset()
        
        super().set(exclude, **kwargs)

    def read(self):
        """
        Writes random numbers to private :py:attr:`buffer`.
        """

        self.buffer = numpy.random.uniform(self.low, self.high, (self.m,))

        # call super
        return super().read()
    
class Gaussian(block.BufferBlock):
    """
    :py:class:`pyctrl.block.random.Gaussian` produces an output with random entries normally distributed with parameters :py:attr:`mu` and :py:attr:`sigma`.

    :py:class:`pyctrl.block.random.Gaussian` uses :py:meth:`numpy.random.normal`.

    :param float mu: mean (default `0`)
    :param float sigma: variance (default `1`)
    :param int m: number of outputs (default `1`)
    :param seed: seed (default None)
    """

    def __init__(self, **kwargs):

        self.mu = kwargs.pop('mu', 0)
        self.sigma = kwargs.pop('sigma', 1)

        m = kwargs.pop('m', 1)
        if not isinstance(m, int):
            raise block.BlockException('m must be int')
        self.m = m
        
        self.seed = kwargs.pop('seed', None)

        super().__init__(**kwargs)
        
        self.reset()

    def reset(self):
        """
        Resets :py:class:`pyctrl.block.random.Gaussian` by reseeding generator.
        """
        
        if self.seed is not None:
            numpy.random.seed(self.seed)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.random.Gaussian`.

        :param float mu: mean
        :param float sigma: variance
        :param int m: number of outputs
        :param seed: seed
        """
        
        if 'mu' in kwargs:
            self.mu = kwargs.pop('mu')

        if 'sigma' in kwargs:
            self.sigma = kwargs.pop('sigma')

        if 'm' in kwargs:
            m = kwargs.pop('m', 1)
            if not isinstance(m, int):
                raise block.BlockException('m must be int')
            self.m = m
            
        if 'seed' in kwargs:
            self.seed = kwargs.pop('seed')
            self.reset()

        super().set(exclude, **kwargs)

    def read(self):
        """
        Writes random numbers to private :py:attr:`buffer`.
        """

        self.buffer = numpy.random.normal(self.mu, self.sigma, (self.m,))

        # call super
        return super().read()
