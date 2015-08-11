import sys
sys.path.append('..')

import pytest

import numpy as np
import ctrl.linear as linear

def test1():

    num = np.array([1, 1])
    den = np.array([1, -1])
    sys = linear.TFModel(num, den)
    assert np.all(sys.num == num)
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))

    num = np.array([1, 1])
    den = np.array([2, -1])
    sys = linear.TFModel(num, den)
    assert np.all(sys.num == num/2)
    assert np.all(sys.den == den/2)
    assert np.all(sys.state == np.zeros(2))

    num = np.array([1, 1, 3])
    den = np.array([1, -1])
    sys = linear.TFModel(num, den)
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

    sys.set_output(0)
    yk = sys.update(0)
    assert yk == 0

    sys.set_output(3)
    yk = sys.update(0)
    assert yk == 3
    
def test2():

    # PID = PI
    ierror = 0
    error = 0
    alg = linear.PID(3, 4, period = 6)
    err = 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror
    error = err

    err = -1 - 2
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror
    error = err

    # PID = PI + gain
    ierror = 0
    error = 0
    alg = linear.PID(3, 4, 0, period = 6)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror
    error = err

    err = -2/100*(-1) - 2
    ierror += 6. * (err + error) / 2
    assert abs(alg.update(err) - (3 * err + 4 * ierror)) < 1e-6
    error = err

    # PID = PID
    ierror = 0
    error = 0
    alg = linear.PID(3, 4, .5, period = 6)
    err = 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(err) == 3 * err + 4 * ierror + .5 * (err - error) / 6
    error = err

    err = -1 - 2
    ierror += 6. * (err + error) / 2
    assert abs(alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 6)) < 1e-6
    error = err

    # PID = PID + gain
    ierror = 0
    error = 0
    alg = linear.PID(3, 4, .5, period = 6)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert (alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 6)) < 1e-6
    error = err

    err = -2/100*(-1) - 2
    ierror += 6. * (err + error) / 2
    assert (alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 4)) < 1e-6
    error = err

def test3():

    signals = { 'clock' : 1, 'encoder1' : 2 , 'test' : 3}
    labels = ['clock', 'encoder1']

    diff = linear.Differentiator()
    diff.write(signals[label] for label in labels)
    result = diff.read()
    assert result == ([0])

    signals = { 'clock' : 2, 'encoder1' : 5 , 'test' : 3}

    diff.write(signals[label] for label in labels)
    result = diff.read()
    assert result == ([3])

    signals = { 'clock' : 4, 'encoder1' : 6 , 'test' : 3}

    diff.write(signals[label] for label in labels)
    result = diff.read()
    assert result == ([.5])

if __name__ == "__main__":

    test1()
    test2()
    test3()
