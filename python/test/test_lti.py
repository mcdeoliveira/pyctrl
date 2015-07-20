import sys
sys.path.append('..')

import pytest

import numpy as np
import ctrl.lti as lti

def test0():

    Ts = 0.1
    num = np.array([1, 1])
    den = np.array([1, -1])
    sys = lti.SISOLTISystem(Ts, num, den)
    assert np.all(sys.num == num)
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))

    num = np.array([1, 1])
    den = np.array([2, -1])
    sys = lti.SISOLTISystem(Ts, num, den)
    assert np.all(sys.num == num/2)
    assert np.all(sys.den == den/2)
    assert np.all(sys.state == np.zeros(2))

    num = np.array([1, 1, 3])
    den = np.array([1, -1])
    sys = lti.SISOLTISystem(Ts, num, den)
    assert np.all(sys.num == num)
    den = np.array([1, -1, 0])
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))

    sys.update(1)
    state = np.array([1, 0])
    assert np.all(sys.state == state)

    sys.update(-1)
    state = np.array([0, 1])
    assert np.all(sys.state == state)

    sys.update(2)
    state = np.array([2, 0])
    assert np.all(sys.state == state)

    sys.update(1)
    state = np.array([3, 2])
    assert np.all(sys.state == state)

    sys.set_position(0)
    yk = sys.update(0)
    assert yk == 0

    sys.set_position(3)
    yk = sys.update(0)
    assert yk == 3
    
