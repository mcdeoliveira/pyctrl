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

def testCompareWithHysterisis():

    # should work like Compare
    
    blk = logic.CompareWithHysterisis(hysterisis = 0)

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 1

    blk = logic.CompareWithHysterisis(threshold = 1, hysterisis = 0)

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 0

    blk = logic.CompareWithHysterisis(hysterisis = 0)

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
        logic.CompareWithHysterisis(m = 1.2)
        
    with pytest.raises(block.BlockException):
        logic.CompareWithHysterisis(threshold = 'as')

    with pytest.raises(block.BlockException):
        blk.set(m = 1.2)
        
    with pytest.raises(block.BlockException):
        blk.set(threshold = 'as')
        
    with pytest.raises(block.BlockException):
        blk.set(hysterisis = -1)

    # with hysterisis
        
    blk = logic.CompareWithHysterisis(hysterisis = 0.1)
    assert blk.state == (1,)

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0,0)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0,-0.2)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(0,0)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(0,0.2)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)
    
    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk = logic.CompareWithHysterisis(threshold = 1, hysterisis = 0)
    assert blk.state == (1,)

    blk.write(0,1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1,0)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1,1)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

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
    
def testCompareAbsWithHysterisis():

    # should work like CompareAbs
    
    blk = logic.CompareAbsWithHysterisis(threshold = 1, hysterisis = 0)
    assert blk.state == None

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0.9)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1.05)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1.1)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)
    
    blk = logic.CompareAbsWithHysterisis(threshold = 1, invert = True, hysterisis = 0)

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0.9)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1.05)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1.1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk = logic.CompareAbsWithHysterisis(threshold = 0, invert = False, hysterisis = 0)

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
        
    with pytest.raises(block.BlockException):
        blk.set(hysterisis = -1)

    # with hysterisis
        
    blk = logic.CompareAbsWithHysterisis(threshold = 1)
    assert blk.state == None
    assert blk.hysterisis == 0.1

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(0.9)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1.05)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1.11)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)
    
    blk = logic.CompareAbsWithHysterisis(threshold = 1, invert = True)
    assert blk.hysterisis == 0.1

    blk.write(2)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(3)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0.9)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)

    blk.write(0)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(0.5)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1.05)
    (answer,) = blk.read()
    assert answer == 0
    assert blk.state == (1,)

    blk.write(1.1)
    (answer,) = blk.read()
    assert answer == 1
    assert blk.state == (0,)
        
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
    testCompareWithHysterisis()
    testCompareAbs()
    testCompareAbsWithHysterisis()
    testTrigger()
