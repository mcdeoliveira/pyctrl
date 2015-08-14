import sys
sys.path.append('..')

import pytest

import ctrl.block as block
import ctrl.block.linear as linear

def test():

    obj = block.Printer()
    obj.write([1.5, 1.3])
    obj.write((1.5, 1.3))

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

    assert blk.get() == {'endln': '\n', 'enabled': True, 'frmt': '{:12.2f}', 'sep': ' '}
    assert blk.get(['enabled', 'frmt']) == {'frmt': '{:12.2f}', 'enabled': True}
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


if __name__ == "__main__":

    test()
    test_set()
