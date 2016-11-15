import pytest

import numpy as np
import ctrl.block.nl as nonlinear
import ctrl.block as block

def test1():

    # DeadZone

    blk = nonlinear.DeadZone(10, 10)
    assert blk.Y == 10
    assert blk.X == 10
    assert blk._pars == (1,0,1)

    blk = nonlinear.DeadZone(0, 0)
    assert blk.Y == 0
    assert blk.X == 0
    assert blk._pars == (1,0,1)

    blk = nonlinear.DeadZone(0, 50)
    assert blk.Y == 50
    assert blk.X == 0
    assert blk._pars == (.5,50,np.nan)

    blk = nonlinear.DeadZone(50, 0)
    assert blk.Y == 0
    assert blk.X == 50
    assert blk._pars == (2.0,-100,0)

    blk = nonlinear.DeadZone(50)
    assert blk.Y == 0
    assert blk.X == 50
    assert blk._pars == (2.0,-100,0)

    blk = nonlinear.DeadZone(1, 10)
    _pars = blk._pars
    assert blk.Y == 10
    assert blk.X == 1
    
    blk.set('Y', 1)
    assert blk._pars == (1,0,1)

    blk.set('Y', 10)
    blk.set('X', 1)
    assert blk._pars == _pars

    assert blk.get('Y') == 10

    blk.set('X', 10)
    assert blk._pars == (1,0,1)

    blk = nonlinear.DeadZone(1, 10)
    blk.write(100)
    (yk,) = blk.read()
    assert yk == 100

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

    blk = nonlinear.Abs()
    
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
    
if __name__ == "__main__":

    test1()
    test2()
