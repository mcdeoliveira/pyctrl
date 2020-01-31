import unittest

import numpy as np
import math
import pyctrl.block.nl as nonlinear
import pyctrl.block as block

class TestUnittestAssertions(unittest.TestCase):

    def test1(self):

        # DeadZone

        blk = nonlinear.DeadZone(Y = 10, X = 10)
        self.assertEqual(blk.Y, 10)
        self.assertEqual(blk.X, 10)
        self.assertEqual(blk._pars, (1,0,1))

        blk = nonlinear.DeadZone(Y = 0, X = 0)
        self.assertEqual(blk.Y, 0)
        self.assertEqual(blk.X, 0)
        self.assertEqual(blk._pars, (1,0,1))

        blk = nonlinear.DeadZone(Y = 50, X = 0)
        self.assertEqual(blk.Y, 50)
        self.assertEqual(blk.X, 0)
        # self.assertEqual(blk._pars, (.5,50, np.nan))
        self.assertEqual(blk._pars, (.5,50, 0))

        blk = nonlinear.DeadZone(X = 50, Y = 0)
        self.assertEqual(blk.Y, 0)
        self.assertEqual(blk.X, 50)
        self.assertEqual(blk._pars, (2.0,-100,0))

        blk = nonlinear.DeadZone(X = 50)
        self.assertEqual(blk.Y, 0)
        self.assertEqual(blk.X, 50)
        self.assertEqual(blk._pars, (2.0,-100,0))

        blk = nonlinear.DeadZone(X = 1, Y = 10)
        _pars = blk._pars
        self.assertEqual(blk.Y, 10)
        self.assertEqual(blk.X, 1)

        blk.set(Y = 1)
        self.assertEqual(blk._pars, (1,0,1))

        blk.set(Y = 10)
        blk.set(X = 1)
        self.assertEqual(blk._pars, _pars)

        self.assertEqual(blk.get('Y'), 10)

        blk.set(X = 10)
        self.assertEqual(blk._pars, (1,0,1))

        blk = nonlinear.DeadZone(X = 1, Y = 10)
        blk.write(100)
        (yk,) = blk.read()
        assert math.fabs(yk - 100) < 1e-4

        blk.write(0)
        (yk,) = blk.read()
        self.assertEqual(yk, 0)

        blk.write(1)
        (yk,) = blk.read()
        self.assertEqual(yk, 10)

        blk.write(.5)
        (yk,) = blk.read()
        self.assertEqual(yk, 5)

        blk.write(1+(100-1)/2)
        (yk,) = blk.read()
        self.assertEqual(yk, 10 + 45)

    def test2(self):

        blk = block.Map(function = abs)

        blk.write(-1)
        answer = blk.read()
        self.assertEqual(answer, (1, ))

        blk.write(1)
        answer = blk.read()
        self.assertEqual(answer, (1, ))

        blk.write(0)
        answer = blk.read()
        self.assertEqual(answer, (0, ))

        blk.write(-1,1,-2,2)
        answer = blk.read()
        self.assertEqual(answer, (1,1,2,2))

    def test3(self):

        blk = nonlinear.Product()

        blk.write(1, 2)
        answer = blk.read()
        self.assertEqual(answer, (2, ))

        blk.write(2, 2)
        answer = blk.read()
        self.assertEqual(answer, (4, ))

        blk.write(2, 2, 3)
        answer = blk.read()
        self.assertEqual(answer, (4,))

        with self.assertRaises(block.BlockException):
            nonlinear.Product(m = 1.5)

        with self.assertRaises(block.BlockException):
            blk.set(m = 1.5)

        blk.set(m = 2)

        blk.write(2, -1, 2, 3)
        answer = blk.read()
        self.assertEqual(answer, (4,-3))

    def test5(self):

        blk = nonlinear.ControlledCombination()

        blk.write(0, 2, 4)
        answer = blk.read()
        self.assertEqual(answer, (2, 0))

        blk.write(1, 2, 4)
        answer = blk.read()
        self.assertEqual(answer, (0, 4))

        blk.write(.5, 2, 4)
        answer = blk.read()
        self.assertEqual(answer, (1., 2.))

        blk = nonlinear.ControlledCombination(gain = 100)

        blk.write(0, 2, 4)
        answer = blk.read()
        self.assertEqual(answer, (2, 0))

        blk.write(100, 2, 4)
        answer = blk.read()
        self.assertEqual(answer, (0, 4))

        with self.assertRaises(block.BlockException):
            nonlinear.ControlledCombination(gain = 100, m = 1.2)

        with self.assertRaises(block.BlockException):
            nonlinear.ControlledCombination(gain = 'sda', m = 1)

        with self.assertRaises(block.BlockException):
            blk.set(gain = 100, m = 1.2)

        with self.assertRaises(block.BlockException):
            blk.set(gain = 'sda', m = 1)
        
if __name__ == "__main__":
    unittest.main()
