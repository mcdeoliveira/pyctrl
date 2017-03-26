import pytest

import ctrl.block as block
import ctrl.block.system as system
import ctrl.block.random as blkrnd

def test_random_uniform():

    blk = blkrnd.RandomUniform()
    (x,) = blk.read()
    assert x >= 0 and x <= 1
    assert blk.a == 0 and blk.b == 1

    blk = blkrnd.RandomUniform(a = -1, b = 1)
    (x,) = blk.read()
    assert x >= -1 and x <= 1
    assert blk.a == -1 and blk.b == 1

    blk = blkrnd.RandomUniform(a = -1, b = 1,seed = 5)
    (x,) = blk.read()
    assert x >= -1 and x <= 1
    assert blk.a == -1 and blk.b == 1

    blk = blkrnd.RandomUniform(a = -1, b = 1,seed = 5)
    (y,) = blk.read()
    assert x == y

    (y,) = blk.read()
    assert x != y

    blk.reset()
    (y,) = blk.read()
    assert x == y
    
    blk = blkrnd.RandomUniform(a = -1, b = 1)
    blk.set(seed = 5)
    (y,) = blk.read()
    assert x == y

    blk.set(a = -3)
    assert blk.a == -3

    blk.set(b = 3)
    assert blk.b == 3

def test_random_gaussian():

    blk = blkrnd.RandomGaussian()
    (x,) = blk.read()
    assert isinstance(x, float)
    assert blk.mu == 0 and blk.sigma == 1

    blk = blkrnd.RandomGaussian(mu = -1, sigma = 1)
    (x,) = blk.read()
    assert isinstance(x, float)
    assert blk.mu == -1 and blk.sigma == 1

    blk = blkrnd.RandomGaussian(mu = -1, sigma = 1, seed = 5)
    (x,) = blk.read()
    assert isinstance(x, float)
    assert blk.mu == -1 and blk.sigma == 1

    blk = blkrnd.RandomGaussian(mu = -1, sigma = 1,seed = 5)
    (y,) = blk.read()
    assert x == y
    
    blk = blkrnd.RandomGaussian(mu = -1, sigma = 1)
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
