import pytest

import pyctrl.block as block
import pyctrl.block.system as system
import pyctrl.block.random as blkrnd

def test_random_uniform():

    blk = blkrnd.Uniform()
    (x,) = blk.read()
    assert x >= 0 and x <= 1
    assert blk.low == 0 and blk.high == 1

    blk = blkrnd.Uniform(low = -1, high = 1)
    (x,) = blk.read()
    assert x >= -1 and x <= 1
    assert blk.low == -1 and blk.high == 1

    blk = blkrnd.Uniform(low = -1, high = 1,seed = 5)
    (x,) = blk.read()
    assert x >= -1 and x <= 1
    assert blk.low == -1 and blk.high == 1

    blk = blkrnd.Uniform(low = -1, high = 1,seed = 5)
    (y,) = blk.read()
    assert x == y

    (y,) = blk.read()
    assert x != y

    blk.reset()
    (y,) = blk.read()
    assert x == y
    
    blk = blkrnd.Uniform(low = -1, high = 1)
    blk.set(seed = 5)
    (y,) = blk.read()
    assert x == y

    blk.set(low = -3)
    assert blk.low == -3

    blk.set(high = 3)
    assert blk.high == 3

def test_random_gaussian():

    blk = blkrnd.Gaussian()
    (x,) = blk.read()
    assert isinstance(x, float)
    assert blk.mu == 0 and blk.sigma == 1

    blk = blkrnd.Gaussian(mu = -1, sigma = 1)
    (x,) = blk.read()
    assert isinstance(x, float)
    assert blk.mu == -1 and blk.sigma == 1

    blk = blkrnd.Gaussian(mu = -1, sigma = 1, seed = 5)
    (x,) = blk.read()
    assert isinstance(x, float)
    assert blk.mu == -1 and blk.sigma == 1

    blk = blkrnd.Gaussian(mu = -1, sigma = 1,seed = 5)
    (y,) = blk.read()
    assert x == y
    
    blk = blkrnd.Gaussian(mu = -1, sigma = 1)
    blk.set(seed = 5)
    (y,) = blk.read()
    assert x == y

    (y,) = blk.read()
    assert x != y

    blk.reset()
    (y,) = blk.read()
    assert x == y

    blk.set(mu = -3)
    assert blk.mu == -3

    blk.set(sigma = 3)
    assert blk.sigma == 3


if __name__ == "__main__":

    test_random_uniform()
    test_random_gaussian()
