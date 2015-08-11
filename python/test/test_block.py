import sys
sys.path.append('..')

import pytest

import ctrl.block as block
import ctrl.linear as linear

def test():

    printer = block.Printer()
    printer.write([1.5, 1.3])

if __name__ == "__main__":

    test()
