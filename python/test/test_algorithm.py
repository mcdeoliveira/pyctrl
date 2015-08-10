import sys
sys.path.append('..')

import pytest

import numpy
import math
import ctrl.algo as algo

def test_DZ():

    y = 30
    d = 2
    alg = algo.DeadZoneCompensation(algo.OpenLoop(), y, d)
    assert alg.update(0,100,4) == 100
    assert alg.update(0,d+(100-d)/2,4) == y + (100 - y)/2
    assert alg.update(0,d/2,4) == y/2
    assert alg.update(0,d,4) == y
    assert alg.update(0,0,4) == 0
    assert alg.update(0,-d/2,4) == -y/2
    assert alg.update(0,-d,4) == -y
    assert alg.update(0,-100,4) == -100
    assert alg.update(0,-d-(100-d)/2,4) == -y - (100 - y)/2

    y = 15
    d = 5
    alg = algo.DeadZoneCompensation(algo.OpenLoop(), y, d)
    assert alg.update(0,100,4) == 100
    assert alg.update(0,d+(100-d)/2,4) == y + (100 - y)/2
    assert alg.update(0,d/2,4) == y/2
    assert alg.update(0,d,4) == y
    assert alg.update(0,0,4) == 0
    assert alg.update(0,-d/2,4) == -y/2
    assert alg.update(0,-d,4) == -y
    assert alg.update(0,-100,4) == -100
    assert alg.update(0,-d-(100-d)/2,4) == -y - (100 - y)/2

    y = 10
    d = 10
    alg = algo.DeadZoneCompensation(algo.OpenLoop(), y, d)
    assert alg.update(0,100,4) == 100
    assert alg.update(0,d+(100-d)/2,4) == y + (100 - y)/2
    assert alg.update(0,d/2,4) == y/2
    assert alg.update(0,d,4) == y
    assert alg.update(0,0,4) == 0
    assert alg.update(0,-d/2,4) == -y/2
    assert alg.update(0,-d,4) == -y
    assert alg.update(0,-100,4) == -100
    assert alg.update(0,-d-(100-d)/2,4) == -y - (100 - y)/2
