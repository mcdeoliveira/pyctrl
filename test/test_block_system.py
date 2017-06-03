import pytest

import numpy as np
import pyctrl.block as block
import pyctrl.block.system as system
import pyctrl.system.tf as tf
import pyctrl.system.ss as ss

test_ode = True
try:
    import pyctrl.system.ode as ode
except:
    test_ode = False

def test_System():

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

    blk = system.System(model = sys)
    assert blk.model is sys

    with pytest.raises(block.BlockException):
        blk = system.System(modelo = sys)

    with pytest.raises(block.BlockException):
        blk = system.System(model = 1)
        
    with pytest.raises(block.BlockException):
        blk = system.System(model = sys, mux = False)
        
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

    blk = system.System(model = sys)
    blk.set(model = sys2)
    assert blk.model is sys2
    with pytest.raises(block.BlockException):
        blk.set(model = 1)

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

    blk = system.System(model = sys)
    assert blk.model is sys

    with pytest.raises(block.BlockException):
        blk = system.System(modelo = sys)

    blk.write([1])
    yk = blk.read()
    state = np.array([0, 1])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([1,0]))

    blk.write([-1])
    yk = blk.read()
    state = np.array([1, -3])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([-3, 1]))

    blk.write([3])
    yk = blk.read()
    state = np.array([-3, 10])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([10, -3]))

    blk.write([0])
    yk = blk.read()
    state = np.array([10, -23])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([-23, 10]))

    blk.reset()
    assert np.all(sys.state == [0, 0])

    # SIMO

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

    blk = system.System(model = sys)
    assert blk.model is sys

    with pytest.raises(block.BlockException):
        blk = system.System(modelo = sys)

    blk.write(1)
    yk = blk.read()
    state = np.array([0, 1])
    #print(sys.state)
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([1,0]))

    blk.write([-1])
    yk = blk.read()
    state = np.array([1, -3])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([-3, 1]))

    blk.write(3)
    yk = blk.read()
    state = np.array([-3, 10])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([10, -3]))

    blk.write([0])
    yk = blk.read()
    state = np.array([10, -23])
    assert np.all(sys.state == state)
    assert np.all(yk == np.array([-23, 10]))

    blk.reset()
    assert np.all(sys.state == [0, 0])

    # System
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

    blk = system.System(model = sys)
    assert blk.model is sys

    # u1 = 1   =>  y1 = 1

    blk.write([1,1])
    y2 = blk.read()
    assert np.all(sys.state == np.array([0,1]))
    assert np.all(y2 == np.array([1,0]))

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3

    blk.write([-1,0])
    y2 = blk.read()
    assert np.all(sys.state == np.array([0,-3]))
    assert np.all(y2 == np.array([-3,2]))

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10

    blk.write([3,-1])
    y2 = blk.read()
    assert np.all(sys.state == np.array([1,9]))
    assert np.all(y2 == np.array([9,-7]))

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23

    blk.write([2,1])
    y2 = blk.read()
    assert np.all(sys.state == np.array([10,-15]))
    assert np.all(y2 == np.array([-15,8]))

    # Test to work with multiple signals

    # reset state
    blk.reset()
    
    # u1 = 1   =>  y1 = 1

    blk.write(1,1)
    y2 = blk.read()
    assert np.all(sys.state == np.array([0,1]))
    assert np.all(y2 == np.array([1,0]))

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3

    blk.write(-1,0)
    y2 = blk.read()
    assert np.all(sys.state == np.array([0,-3]))
    assert np.all(y2 == np.array([-3,2]))

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10

    blk.write(3,-1)
    y2 = blk.read()
    assert np.all(sys.state == np.array([1,9]))
    assert np.all(y2 == np.array([9,-7]))

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23

    blk.write(2,1)
    y2 = blk.read()
    assert np.all(sys.state == np.array([10,-15]))
    assert np.all(y2 == np.array([-15,8]))

    
