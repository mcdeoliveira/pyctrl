import unittest
from threading import Thread
import pyctrl.util.clock as clock
import time


class TestUnittestAssertions(unittest.TestCase):

    def test_util_clock(self):

        class Test:

            def __init__(self):
                self.count = 0

            def increment(self, inc=1):
                self.count += inc

        Ts = 0.1

        test = Test()
        clk = clock.Clock(interval=Ts, function=test.increment)

        clk.start()

        time.sleep(1.1)
        self.assertEqual(test.count, 10)

        clk.cancel()
        clk.join()

        test = Test()
        clk = clock.Clock(interval=Ts, function=test.increment, args=(2,))

        clk.start()

        time.sleep(1.1)
        self.assertEqual(test.count, 20)

        clk.cancel()
        clk.join()

        test = Test()
        clk = clock.Clock(interval=Ts, function=test.increment, kwargs={'inc': 3})

        clk.start()

        time.sleep(1.1)
        self.assertEqual(test.count, 30)

        clk.cancel()
        clk.join()

    def test_clock_join(self):

        class MyThread(Thread):

            def __init__(self, clock, test, maxiters, sleep_time):
                self.clock = clock
                self.test = test
                self.maxiters = maxiters
                self.sleep_time = sleep_time

            def run(self):
                while self.test.count < self.maxiters:
                    time.sleep(self.sleep_time)
                self.clock.cancel()

        class Test:

            def __init__(self):
                self.count = 0

            def increment(self, inc=1):
                self.count += inc

        Ts = 0.1

        test = Test()
        clk = clock.Clock(interval=Ts, function=test.increment)

        thread = MyThread(clk, test, 10, Ts)

        clk.start()
        thread.start()

        time.sleep(Ts)

        clk.join()

        self.assertTrue(test.count >= 10)


if __name__ == '__main__':
    unittest.main()
