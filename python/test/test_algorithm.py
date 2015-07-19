import sys
sys.path.append('..')

import pytest

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
    assert alg.update(1,2,3) == 3 * (4 * 2 - 1)

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
    err = -2 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(5,7,6) == 3 * err + 4 * ierror
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    err = -2*(-1) - 2
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
    err = -2 * 7 - 5
    ierror += 6. * (err + error) / 2
    assert alg.update(5,7,6) == 3 * err + 4 * ierror + .5 * (err - error) / 6
    error = err
    assert alg.error == error
    assert alg.ierror == ierror

    err = -2*(-1) - 2
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
    assert alg.update(1,2,3) == 3 * (4 * 2 - vel)
    meas = 1
    assert alg.measurement == meas
    vel = 1.*(4 - meas) / 3
    assert alg.measurement == meas
    assert alg.update(4,7,3) == 3 * (4 * 7 - vel)