def test_Gain():

    # Gain

    blk = system.Gain()
    assert blk.gain == 1

    blk = system.Gain(gain = -1)
    assert blk.gain == -1

    blk = system.Gain(gain = 3)
    assert blk.gain == 3

    blk = system.Gain(gain = -1.2)
    assert blk.gain == -1.2

    with pytest.raises(block.BlockException):
        blk = system.Gain(gain = 'asd')

    blk = system.Gain(gain = -5.2)
    blk.write(np.array([2]))
    (yk,) = blk.read()
    assert yk == -10.4

    blk = system.Gain(gain = 3)
    blk.write(2, 4)
    yk = blk.read()
    assert yk == (6, 12)

    blk.write(np.array([2, 4]))
    (yk,) = blk.read()
    assert np.all(yk == [6, 12])

    blk.write(2, np.array([4,2]))
    yk = blk.read()
    assert yk[0] == 6 and np.all(yk[1] == np.array([12, 6]))

    blk.set(gain = 8)
    assert blk.gain == 8

    blk = system.Gain(gain = (-1,2), demux = True)
    blk.write(1)
    yk = blk.read()
    assert yk == (-1, 2)

    blk = system.Gain(gain = np.array([-1,2]), demux = True)
    blk.write(1)
    yk = blk.read()
    assert yk == (-1, 2)

    with pytest.raises(block.BlockException):
        blk = system.Gain(gain = np.array([[-1,2],[3,1]]),
                          mux = True, demux = True)
    
def test_Affine():

    # Affine

    blk = system.Affine()
    assert blk.gain == 1
    assert blk.offset == 0

    blk = system.Affine(gain = -1, offset = 2)
    assert blk.gain == -1
    assert blk.offset == 2

    blk = system.Affine(offset = 3)
    assert blk.gain == 1
    assert blk.offset == 3

    blk = system.Affine(gain = -1.2, offset = 2.2)
    assert blk.gain == -1.2
    assert blk.offset == 2.2

    with pytest.raises(block.BlockException):
        blk = system.Affine(gain = 'asd')

    with pytest.raises(block.BlockException):
        blk = system.Affine(offset = 'asd')
        
    blk = system.Affine(gain = -5.2)
    blk.write(np.array([2]))
    (yk,) = blk.read()
    assert yk == -10.4

    blk = system.Affine(gain = 3)
    blk.write(2, 4)
    yk = blk.read()
    assert yk == (6, 12)

    blk.write(np.array([2, 4]))
    (yk,) = blk.read()
    assert np.all(yk == [6, 12])

    blk.write(2, np.array([4,2]))
    yk = blk.read()
    assert yk[0] == 6 and np.all(yk[1] == np.array([12, 6]))

    blk.set(gain = 8)
    assert blk.gain == 8

    blk = system.Affine(gain = (-1,2), offset = 1, demux = True)
    blk.write(1)
    yk = blk.read()
    assert yk == (0, 3)

    blk = system.Affine(gain = np.array([-1,2]), offset = 1, demux = True)
    blk.write(1)
    yk = blk.read()
    assert yk == (0, 3)

    blk = system.Affine(gain = np.array([-1,2]), offset = (3,4), demux = True)
    blk.write(1)
    yk = blk.read()
    assert yk == (2, 6)
    
    blk = system.Affine(gain = np.array([-1,2]), offset = np.array([3,4]), demux = True)
    blk.write(1)
    yk = blk.read()
    assert yk == (2, 6)
    
    with pytest.raises(block.BlockException):
        blk = system.Affine(gain = np.array([[-1,2],[3,1]]),
                          mux = True, demux = True)

    with pytest.raises(block.BlockException):
        blk = system.Affine(offset = np.array([[-1,2],[3,1]]),
                          mux = True, demux = True)
        

def test_ShortCircuit():

    # Short-Circuit

    blk = block.ShortCircuit()

    blk.write(2)
    (yk,) = blk.read()
    assert yk == 2

    blk.write(2, 4)
    yk = blk.read()
    assert yk == (2, 4)

    blk.write(np.array([2, 4]))
    (yk,) = blk.read()
    assert np.all(yk == [2, 4])

    blk.write(np.array([2, 4]),-1)
    yk = blk.read()
    assert np.all(yk[0] == [2, 4]) and yk[1] == -1


