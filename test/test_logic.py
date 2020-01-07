import unittest

import pyctrl.block as block
import pyctrl.block.logic as logic


class TestUnittestAssertions(unittest.TestCase):

    def testCompare(self):
        blk = logic.Compare()

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk = logic.Compare(threshold=1)

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk = logic.Compare()

        blk.set(threshold=1)

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        with self.assertRaises(block.BlockException):
            logic.Compare(m=1.2)

        with self.assertRaises(block.BlockException):
            logic.Compare(threshold='as')

        with self.assertRaises(block.BlockException):
            blk.set(m=1.2)

        with self.assertRaises(block.BlockException):
            blk.set(threshold='as')

    def testCompareWithHysterisis(self):
        # should work like Compare

        blk = logic.CompareWithHysterisis(hysterisis=0)

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk = logic.CompareWithHysterisis(threshold=1, hysterisis=0)

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk = logic.CompareWithHysterisis(hysterisis=0)

        blk.set(threshold=1)

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        with self.assertRaises(block.BlockException):
            logic.CompareWithHysterisis(m=1.2)

        with self.assertRaises(block.BlockException):
            logic.CompareWithHysterisis(threshold='as')

        with self.assertRaises(block.BlockException):
            blk.set(m=1.2)

        with self.assertRaises(block.BlockException):
            blk.set(threshold='as')

        with self.assertRaises(block.BlockException):
            blk.set(hysterisis=-1)

        # with hysterisis

        blk = logic.CompareWithHysterisis(hysterisis=0.1)
        self.assertEqual(blk.state, (1,))

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (0,))

        blk.write(0, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (0,))

        blk.write(0, -0.2)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (1,))

        blk.write(0, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (1,))

        blk.write(0, 0.2)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (0,))

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (1,))

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (1,))

        blk = logic.CompareWithHysterisis(threshold=1, hysterisis=0)
        self.assertEqual(blk.state, (1,))

        blk.write(0, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (0,))

        blk.write(1, 0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (1,))

        blk.write(1, 1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (1,))

    def testCompareAbs(self):
        blk = logic.CompareAbs(threshold=1)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk = logic.CompareAbs(threshold=1, invert=True)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk = logic.CompareAbs(threshold=0, invert=False)

        blk.set(threshold=1)
        blk.set(invert=True)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        with self.assertRaises(block.BlockException):
            logic.CompareAbs(threshold='as')

        with self.assertRaises(block.BlockException):
            blk.set(threshold='as')

    def testCompareAbsWithHysterisis(self):
        # should work like CompareAbs

        blk = logic.CompareAbsWithHysterisis(threshold=1, hysterisis=0)
        self.assertIsNone(blk.state)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0.9)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(1.05)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(1.1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk = logic.CompareAbsWithHysterisis(threshold=1, invert=True, hysterisis=0)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0.9)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(1.05)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(1.1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk = logic.CompareAbsWithHysterisis(threshold=0, invert=False, hysterisis=0)

        blk.set(threshold=1)
        blk.set(invert=True)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)

        with self.assertRaises(block.BlockException):
            logic.CompareAbs(threshold='as')

        with self.assertRaises(block.BlockException):
            blk.set(threshold='as')

        with self.assertRaises(block.BlockException):
            blk.set(hysterisis=-1)

        # with hysterisis

        blk = logic.CompareAbsWithHysterisis(threshold=1)
        self.assertIsNone(blk.state)
        self.assertEqual(blk.hysterisis, 0.1)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(0.9)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(1.05)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(1.11)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk = logic.CompareAbsWithHysterisis(threshold=1, invert=True)
        self.assertEqual(blk.hysterisis, 0.1)

        blk.write(2)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0.9)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(0.5)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(1.05)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (0,))

        blk.write(1.1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (1,))

        # with hysterisis

        blk = logic.CompareAbsWithHysterisis(threshold=0.2,
                                             hysterisis=0.1)
        self.assertIsNone(blk.state)
        self.assertEqual(blk.threshold, 0.2)
        self.assertEqual(blk.hysterisis, 0.1)

        blk.write(-0.3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

        blk.write(-0.31)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (logic.State.LOW,))

        blk.write(-0.41)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (logic.State.LOW,))

        blk.write(-0.3)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (logic.State.LOW,))

        blk.write(-0.1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

        blk.write(-0)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

        blk.write(-0.3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

        blk.write(-0.31)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (logic.State.LOW,))

        blk.write(0)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

        blk.write(0.3)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

        blk.write(0.31)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (logic.State.LOW,))

        blk.write(0.11)
        (answer,) = blk.read()
        self.assertEqual(answer, 0)
        self.assertEqual(blk.state, (logic.State.LOW,))

        blk.write(0.1)
        (answer,) = blk.read()
        self.assertEqual(answer, 1)
        self.assertEqual(blk.state, (logic.State.HIGH,))

    def testTrigger(self):
        import math

        blk = logic.Trigger(function=lambda x: x >= 0)

        blk.write(-1, 1)
        answer = blk.read()
        self.assertEqual(answer, (0,))

        blk.write(1, 2)
        answer = blk.read()
        self.assertEqual(answer, (2,))

        blk.write(-1, 3)
        answer = blk.read()
        self.assertEqual(answer, (3,))

        blk.reset()

        blk.write(-1, 1)
        answer = blk.read()
        self.assertEqual(answer, (0,))

        blk.reset()

        blk.write(-1)
        answer = blk.read()
        self.assertEqual(answer, ())

        blk.write(-1, 1, 2, 3)
        answer = blk.read()
        self.assertEqual(answer, (0, 0, 0))

        blk.write(1, 1, 2, 3)
        answer = blk.read()
        self.assertEqual(answer, (1, 2, 3))

        blk.write(-1, 1, 2, 3)
        answer = blk.read()
        self.assertEqual(answer, (1, 2, 3))

        blk.write(-1)
        answer = blk.read()
        self.assertEqual(answer, ())

    def testEvent(self):
        class myEvent(logic.Event):

            def __init__(self, **kwargs):
                self.value = False
                super().__init__(**kwargs)

            def rise_event(self):
                self.value = True

            def fall_event(self):
                self.value = False

        blk = myEvent()

        self.assertFalse(blk.value)  
        self.assertEqual(blk.state, logic.State.LOW)
        self.assertEqual(blk.high, 0.8)
        self.assertEqual(blk.low, 0.2)

        blk.write(1)
        self.assertTrue(blk.value)  
        self.assertEqual(blk.state, logic.State.HIGH)

        blk.write(1)
        self.assertTrue(blk.value)  
        self.assertEqual(blk.state, logic.State.HIGH)

        blk.write(0)
        self.assertFalse(blk.value)  
        self.assertEqual(blk.state, logic.State.LOW)

        blk.write(0.8)
        self.assertFalse(blk.value)  
        self.assertEqual(blk.state, logic.State.LOW)

        blk.write(0.9)
        self.assertTrue(blk.value)  
        self.assertEqual(blk.state, logic.State.HIGH)

        blk.write(0.8)
        self.assertTrue(blk.value)  
        self.assertEqual(blk.state, logic.State.HIGH)

        blk.write(0.5)
        self.assertTrue(blk.value)  
        self.assertEqual(blk.state, logic.State.HIGH)

        blk.write(0.2)
        self.assertTrue(blk.value)  
        self.assertEqual(blk.state, logic.State.HIGH)

        blk.write(0.1)
        self.assertFalse(blk.value)  
        self.assertEqual(blk.state, logic.State.LOW)

    def testSetBlock(self):
        from pyctrl import Controller
        from pyctrl.block import Constant

        controller = Controller()

        controller.add_source('block',
                              Constant(),
                              ['s1'])
        self.assertTrue(controller.get_source('block', 'enabled'))

        blk = logic.SetSource(parent=controller,
                              label='block',
                              on_rise_and_fall={'enabled': False})

        self.assertTrue(blk.state is logic.State.LOW)

        blk.write(1)
        self.assertTrue(not controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        controller.set_source('block', enabled=True)
        self.assertTrue(controller.get_source('block', 'enabled'))

        blk.write(0.5)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        blk.write(0.1)
        self.assertTrue(not controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.LOW)

        controller.set_source('block', enabled=True)
        self.assertTrue(controller.get_source('block', 'enabled'))

        blk.write(0.5)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.LOW)

        blk.write(0.9)
        self.assertTrue(not controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        # OnRiseSet

        blk = logic.SetSource(parent=controller,
                              label='block',
                              on_rise={'enabled': False})

        self.assertTrue(blk.state is logic.State.LOW)

        blk.write(1)
        self.assertTrue(not controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        controller.set_source('block', enabled=True)
        self.assertTrue(controller.get_source('block', 'enabled'))

        blk.write(0.5)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        blk.write(0.1)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.LOW)

        controller.set_source('block', enabled=True)
        self.assertTrue(controller.get_source('block', 'enabled'))

        blk.write(0.5)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.LOW)

        blk.write(0.9)
        self.assertTrue(not controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        # OnFallSet

        blk = logic.SetSource(parent=controller,
                              label='block',
                              on_fall={'enabled': False})

        controller.set_source('block', enabled=True)

        self.assertTrue(blk.state is logic.State.LOW)

        blk.write(1)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        self.assertTrue(controller.get_source('block', 'enabled'))

        blk.write(0.5)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        blk.write(0.1)
        self.assertTrue(not controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.LOW)

        controller.set_source('block', enabled=True)
        self.assertTrue(controller.get_source('block', 'enabled'))

        blk.write(0.5)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.LOW)

        blk.write(0.9)
        self.assertTrue(controller.get_source('block', 'enabled'))
        self.assertTrue(blk.state is logic.State.HIGH)

        # try pickling
        import pickle

        pickle.dumps(blk)


if __name__ == "__main__":
    unittest.main()
