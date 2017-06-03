import pytest

import numpy as np
import pyctrl.block as block
import pyctrl.block.logic as logic

def testCompare():

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

    blk = logic.Compare()

    blk.set(threshold = 1)
    
    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 0
    
    with pytest.raises(block.BlockException):
        logic.Compare(m = 1.2)
        
    with pytest.raises(block.BlockException):
        logic.Compare(threshold = 'as')

    with pytest.raises(block.BlockException):
        blk.set(m = 1.2)
        
    with pytest.raises(block.BlockException):
        blk.set(threshold = 'as')
        
def testCompareAbs():

    blk = logic.CompareAbs(threshold = 1)

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 1

    blk = logic.CompareAbs(threshold = 1, invert = True)

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 0

    blk = logic.CompareAbs(threshold = 0, invert = False)

    blk.set(threshold = 1)
    blk.set(invert = True)

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 0
    
    with pytest.raises(block.BlockException):
        logic.CompareAbs(threshold = 'as')

    with pytest.raises(block.BlockException):
        blk.set(threshold = 'as')
    
def testTrigger():

    import math
    
    blk = logic.Trigger(function = lambda x: x >= 0)

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
    
    blk.write(-1)
    answer = blk.read()
    assert answer == ()

    blk.write(-1,1,2,3)
    answer = blk.read()
    assert answer == (0,0,0)

    blk.write(1,1,2,3)
    answer = blk.read()
    assert answer == (1,2,3)

    blk.write(-1,1,2,3)
    answer = blk.read()
    assert answer == (1,2,3)

    blk.write(-1)
    answer = blk.read()
    assert answer == ()
    
if __name__ == "__main__":

    testCompare()
    testCompareAbs()
    testTrigger()