def test_Differentiator():
    
    # Differentiator

    signals = { 'clock' : 1, 'encoder1' : 5 , 'test' : 0}
    labels = ['clock', 'test']

    diff = system.Differentiator()
    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result == ([0])

    signals = { 'clock' : 2, 'encoder1' : 5 , 'test' : 3}

    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result == ([3])

    signals = { 'clock' : 4, 'encoder1' : 6 , 'test' : 0}

    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result == ([-1.5])

    signals = { 'clock' : 1, 'encoder1' : 5 , 'test' : 0}
    labels = ['clock', 'test', 'encoder1']

    diff = system.Differentiator()
    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result == ([0, 0])

    signals = { 'clock' : 2, 'encoder1' : 5 , 'test' : 3}

    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result == ([3, 0])

    signals = { 'clock' : 4, 'encoder1' : 6 , 'test' : 0}

    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result == ([-1.5, .5])

    signals = { 'clock' : 1, 'encoder1' : 5 , 'test' : np.array([0,1])}
    labels = ['clock', 'test', 'encoder1']

    diff = system.Differentiator()
    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result[1] == 0 and np.all(result[0] == np.array([0,0]))

    signals = { 'clock' : 2, 'encoder1' : 5 , 'test' : np.array([3,2])}

    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result[1] == 0 and np.all(result[0] == np.array([3,1]))

    signals = { 'clock' : 4, 'encoder1' : 6 , 'test' : np.array([0,-1])}

    diff.write(*[signals[label] for label in labels])
    result = diff.read()
    assert result[1] == .5 and np.all(result[0] == np.array([-1.5,-1.5]))

    with pytest.raises(block.BlockException):
        diff.set(time = 8)

    with pytest.raises(block.BlockException):
        diff.set(last = 8)

def test_Feedback():

    # Feedback

    blk1 = system.Gain(gain = 2)
    blk = system.Feedback(block = blk1)
    assert blk.block is blk1
    assert blk.gamma == 1.0

    blk = system.Feedback(block = blk1)
    assert blk.block is blk1
    assert blk.gamma == 1.0

    blk = system.Feedback(block = blk1, gamma = 4)
    assert blk.block is blk1
    assert blk.gamma == 4

    blk.write(2,3)
    (yk,) = blk.read()
    assert yk == 2 * (3 * 4 - 2)

    gn = system.Gain(gain = 150)
    blk.set(block = gn)
    assert blk.block is gn

    blk.set(gamma = 10)
    assert blk.gamma == 10

    # Feedback with transfer-function
    #
    # G(z) = -.5/(z - .5)

    # TODO: CHECK DIFFERENT SIZES NUM/DEN
    blk1 = system.System(model = tf.zDTTF([-.5, 0], [-.5, 1]))
    blktf = system.Feedback(block = blk1)
    assert blktf.block is blk1

    # A = .5, B = 1, C = -.5, D = 0
    #
    # u = C x + D (- y + r)
    # x = A x + B (- y + r)
    
    A = np.array([[.5]])
    B = np.array([[-1, 1]])
    C = np.array([[-.5]])
    D = np.array([[0, 0]])
    blkss = system.System(model = ss.DTSS(A,B,C,D))
    
    blktf.write(1,3)
    yk1 = list(blktf.read())

    blkss.write([1,3])
    yk2 = blkss.read()
    
    assert np.all(np.array(yk1) == yk2)
    
    blktf.write(-1,3)
    yk1 = list(blktf.read())

    blkss.write([-1,3])
    yk2 = blkss.read()

    assert np.all(np.array(yk1) == yk2)

    blktf.write(-1,3)
    yk1 = list(blktf.read())

    blkss.write([-1,3])
    yk2 = blkss.read()

    assert np.all(np.array(yk1) == yk2)

    # Reset feedback
    assert blktf.block.model.state == (6.5,)

    blktf.reset()
    assert blktf.block.model.state == (0,)

def test_Sum():
    
    # Sum
    blk = system.Sum()
    
    blk.write(1)
    (yk, ) = blk.read()
    assert yk == 1

    blk.write()
    (yk, ) = blk.read()
    assert yk == 0

    blk.write(1, 2)
    (yk, ) = blk.read()
    assert yk == 3

    blk.write(1, .4)
    (yk, ) = blk.read()
    assert yk == 1.4

    blk.write([1, .4])
    (yk, ) = blk.read()
    assert np.all(yk == [1, .4])

    blk.write([1, .4], [2, 3])
    (yk, ) = blk.read()
    assert np.all(yk == [3, 3.4])

