import pytest

import numpy as np
import ctrl.block as block
import ctrl.block.logic as logic

def test1():

    blk = logic.Compare()

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 1

    blk = logic.Compare(threshold = 1)

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 0
    
def test2():

    blk = logic.CompareAbs(threshold = 1)

    blk.write(0,2)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(2,0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(0,0)
    (answer,) = blk.read()
    assert answer == 1
    
def test3():

    blk = logic.Trigger()

    blk.write(-1,1)
    answer = blk.read()
    assert answer == (0,)

    blk.write(1,2)
    answer = blk.read()
    assert answer == (2,)

    blk.write(-1,3)
    answer = blk.read()
    assert answer == (3,)

    blk.reset()
    
    blk.write(-1,1)
    answer = blk.read()
    assert answer == (0,)

    blk.reset()
    
    blk.write(-1,1,2,3)
    answer = blk.read()
    assert answer == (0,0,0)

    blk.write(1,1,2,3)
    answer = blk.read()
    assert answer == (1,2,3)

    blk.write(-1,1,2,3)
    answer = blk.read()
    assert answer == (1,2,3)

if __name__ == "__main__":

    test1()
    test2()
