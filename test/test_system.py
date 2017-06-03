import pytest

import math
import numpy as np
import pyctrl.block as block
import pyctrl.system as system
import pyctrl.system.tf as tf
import pyctrl.system.ss as ss

test_ode = True
try:
    import pyctrl.system.ode as ode
except:
    test_ode = False

def test1():

    num = np.array([1, 1])
    den = np.array([1, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == num)
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(1))
    assert sys.state.size == 1

    num = np.array([1, 1])
    den = np.array([2, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == num/2)
    assert np.all(sys.den == den/2)
    assert np.all(sys.state == np.zeros(1))
    assert sys.state.size == 1

    # different size num < den

    # G(z) = 2 z / (z - 1) = 2/(1 - q)
    num = np.array([2])
    den = np.array([1, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == np.array([2, 0]))
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(1))
    assert sys.state.size == 1

    # different size num > den
    num = np.array([1, 1, 3])
    den = np.array([1, -1])
    sys = tf.DTTF(num, den)
    assert np.all(sys.num == num)
    den = np.array([1, -1, 0])
    assert np.all(sys.den == den)
    assert np.all(sys.state == np.zeros(2))
    assert sys.state.size == 2

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
    alg = tf.PID(3, 4, period = 6)
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
    alg = tf.PID(3, 4, 0, period = 6)
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
    alg = tf.PID(3, 4, .5, period = 6)
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
    alg = tf.PID(3, 4, .5, period = 6)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert (alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 6)) < 1e-6
    error = err

    err = -2/100*(-1) - 2
    ierror += 6. * (err + error) / 2
    assert (alg.update(err) - (3 * err + 4 * ierror + .5 * (err - error) / 4)) < 1e-6
    error = err