def test_Average():
    
    # Average
    blk = system.Average()
    
    blk.write(1)
    (yk, ) = blk.read()
    assert yk == 1

    blk.write()
    (yk, ) = blk.read()
    assert yk == 0

    blk.write(1, 2)
    (yk, ) = blk.read()
    assert yk == 1.5

    blk.write(1, .4)
    (yk, ) = blk.read()
    assert yk == (1 + .4)/2

    blk.write([1, .4])
    (yk, ) = blk.read()
    assert np.all(yk == [1, .4])

    blk.write([1, .4], [2, 3])
    (yk, ) = blk.read()
    assert np.all(yk == [1.5, 3.4/2])

    # Weighted
    blk = system.Average(weights = np.array([1]))
    
    blk.write(1)
    (yk, ) = blk.read()
    assert yk == 1

    blk.write()
    (yk, ) = blk.read()
    assert yk == 0

    blk.set(weights = np.array([2,1]))
    
    blk.write(1, 2)
    (yk, ) = blk.read()
    assert yk == (2 + 2)/3

    blk.write(1, .4)
    (yk, ) = blk.read()
    assert yk == (2 + .4)/3

    blk.set(weights = None)

    blk.write([1, .4])
    (yk, ) = blk.read()
    assert np.all(yk == [1, .4])

    blk.set(weights = np.array([1, 2]))
    
    blk.write([1, .4], [2, 3])
    (yk, ) = blk.read()
    assert np.all(yk == [(1+2*2)/3, (.4+2*3)/3])
    
def test_Subtract():
    
    # Subtract
    blk = system.Subtract()
    
    blk.write(1,2)
    (yk, ) = blk.read()
    assert yk == 1

    blk.write(2,1)
    (yk, ) = blk.read()
    assert yk == -1

    blk.write(0,0)
    (yk, ) = blk.read()
    assert yk == 0

    blk.write(2,1,1)
    (yk, ) = blk.read()
    assert yk == 0

    blk.write(2)
    (yk, ) = blk.read()
    assert yk == -2

    blk.write()
    (yk, ) = blk.read()
    assert yk == 0
    
def test_TimeVaryingSystem():

    with pytest.raises(block.BlockException):
        blk = system.TimeVaryingSystem(modelo = 1)

    with pytest.raises(block.BlockException):
        blk = system.TimeVaryingSystem(model = 1)

    if test_ode:
        
        a = np.array([[-1, 1],[0, -2]])
        b = np.array([[1],[1]])

        def f(t, x, u, a, b):
            return a.dot(x) + b.dot(u)

        tk = 0
        xk = np.array([1,-1])
        sys = ode.ODE(shape = (1,2,2), f = f, t0 = tk, x0 = xk, pars = (a,b))

        with pytest.raises(block.BlockException):
            blk = system.TimeVaryingSystem(model = sys, mux = False)

        uk = [0]
        tk += 1
        yk1 = sys.update(tk, uk)
        #print(yk1)

        uk = [0]
        tk += 10
        yk2 = sys.update(tk, uk)
        #print(yk2)

        uk = [1]
        tk += 3
        yk3 = sys.update(tk, uk)
        #print(yk3)

        # Repeat with TimeVaryingSystem block

        tk = 0
        blk = system.TimeVaryingSystem(model = ode.ODE(shape = (1,2,2), f = f, t0 = tk, x0 = xk, pars = (a,b)))

        # u1 = 1   =>  y1 = 1

        uk = [0]
        tk += 1
        blk.write(tk, uk)
        yk = blk.read()
        assert np.all(np.abs(yk - yk1) < 1e-4)

        uk = 0
        tk += 10
        blk.write(tk, uk)
        yk = blk.read()
        assert np.all(np.abs(yk - yk2) < 1e-4)

        uk = [1]
        tk += 3
        blk.write(tk, uk)
        yk = blk.read()
        assert np.all(np.abs(yk - yk3) < 1e-4)

if __name__ == "__main__":

    test1()
    test2()
