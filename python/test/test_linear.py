import sys
sys.path.append('..')

import pytest

import numpy as np
import ctrl.block as block
import ctrl.block.linear as linear
import ctrl.system.tf as tf
import ctrl.system.ss as ss

def test1():

    signals = { 'clock' : 1, 'encoder1' : 2 , 'test' : 3}
    labels = ['clock', 'encoder1']

    # Transfer-function

    num = np.array([1, 1, 3])
    den = np.array([1, -1])
    sys = tf.DTTF(num, den)
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
    sys2 = tf.DTTF(num, den)

    blk = linear.TransferFunction(sys)
    blk.set(model = sys2)
    assert blk.model is sys2

    # State space

    A = np.array([[0,1],[1, -2]])
    B = np.array([[0],[1]])
    C = np.array([[1,-2],[0,1]])
    D = np.array([[1],[0]])
    sys = ss.DTSS(A, B, C, D)
    assert np.all(sys.A == A)
    assert np.all(sys.B == B)
    assert np.all(sys.C == C)
    assert np.all(sys.D == D)
    assert np.all(sys.state == np.zeros(2))

    blk = linear.StateSpace(sys)
    assert blk.model is sys

    with pytest.raises(block.BlockException):
        blk = linear.StateSpace(modelo = sys)

    blk.write([1])
    yk = blk.read()
    state = np.array([[0], [1]])
    assert np.all(sys.state == state)
    assert yk == [1,0]

    blk.write([-1])
    yk = blk.read()
    state = np.array([[1], [-3]])
    assert np.all(sys.state == state)
    assert yk == [-3, 1]

    blk.write([3])
    yk = blk.read()
    state = np.array([[-3], [10]])
    assert np.all(sys.state == state)
    assert yk == [10, -3]

    blk.write([0])
    yk = blk.read()
    state = np.array([[10], [-23]])
    assert np.all(sys.state == state)
    assert yk == [-23, 10]

    blk.reset()
    assert np.all(sys.state == [[0], [0]])

    # MIMO
    A = np.array([[0,1],[1, -2]])
    B = np.array([[1,-1],[1,0]])
    C = np.array([[1,-2],[0,1]])
    D = np.array([[1,0],[-1,1]])
    sys = ss.DTSS(A, B, C, D)
    assert np.all(sys.A == A)
    assert np.all(sys.B == B)
    assert np.all(sys.C == C)
    assert np.all(sys.D == D)
    assert np.all(sys.state == np.zeros(2))

    blk = linear.StateSpace(sys)
    assert blk.model is sys

    # u1 = 1   =>  y1 = 1

    blk.write([1,1])
    y2 = blk.read()
    assert np.all(sys.state == np.array([[0],[1]]))
    assert y2 == [1,0]

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3

    blk.write([-1,0])
    y2 = blk.read()
    assert np.all(sys.state == np.array([[0],[-3]]))
    assert y2 == [-3,2]

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10

    blk.write([3,-1])
    y2 = blk.read()
    assert np.all(sys.state == np.array([[1],[9]]))
    assert y2 == [9,-7]

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23

    blk.write([2,1])
    y2 = blk.read()
    assert np.all(sys.state == np.array([[10],[-15]]))
    assert y2 == [-15,8]

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

    blk.set(gain = 8)
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
        blk.set(time = 8)

    with pytest.raises(block.BlockException):
        blk.set(last = 8)

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
    blk.set(block = gn)
    assert blk.block is gn

    blk.set(gamma = 10)
    assert blk.gamma == 0.1

    # Feedback with transfer-function
    #
    # G(z) = -.5/(z - .5)

    # TODO: CHECK DIFFERENT SIZES NUM/DEN
    blk1 = linear.TransferFunction(tf.zDTTF([-.5, 0], [-.5, 1]))
    blktf = linear.Feedback(blk1)
    assert blktf.block is blk1

    # A = .5, B = 1, C = -.5, D = 0
    #
    # u = C x + D (- y + r)
    # x = A x + B (- y + r)
    
    A = np.array([[.5]])
    B = np.array([[-1, 1]])
    C = np.array([[-.5]])
    D = np.array([[0, 0]])
    blkss = linear.StateSpace(ss.DTSS(A,B,C,D))
    
    blktf.write([1,3])
    yk1 = list(blktf.read())

    blkss.write([1,3])
    yk2 = blkss.read()
    
    assert yk1 == yk2
    
    blktf.write([-1,3])
    yk1 = list(blktf.read())

    blkss.write([-1,3])
    yk2 = blkss.read()

    assert yk1 == yk2

    blktf.write([-1,3])
    yk1 = list(blktf.read())

    blkss.write([-1,3])
    yk2 = blkss.read()

    assert yk1 == yk2

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
