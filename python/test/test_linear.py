import sys
sys.path.append('..')

import pytest

import numpy as np
import ctrl.block as block
import ctrl.block.linear as linear

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

    yk = sys.update(1)
    state = np.array([1, 0])
    assert np.all(sys.state == state)
    assert yk == 1

    yk = sys.update(-1)
    state = np.array([0, 1])
    assert np.all(sys.state == state)
    assert yk == 1

    yk = sys.update(2)
    state = np.array([2, 0])
    assert np.all(sys.state == state)
    assert yk == 5

    yk = sys.update(1)
    state = np.array([3, 2])
    assert np.all(sys.state == state)
    assert yk == 5

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

    # Transfer-function

    num = np.array([1, 1, 3])
    den = np.array([1, -1])
    sys = linear.TFModel(num, den)
    assert np.all(sys.num == num)
    den = np.array([1, -1, 0])
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))

    blk = linear.TransferFunction(sys)
    assert blk.model is sys

    with pytest.raises(block.BlockException):
        blk = linear.TransferFunction(modelo = sys)

    blk.write([1])
    (yk,) = blk.read()
    state = np.array([1, 0])
    assert np.all(sys.state == state)
    assert yk == 1

    blk.write([-1])
    (yk,) = blk.read()
    state = np.array([0, 1])
    assert np.all(sys.state == state)
    assert yk == 1

    blk.write([2])
    (yk,) = blk.read()
    state = np.array([2, 0])
    assert np.all(sys.state == state)
    assert yk == 5

    blk.write([1])
    (yk,) = blk.read()
    state = np.array([3, 2])
    assert np.all(sys.state == state)
    assert yk == 5

    blk.reset()
    yk = sys.update(0)
    assert yk == 0

    num = np.array([1, 1])
    den = np.array([1, -1])
    sys2 = linear.TFModel(num, den)

    blk = linear.TransferFunction(sys)
    blk.set('model', sys2)
    assert blk.model is sys2

    # Gain

    blk = linear.Gain()
    assert blk.gain == 1

    blk = linear.Gain(-1)
    assert blk.gain == -1

    blk = linear.Gain(gain = 3)
    assert blk.gain == 3

    blk = linear.Gain(-1.2)
    assert blk.gain == -1.2

    with pytest.raises(AssertionError):
        blk = linear.Gain('asd')

    with pytest.raises(AssertionError):
        blk = linear.Gain((1,2))

    blk = linear.Gain(-5.2)
    blk.write([2])
    (yk,) = blk.read()
    assert yk == -10.4

    blk = linear.Gain(3)
    blk.write([2, 4])
    yk = blk.read()
    assert yk == (6, 12)

    blk.write((2, 4))
    yk = blk.read()
    assert yk == (6, 12)

    blk.set('gain', 8)
    assert blk.gain == 8

    # Short-Circuit

    blk = linear.ShortCircuit()

    with pytest.raises(block.BlockException):
        blk = linear.ShortCircuit('asd')

    blk.write([2])
    (yk,) = blk.read()
    assert yk == 2

    blk.write([2, 4])
    yk = blk.read()
    assert yk == (2, 4)

    blk.write((2, 4))
    yk = blk.read()
    assert yk == (2, 4)

    # Differentiator

    diff = linear.Differentiator()
    diff.write([signals[label] for label in labels])
    result = diff.read()
    assert result == ([0])

    signals = { 'clock' : 2, 'encoder1' : 5 , 'test' : 3}

    diff.write([signals[label] for label in labels])
    result = diff.read()
    assert result == ([3])

    signals = { 'clock' : 4, 'encoder1' : 6 , 'test' : 3}

    diff.write([signals[label] for label in labels])
    result = diff.read()
    assert result == ([.5])

    with pytest.raises(block.BlockException):
        blk.set('time', 8)

    with pytest.raises(block.BlockException):
        blk.set('last', 8)

    # Feedback

    blk1 = linear.Gain(2)
    blk = linear.Feedback(blk1)
    assert blk.block is blk1
    assert blk.gamma == 1.0

    blk = linear.Feedback(block = blk1)
    assert blk.block is blk1
    assert blk.gamma == 1.0

    blk = linear.Feedback(block = blk1, gamma = 2)
    assert blk.block is blk1
    assert blk.gamma == 2/100

    blk.write([2,3])
    (yk, ) = blk.read()
    assert yk == 2 * (3 * 2 / 100 - 2)

    gn = linear.Gain(150)
    blk.set('block', gn)
    assert blk.block is gn

    blk.set('gamma', 10)
    assert blk.gamma == 0.1

    # Sum
    blk = linear.Sum()
    
    blk.write([1])
    (yk, ) = blk.read()
    assert yk == 1

    blk.write([])
    (yk, ) = blk.read()
    assert yk == 0

    blk.write([1, 2])
    (yk, ) = blk.read()
    assert yk == 3

    blk.write([1, .4])
    (yk, ) = blk.read()
    assert yk == 1.4

if __name__ == "__main__":

    test1()
    test2()
    test3()
