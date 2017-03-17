import pytest
import sys

import ctrl.block as block
import ctrl.block.linear as linear

def testPrinter():

    obj = block.Printer()

    obj.write(1.5)

    obj.write([1.5, 1.3])

    obj.write((1.5, 1.3))

    obj.write(*[1.5, 1.3])

    obj.write(*(1.5, 1.3))

    assert obj.get() == { 'enabled': True, 'endln': '\n', 'frmt': '{: 12.4f}', 'sep': ' ', 'file': sys.stdout }

    assert obj.get('enabled') == True
    print("-> '{}'".format(obj.get('endln', 'frmt')))
    assert obj.get(['endln', 'frmt']) == { 'endln': '\n', 'frmt': '{: 12.4f}' }

    with pytest.raises(block.BlockException):
        obj = block.Printer("adsadsda")

    with pytest.raises(block.BlockException):
        obj = block.Printer(1, "adsadsda")

    with pytest.raises(block.BlockException):
        obj = block.Printer("adsadsda", "adsads")

    with pytest.raises(block.BlockException):
        obj = block.Printer(par = "adsadsda")

    with pytest.raises(block.BlockException):
        obj = block.Printer(par = 1)

    with pytest.raises(block.BlockException):
        obj = block.Printer(1, par = "adsadsda")

    with pytest.raises(block.BlockException):
        obj = block.Printer(1, par = "adsadsda", sadasd = 1)

    obj = block.Printer(enabled = False)

def test_set():

    blk = block.Printer()

    assert blk.get() == { 'enabled': True, 'endln': '\n', 'frmt': '{: 12.4f}', 'sep': ' ', 'file': sys.stdout }
    
    assert blk.get(['enabled', 'frmt']) == {'frmt': '{: 12.4f}', 'enabled': True}
    
    assert blk.get('enabled') == True

    with pytest.raises(KeyError):
        blk.get('*enabled')

    blk.set(enabled = False)
    assert blk.get('enabled') == False

    blk.set(enabled = True)
    assert blk.get('enabled') == True

    with pytest.raises(block.BlockException):
        blk.set(_enabled = True)
    
    blk.set(sep = '-')
    assert blk.get('sep') == '-'

    blk = block.BufferBlock()
    assert blk.get() == {'enabled': True}
    # test twice to make sure it is copying
    assert blk.get() == {'enabled': True}
    with pytest.raises(KeyError):
        blk.get('buffer')


def test_logger():

    import ctrl.block.logger as logger
    import numpy as np

    _logger = logger.Logger()

    # write one entry
    _logger.write(1,2,3)
    log = _logger.read()
    assert np.all(log == [[1,2,3]])

    # write second entry
    _logger.write(4,5,6)
    log = _logger.read()
    assert np.all(log == [[1,2,3],[4,5,6]])

    # dynamic reshaping
    _logger.write(1,2,3,5)
    log = _logger.read()
    assert np.all(log == [[1,2,3,5]])

    # vector entries
    _logger.write(1,2,[3,5])
    log = _logger.read()
    assert np.all(log == [[1,2,3,5]])

    # vector entries
    _logger.write([1,2],2,[3,5])
    log = _logger.read()
    assert np.all(log == [[1,2,2,3,5]])

    assert _logger.get() == { 'auto_reset': False, 'enabled': True, 'current': 1, 'page': 0 }

def test_signal():

    import numpy as np

    x = np.array([1,2,3])
    obj = block.Signal(signal = x, repeat = True)
    
    k = 0
    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]

    k = 0
    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]

    x = np.array([1,2,3])
    obj = block.Signal(signal = x, repeat = False)
    
    k = 0
    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]

    (y,) = obj.read(0)
    assert y == 0

    (y,) = obj.read(0)
    assert y == 0

    (y,) = obj.read(0)
    assert y == 0

    x = np.array([1,2,3])
    obj = block.Signal(signal = x, repeat = True)
    
    k = 0
    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    (y,) = obj.read(0)
    assert y == x[k]
    k += 1

    obj.reset()
    
    k = 0
    (y,) = obj.read(0)
    assert y == x[0]

def test_apply():

    def f(*x):
        return (x[0] < 1, )
    
    obj = block.Apply(function = f)
    
    obj.write(0)
    (y,) = obj.read()
    assert y == True

    obj.write(1)
    (y,) = obj.read()
    assert y == False

    def g(*x):
        return all(map(lambda y : y < 1, x))
    
    obj = block.Apply(function = g)
    
    obj.write(0)
    (y,) = obj.read()
    assert y == True

    obj.write(1)
    (y,) = obj.read()
    assert y == False

    
def test_map():

    def f(i):
        return i + 1

    obj = block.Map(function = f)
    
    obj.write(0)
    (y,) = obj.read()
    assert y == 1

    obj.write(0,2)
    y = obj.read()
    assert y == (1,3)

    obj.write()
    y = obj.read()
    assert y == ()

    
if __name__ == "__main__":

    testPrinter()
    test_set()
    test_logger()
    test_signal()
