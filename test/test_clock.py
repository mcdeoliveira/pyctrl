import unittest
import pyctrl.block.clock as clk
import time


class TestUnittestAssertions(unittest.TestCase):

    def _test_clock(self, clock, Ts):

        clock.set_enabled(True)

        N = 100
        for k in range(N):
            clock.read()

        average = clock.calculate_average_period()
        print('*** {}'.format(clock.get()))

        clock.set_enabled(False)
        clock.set_enabled(True)

        for k in range(N):
            clock.read()

        average = clock.calculate_average_period()
        print('*** {}'.format(clock.get()))
        self.assertTrue(abs(average - Ts) / Ts < 7e-1)

        clock.set_enabled(False)
        clock.set_enabled(True)

        for k in range(N):
            clock.read()

        average = clock.calculate_average_period()
        self.assertTrue(abs(average - Ts) / Ts < 7e-1)

        clock.set_enabled(False)

    def _test_calibrate(self, clock, Ts, eps):

        clock.set_enabled(True)

        # calibrate
        (success, period) = clock.calibrate(eps)

        self.assertTrue(success)
        self.assertTrue(abs(period - Ts) / Ts < eps)

        clock.set_enabled(False)

    def _test_reset(self, clock, Ts):

        clock.set_enabled(True)

        N = 100
        for k in range(N):
            t, = clock.read()

        self.assertTrue(t > 0.9 * N * Ts)

        clock.reset()
        (t,) = clock.read()

        self.assertTrue(t < 2 * Ts)
        self.assertTrue(clock.time - clock.time_origin < 2 * Ts)

        for k in range(N):
            t, = clock.read()

        self.assertTrue(t > 0.9 * N * Ts)

        clock.reset()
        (t,) = clock.read()

        self.assertTrue(t < 2 * Ts)
        self.assertTrue(clock.time - clock.time_origin < 2 * Ts)

        clock.set_enabled(False)

    def test_basic_alt_timer_clock(self):

        Ts = 0.01
        clock = clk.AltTimerClock(period=Ts, enabled=False)

        self.assertEqual(clock.count, 0)

        clock.set_enabled(True)
        time.sleep(1.1*Ts)
        clock.set_enabled(False)
        self.assertEqual(clock.count, 1)

        clock.set_enabled(True)
        time.sleep(10.1*Ts)
        clock.set_enabled(False)
        print(clock.count)
        self.assertEqual(clock.count, 10)

        clock.set_enabled(True)
        clock.reset()
        self.assertEqual(clock.count, 0)
        t, = clock.read()
        self.assertEqual(clock.count, 1)
        t, = clock.read()
        self.assertEqual(clock.count, 2)
        clock.set_enabled(False)

    def test_timer_clock(self):

        Ts = 0.01
        clock = clk.TimerClock(period=Ts)

        self._test_clock(clock, Ts)
        self._test_reset(clock, Ts)
        self._test_calibrate(clock, Ts, 0.01)

    def test_alt_timer_clock(self):

        Ts = 0.01
        clock = clk.AltTimerClock(period=Ts)

        self._test_clock(clock, Ts)
        self._test_reset(clock, Ts)
        self._test_calibrate(clock, Ts, 0.01)


if __name__ == '__main__':
    unittest.main()