def test3():

    # different size num < den

    # G(z) = 2 / (z - 1) = 2 q /(1 - q)
    num1 = np.array([2])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([0, 2])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)
    assert sys.state.size == 1

    # inproper
    # G(z) = z^2 / (z - 1) = 1 /(q - q^2)
    num1 = np.array([0, 0, 1])
    den1 = np.array([-1, 1])
    with pytest.raises(system.SystemException):
        sys = tf.zDTTF(num1, den1)

    # G(z) = z^2 / (z - 1) = 1 /(q - q^2)
    num1 = np.array([0, 0, 1])
    den1 = np.array([-1, 1, 0])
    with pytest.raises(system.SystemException):
        sys = tf.zDTTF(num1, den1)

    # G(z) = (z + 2)/(z - 1) = (1 + 2 q) / (1 - q)
    num1 = np.array([2, 1])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([1, 2])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)
    assert sys.state.size == 1

    # G(z) = (z + 2)/(z - 1) = (z - 1 + 3)/(z-1) = 1 + 3/(z-1)
    sysss = sys.as_DTSS()
    A = np.array([1])
    B = np.array([1])
    C = np.array([3])
    D = np.array([1])
    assert np.all(A == sysss.A)
    assert np.all(B == sysss.B)
    assert np.all(C == sysss.C)
    assert np.all(D == sysss.D)

    y1 = sys.update(1)
    y2 = sysss.update(1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(-1)
    y2 = sysss.update(-1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(3)
    y2 = sysss.update(3)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(0)
    y2 = sysss.update(0)
    assert y1 == y2
    #print(y1, y2)

    # G(z) = z/(z - 1) = 1 / (1 - q)
    num1 = np.array([0, 1])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([1, 0])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    # G(z) = z/(z - 1) = (z - 1 + 1)/(z-1) = 1 + 1/(z-1)
    sysss = sys.as_DTSS()
    A = np.array([1])
    B = np.array([1])
    C = np.array([1])
    D = np.array([1])
    assert np.all(A == sysss.A)
    assert np.all(B == sysss.B)
    assert np.all(C == sysss.C)
    assert np.all(D == sysss.D)

    y1 = sys.update(1)
    y2 = sysss.update(1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(-1)
    y2 = sysss.update(-1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(3)
    y2 = sysss.update(3)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(0)
    y2 = sysss.update(0)
    assert y1 == y2
    #print(y1, y2)

    # G(z) = 2/(z - 1)
    num1 = np.array([2, 0])
    den1 = np.array([-1, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([0, 2])
    den2 = np.array([1, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    sysss = sys.as_DTSS()
    A = np.array([1])
    B = np.array([1])
    C = np.array([2])
    D = np.array([0])
    assert np.all(A == sysss.A)
    assert np.all(B == sysss.B)
    assert np.all(C == sysss.C)
    assert np.all(D == sysss.D)
    #print(sysss.A, sysss.B, sysss.C, sysss.D)

    y1 = sys.update(1)
    y2 = sysss.update(1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(-1)
    y2 = sysss.update(-1)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(3)
    y2 = sysss.update(3)
    assert y1 == y2
    #print(y1, y2)

    y1 = sys.update(0)
    y2 = sysss.update(0)
    assert y1 == y2
    #print(y1, y2)

    # G(z) = z^2/(z - 1) = 1 / (1 - q)
    num1 = np.array([1, 0, 0])
    den1 = np.array([-1, 1])
    with pytest.raises(system.SystemException):
        sys = tf.zDTTF(num1, den1)

    # G(z) = (z + 3)/(z^2 + 2 z - 1) = (q + 3 q^2)/(1 + 2 q - q^2)
    num1 = np.array([3, 1, 0])
    den1 = np.array([-1, 2, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([0, 1, 3])
    den2 = np.array([1, 2, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    sysss = sys.as_DTSS()
    A = np.array([[0,1],[1,-2]])
    B = np.array([[0],[1]])
    C = np.array([[3,1]])
    D = np.array([[0]])
    assert np.all(A == sysss.A)
    assert np.all(B == sysss.B)
    assert np.all(C == sysss.C)
    assert np.all(D == sysss.D)
    #print('A =\n{}\nB =\n{}\nC =\n{}\nD =\n{}'.format(sysss.A, sysss.B, sysss.C, sysss.D))

    # yk = -2 yk-1 + yk-2 + uk-1 + 3 uk-2
    # u1 = 1   =>  y1 = 0
    # u1 = 1   =>  y1 = [3 1] [0; 0] = 0
    #              x2 = [0 1; 1 -2] [0; 0] + [0; 1] 1 = [0; 1]

    y1 = sys.update(1)
    y2 = sysss.update(np.array([1]))
    #print(y1, y2)
    assert y1 == 0 
    assert np.all(sysss.state == np.array([0,1]))
    assert y1 == y2

    # u2 = -1  =>  y2 = -2 y1 + u1 = 1
    # u2 = -1  =>  y2 = [3 1] [0; 1] = 1
    #              x3 = [0 1; 1 -2] [0; 1] + [0; 1] -1 
    #                 = [1; -2] + [0; -1] = [1; -3]

    y1 = sys.update(-1)
    y2 = sysss.update(np.array([-1]))
    #print(y1, y2)
    assert y1 == 1 
    assert np.all(sysss.state == np.array([1,-3]))
    assert y1 == y2

    # u3 = 3   =>  y3 = -2 y2 + y1 + u2 + 3 u1 = -2 + 0 + -1 + 3 = 0
    # u3 = 3   =>  y3 = [3 1] [1; -3] = 0
    #              x4 = [0 1; 1 -2] [1; -3] + [0; 1] 3 
    #                 = [-3; 7] + [0; 3] = [-3; 10]

    y1 = sys.update(3)
    y2 = sysss.update(np.array([3]))
    #print(y1, y2)
    assert y1 == 0 
    assert np.all(sysss.state == np.array([-3,10]))
    assert y1 == y2

    # u4 = 0   =>  y4 = -2 y3 + y2 + u3 + 3 u2 = 0 + 1 + 3 - 3 = 1
    # u4 = 0   =>  y4 = [3 1] [-3; 10] = 1
    #              x5 = [0 1; 1 -2] [-3; 10] + [0; 1] 0 
    #                 = [10; -23]

    y1 = sys.update(0)
    y2 = sysss.update(np.array([0]))
    #print(y1, y2)
    assert y1 == 1
    assert np.all(sysss.state == np.array([10,-23]))
    assert y1 == y2

    # G(z) = z^2/(z^2 + 2 z - 1) = 1 + (1 - 2 z)/(z^2 + 2 z - 1)
    num1 = np.array([0, 0, 1])
    den1 = np.array([-1, 2, 1])
    sys = tf.zDTTF(num1, den1)
    num2 = np.array([1, 0, 0])
    den2 = np.array([1, 2, -1])
    assert np.all(sys.num == num2)
    assert np.all(sys.den == den2)

    sysss = sys.as_DTSS()
    A = np.array([[0,1],[1, -2]])
    B = np.array([[0],[1]])
    C = np.array([[1,-2]])
    D = np.array([[1]])
    assert np.all(A == sysss.A)
    assert np.all(B == sysss.B)
    assert np.all(C == sysss.C)
    assert np.all(D == sysss.D)
    #print('A =\n{}\nB =\n{}\nC =\n{}\nD =\n{}'.format(sysss.A, sysss.B, sysss.C, sysss.D))

    # yk = -2 yk-1 + yk-2 + uk
    # u1 = 1   =>  y1 = 1
    # u1 = 1   =>  y1 = [1 -2] [0; 0] + [1] 1 = 1
    #              x2 = [0 1; 1 -2] [0; 0] + [0; 1] 1 = [0; 1]

    y1 = sys.update(1)
    y2 = sysss.update(np.array([1]))
    #print(y1, y2)
    assert y1 == 1 
    assert np.all(sysss.state == np.array([0,1]))
    assert y1 == y2

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3
    # u2 = -1  =>  y2 = [1 -2] [0; 1] + [1] -1 = -2 -1 = -3
    #              x3 = [0 1; 1 -2] [0; 1] + [0; 1] -1 
    #                 = [1; -2] + [0; -1] = [1; -3]

    y1 = sys.update(-1)
    y2 = sysss.update(np.array([-1]))
    #print(y1, y2)
    assert y1 == -3 
    assert np.all(sysss.state == np.array([1,-3]))
    assert y1 == y2

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10
    # u3 = 3   =>  y3 = [1 -2] [1; -3] + [1] 3 = 1 + 6 + 3 = 10
    #              x4 = [0 1; 1 -2] [1; -3] + [0; 1] 3 
    #                 = [-3; 7] + [0; 3] = [-3; 10]

    y1 = sys.update(3)
    y2 = sysss.update([3])
    #print(y1, y2)
    assert y1 == 10 
    assert np.all(sysss.state == np.array([-3,10]))
    assert y1 == y2

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23
    # u4 = 0   =>  y4 = [1 -2] [-3; 10] + [1] 0 = -3 -20 = -23
    #              x5 = [0 1; 1 -2] [-3; 10] + [0; 1] 0 
    #                 = [10; -23]

    y1 = sys.update(0)
    y2 = sysss.update([0])
    #print(y1, y2)
    assert y1 == -23
    assert np.all(sysss.state == np.array([10,-23]))
    assert y1 == y2

    # vector input/output

    sysss = sys.as_DTSS()
    A = np.array([[0,1],[1, -2]])
    B = np.array([[0],[1]])
    C = np.array([[1,-2]])
    D = np.array([[1]])
    assert np.all(A == sysss.A)
    assert np.all(B == sysss.B)
    assert np.all(C == sysss.C)
    assert np.all(D == sysss.D)
    #print('A =\n{}\nB =\n{}\nC =\n{}\nD =\n{}'.format(sysss.A, sysss.B, sysss.C, sysss.D))

    # u1 = 1   =>  y1 = 1

    y2 = sysss.update(np.array([1]))
    assert isinstance(y2, np.ndarray) and y2 == 1 

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3

    y2 = sysss.update([-1])
    assert isinstance(y2, np.ndarray) and y2 == -3 

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10

    y2 = sysss.update(np.array([3]))
    assert isinstance(y2, np.ndarray) and y2 == 10 

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23

    y2 = sysss.update([0])
    assert isinstance(y2, np.ndarray) and y2 == -23

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

    # u1 = 1   =>  y1 = 1

    y2 = sys.update(np.array([1]))
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([1,0]))

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3

    y2 = sys.update([-1])
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([-3,1]))

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10

    y2 = sys.update(np.array([3]))
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([10,-3]))

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23

    y2 = sys.update([0])
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([-23,10]))

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

    # u1 = 1   =>  y1 = 1

    y2 = sys.update(np.array([1,1]))
    assert np.all(sys.state == np.array([0,1]))
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([1,0]))

    # u2 = -1  =>  y2 = -2 y1 + u2 = -2 - 1 = -3

    y2 = sys.update(np.array([-1,0]))
    assert np.all(sys.state == np.array([0,-3]))
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([-3,2]))

    # u3 = 3   =>  y3 = -2 y2 + y1 + u3 = 6 + 1 + 3 = 10

    y2 = sys.update(np.array([3,-1]))
    assert np.all(sys.state == np.array([1,9]))
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([9,-7]))

    # u4 = 0   =>  y4 = -2 y3 + y2 + u4 = - 20 - 3 + 0 = -23

    y2 = sys.update(np.array([2,1]))
    assert np.all(sys.state == np.array([10,-15]))
    assert isinstance(y2, np.ndarray) and np.all(y2 == np.array([-15,8]))

def dotest4(oode):

    # \dot{x} = 1

    def f(t, x, *pars):
        return np.array([1])
    
    sys = oode((0,1,1), f, t0 = 0)

    yk = sys.update(1, 0)
    #print(yk)
    assert np.abs(yk - np.array([1.])) < 1e-4

    yk = sys.update(2, 0)
    assert np.abs(yk - np.array([2.])) < 1e-4

    sys = oode((0,1,1), f, t0 = 0)

    yk = sys.update(.1, 0)
    assert np.abs(yk - np.array([.1])) < 1e-4
    
    yk = sys.update(.2, 0)
    assert np.abs(yk - np.array([.2])) < 1e-4

    sys = oode((0,1,1), f, t0 = 0, pars = (3,))

    yk = sys.update(1, -1)
    assert np.abs(yk - np.array([1.])) < 1e-4

    # \dot{x} = u
    def f(t, x, u, *pars):
        #print('t = {}, x = {}, u = {}, pars = {}'.format(t, x, u, pars))
        return u
    
    tk = 0
    sys = oode((0,1,1), f, t0 = tk)

    tk += 1
    yk = sys.update(tk, 0)
    assert np.abs(yk - np.array([0.])) < 1e-4

    tk += 1
    yk = sys.update(tk, 1)
    assert np.abs(yk - np.array([1.])) < 1e-4

    tk = 0
    sys = oode((0,1,1), f, t0 = tk)

    tk += .1
    yk = sys.update(tk, 2)
    assert np.abs(yk - np.array([.2])) < 1e-4

    tk += .1
    yk = sys.update(tk, -2)
    assert np.abs(yk - np.array([0])) < 1e-4

    # \dot{x} = -a * x + a * u
    def F(t, x, u, a):
        #print('t = {}, x = {}, u = {}, a = {}'.format(t, x, u, a))
        return -a * x + a * u

    a = 2
    x0 = -1.5
    tk = 0
    sys = oode((1,1,1), f = F, t0 = tk, x0 = x0, pars = (a,))

    tk += 1
    yk = sys.update(tk, 0)
    #print(yk, np.array([x0 * math.exp(-a*tk)]))
    assert np.abs(yk - np.array([x0 * math.exp(-a*tk)])) < 1e-4

    x0 = -1.5
    tk = 0
    sys = oode((1,1,1), f = F, t0 = tk, x0 = x0, pars = (a,))

    uk = 3
    tk += 2
    yk = sys.update(tk, uk)
    yyk = uk * (1 - math.exp(-a*tk)) + x0 * math.exp(-a*tk)
    assert np.abs(yk - np.array([yyk])) < 1e-4

def test4():

    if test_ode:
        dotest4(ode.ODE)
        
def test5():

    if test_ode:
        dotest4(ode.ODEINT)
    
def test6():

    if not test_ode:
        return
    
    a = np.array([[-1, 0],[0, -2]])
    b = np.array([[1],[1]])

    def f(t, x, u, a, b):
        return a.dot(x) + b.dot(u)
    
    tk = 0
    xk = np.array([1,-1])
    sys = ode.ODE((2,2,2), f = f, t0 = tk, x0 = xk, pars = (a,b))

    uk = [0]
    tk += 1
    yyk = [-(b[0,0]/a[0,0])*uk[0] * (1 - math.exp(a[0,0]*tk)) + xk[0] * math.exp(a[0,0]*tk),
           -(b[1,0]/a[1,1])*uk[0] * (1 - math.exp(a[1,1]*tk)) + xk[1] * math.exp(a[1,1]*tk)]
    yk = sys.update(tk, uk)
    assert np.all(np.abs(yk - yyk) < 1e-4)

    tk = 0
    xk = np.array([1,-1])
    sys = ode.ODE((2,2,2), f = f, t0 = tk, x0 = xk, pars = (a,b))

    uk = [2]
    tk += 1
    yyk = [-(b[0,0]/a[0,0])*uk[0] * (1 - math.exp(a[0,0]*tk)) + xk[0] * math.exp(a[0,0]*tk),
           -(b[1,0]/a[1,1])*uk[0] * (1 - math.exp(a[1,1]*tk)) + xk[1] * math.exp(a[1,1]*tk)]
    yk = sys.update(tk, uk)
    assert np.all(np.abs(yk - yyk) < 1e-4)

    import scipy.integrate

    P = 0       # birth rate
    d = 0.0001  # natural death percent (per day)
    B = 0.0095  # transmission percent  (per day)
    G = 0.0001  # resurect percent (per day)
    A = 0.0001  # destroy percent  (per day)
    
    # solve the system dy/dt = f(y, t)
    def f(y, t):
        # the model equations (see Munz et al. 2009)
        Si, Zi, Ri = y
        return (P - B*Si*Zi - d*Si, 
                B*Si*Zi + G*Ri - A*Si*Zi,
                d*Si + A*Si*Zi - G*Ri)
   
    # initial conditions
    S0 = 500.               # initial population
    Z0 = 0                  # initial zombie population
    R0 = 0                  # initial death population
    y0 = [S0, Z0, R0]       # initial condition vector
    T = 2
    t  = np.linspace(0, T, 2)   # time grid

    # solve the DEs
    soln = scipy.integrate.odeint(f, y0, t)

    # solve the system dy/dt = f(y, t)
    def ff(t, x, u, *pars):
        # the model equations (see Munz et al. 2009)
        #print('t = {}, x = {}, u = {}'.format(t, x, u))
        return list(f(x, t))

    tk = 0
    sys = ode.ODEINT((1,3,3), f = ff, t0 = tk, x0 = y0)

    uk = [0]
    tk += T
    yk = sys.update(tk, uk)
    #print(yk)
    #print(soln[1])
    assert np.all(np.abs(yk - soln[1]) < 1e-4)


if __name__ == "__main__":

    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
