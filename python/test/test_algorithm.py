import sys
sys.path.append('..')

import pytest

import numpy
import math
import ctrl.algo as algo

def test0():
    
    alg = algo.Algorithm()
    with pytest.raises(NameError):
        alg.update(1,2,3)

    alg = algo.OpenLoop()
    assert alg.update(1,2,3) == 2

def testP():

    alg = algo.Proportional(3)
    assert alg.update(1,2,3) == 3 * (2 - 1)

    alg = algo.Proportional(3, 4)
    assert alg.update(1,2,3) == 3 * (4/100 * 2 - 1)

def testPID():

    # PID = P
    alg = algo.PID(3, 0)
    assert alg.update(1,2,3) == 3 * (2 - 1)
    assert alg.update(1,2,3) == 3 * (2 - 1)

    # PID = PI
    ierror = 0
    error = 0
    alg = algo.PID(3, 4)
    err = 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(5,7,6) == 3 * err + 4 * ierror
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    err = -1 - 2
    ierror += 4. * (err + error) / 2
    assert alg.update(2,-1,4) == 3 * err + 4 * ierror
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    # PID = PI + gain
    ierror = 0
    error = 0
    alg = algo.PID(3, 4, 0, -2)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(5,7,6) == 3 * err + 4 * ierror
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    err = -2/100*(-1) - 2
    ierror += 4. * (err + error) / 2
    assert alg.update(2,-1,4) == 3 * err + 4 * ierror
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    # PID = PID
    ierror = 0
    error = 0
    alg = algo.PID(3, 4, .5)
    err = 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(5,7,6) == 3 * err + 4 * ierror + .5 * (err - error) / 6
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    err = -1 - 2
    ierror += 4. * (err + error) / 2
    assert alg.update(2,-1,4) == 3 * err + 4 * ierror + .5 * (err - error) / 4
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    # PID = PID + gain
    ierror = 0
    error = 0
    alg = algo.PID(3, 4, .5, -2)
    err = -2/100 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(5,7,6) == 3 * err + 4 * ierror + .5 * (err - error) / 6
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    err = -2/100*(-1) - 2
    ierror += 4. * (err + error) / 2
    assert alg.update(2,-1,4) == 3 * err + 4 * ierror + .5 * (err - error) / 4
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

def testV():

    alg0 = algo.Proportional(3)
    alg = algo.VelocityController(alg0)
    meas = 0
    vel = 1.*(1 - meas) / 3
    assert alg.measurement == meas
    assert alg.update(1,2,3) == 3 * (2 - vel)
    meas = 1
    assert alg.measurement == meas
    vel = 1.*(4 - meas) / 3
    assert alg.measurement == meas
    assert alg.update(4,7,3) == 3 * (7 - vel)

    alg0 = algo.Proportional(3, 4)
    alg = algo.VelocityController(alg0)
    meas = 0
    vel = 1.*(1 - meas) / 3
    assert alg.measurement == meas
    assert alg.update(1,2,3) == 3 * (4/100 * 2 - vel)
    meas = 1
    assert alg.measurement == meas
    vel = 1.*(4 - meas) / 3
    assert alg.measurement == meas
    assert alg.update(4,7,3) == 3 * (4/100 * 7 - vel)

def testLTI():

    # P
    alg = algo.LTI(numpy.array([3]), numpy.array([1]))
    assert alg.update(1,2,3) == 3 * (2 - 1)
    assert alg.update(1,2,3) == 3 * (2 - 1)

    # PID = PI
    Kp = 3
    Ki = 4
    T = 6.
    alg = algo.LTI(numpy.array([Kp+Ki*T/2, Ki*T/2-Kp]), 
                   numpy.array([1, -1]))

    # PID = PI
    ierror = 0
    error = 0
    err = 7 - 5
    ierror += T * (err + error) / 2
    assert alg.update(5,7,T) == Kp * err + Ki * ierror
    error = err

    err = -1 - 2
    ierror += T * (err + error) / 2
    assert alg.update(2,-1,T) == Kp * err + Ki * ierror
    error = err


    # PID = PI + gain
    alg = algo.LTI(numpy.array([Kp+Ki*T/2, Ki*T/2-Kp]), 
                   numpy.array([1, -1]), None, -2)

    ierror = 0
    error = 0
    err = -2/100 * 7 - 5
    ierror += T * (err + error) / 2
    assert alg.update(5,7,T) == Kp * err + Ki * ierror
    error = err

    err = -2/100*(-1) - 2
    ierror += T * (err + error) / 2
    assert abs(alg.update(2,-1,T) - (Kp * err + Ki * ierror)) < 1e-6
    error = err

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
