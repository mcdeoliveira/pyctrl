import pytest

import ctrl.block as block
import ctrl.block.linear as linear

def test_printer():

    obj = block.Printer()

    obj.write(1.5)

    obj.write([1.5, 1.3])

    obj.write((1.5, 1.3))

    obj.write(*[1.5, 1.3])

    obj.write(*(1.5, 1.3))

    assert obj.get() == { 'enabled': True, 'endln': '\n', 'frmt': '{: 12.4f}', 'sep': ' ' }

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

    assert blk.get() == {'endln': '\n', 'enabled': True, 'frmt': '{: 12.4f}', 'sep': ' '}
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

    assert _logger.get() == { 'enabled': True, 'current': 1, 'page': 0 }

if __name__ == "__main__":

    test_printer()
    test_set()
    test_logger()
