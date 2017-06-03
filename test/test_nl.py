import pytest

import numpy as np
import math
import pyctrl.block.nl as nonlinear
import pyctrl.block as block

def test1():

    # DeadZone

    blk = nonlinear.DeadZone(Y = 10, X = 10)
    assert blk.Y == 10
    assert blk.X == 10
    assert blk._pars == (1,0,1)

    blk = nonlinear.DeadZone(Y = 0, X = 0)
    assert blk.Y == 0
    assert blk.X == 0
    assert blk._pars == (1,0,1)

    blk = nonlinear.DeadZone(Y = 50, X = 0)
    assert blk.Y == 50
    assert blk.X == 0
    assert blk._pars == (.5,50,np.nan)

    blk = nonlinear.DeadZone(X = 50, Y = 0)
    assert blk.Y == 0
    assert blk.X == 50
    assert blk._pars == (2.0,-100,0)

    blk = nonlinear.DeadZone(X = 50)
    assert blk.Y == 0
    assert blk.X == 50
    assert blk._pars == (2.0,-100,0)

    blk = nonlinear.DeadZone(X = 1, Y = 10)
    _pars = blk._pars
    assert blk.Y == 10
    assert blk.X == 1
    
    blk.set(Y = 1)
    assert blk._pars == (1,0,1)

    blk.set(Y = 10)
    blk.set(X = 1)
    assert blk._pars == _pars

    assert blk.get('Y') == 10

    blk.set(X = 10)
    assert blk._pars == (1,0,1)

    blk = nonlinear.DeadZone(X = 1, Y = 10)
    blk.write(100)
    (yk,) = blk.read()
    assert math.fabs(yk - 100) < 1e-4

    blk.write(0)
    (yk,) = blk.read()
    assert yk == 0

    blk.write(1)
    (yk,) = blk.read()
    assert yk == 10

    blk.write(.5)
    (yk,) = blk.read()
    assert yk == 5

    blk.write(1+(100-1)/2)
    (yk,) = blk.read()
    assert yk == 10 + 45

def test2():

    blk = block.Map(function = np.fabs)
    
    blk.write(-1)
    answer = blk.read()
    assert answer == (1, )

    blk.write(1)
    answer = blk.read()
    assert answer == (1, )

    blk.write(0)
    answer = blk.read()
    assert answer == (0, )

    blk.write(-1,1,-2,2)
    answer = blk.read()
    assert answer == (1,1,2,2)

def test3():

    blk = nonlinear.ControlledGain()
    
    blk.write(1, 2)
    answer = blk.read()
    assert answer == (2, )

    blk.write(2, 2)
    answer = blk.read()
    assert answer == (4, )

    blk.write(2, 2, 3)
    answer = blk.read()
    assert answer == (4,)

    with pytest.raises(block.BlockException):
        nonlinear.ControlledGain(m = 1.5)
        
    with pytest.raises(block.BlockException):
        blk.set(m = 1.5)
        
    blk.set(m = 2)
    
    blk.write(2, -1, 2, 3)
    answer = blk.read()
    assert answer == (4,-3)

def test5():

    blk = nonlinear.ControlledCombination()
    
    blk.write(0, 2, 4)
    answer = blk.read()
    assert answer == (2, 0)

    blk.write(1, 2, 4)
    answer = blk.read()
    assert answer == (0, 4)

    blk.write(.5, 2, 4)
    answer = blk.read()
    assert answer == (1., 2.)

    blk = nonlinear.ControlledCombination(gain = 100)

    blk.write(0, 2, 4)
    answer = blk.read()
    assert answer == (2, 0)

    blk.write(100, 2, 4)
    answer = blk.read()
    assert answer == (0, 4)

    with pytest.raises(block.BlockException):
        nonlinear.ControlledCombination(gain = 100, m = 1.2)

    with pytest.raises(block.BlockException):
        nonlinear.ControlledCombination(gain = 'sda', m = 1)
    
    with pytest.raises(block.BlockException):
        blk.set(gain = 100, m = 1.2)

    with pytest.raises(block.BlockException):
        blk.set(gain = 'sda', m = 1)
        
if __name__ == "__main__":

    test1()
    test2()
    test3()
    test4()
    test5()
