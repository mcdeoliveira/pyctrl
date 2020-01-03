import unittest
import pyctrl.block.clock as clk


class TestUnittestAssertions(unittest.TestCase):

    def test_clock(self):

        N = 100
        Ts = 0.01

        clock = clk.TimerClock(period = Ts)
        k = 0
        while k < N:
            (t,) = clock.read()
            k += 1

        average = clock.calculate_average_period()
        print('*** {}'.format(clock.get()))

        clock.set_enabled(False)
        clock.set_enabled(True)

        k = 0
        while k < N:
            (t,) = clock.read()
            k += 1

        average = clock.calculate_average_period()
        print('*** {}'.format(clock.get()))
        self.assertTrue( abs(average - Ts)/Ts < 7e-1 )

        clock.set_enabled(False)
        clock.set_enabled(True)

        k = 0
        while k < N:
            (t,) = clock.read()
            k += 1

        average = clock.calculate_average_period()
        self.assertTrue( abs(average - Ts)/Ts < 7e-1 )

        clock.set_enabled(False)

    def test_calibrate(self):

        Ts = 0.01
        eps = 1/10

        clock = clk.TimerClock(period = Ts)

        (success, period) = clock.calibrate(eps)
        self.assertTrue( success )
        self.assertTrue( abs(period - Ts) / Ts < eps )

        clock.set_enabled(False)

    def test_reset(self):

        N = 10
        Ts = 0.01

        clock = clk.TimerClock(period = Ts)
        k = 0
        while k < N:
            (t,) = clock.read()
            k += 1

        self.assertTrue( t > 0.9 * N * Ts )

        clock.reset()
        (t,) = clock.read()

        self.assertTrue( t < 2*Ts )
        self.assertTrue( clock.time - clock.time_origin < 2*Ts )

        k = 0
        while k < N:
            (t,) = clock.read()
            k += 1

        self.assertTrue( t > 0.9 * N * Ts )

        clock.reset()
        (t,) = clock.read()

        self.assertTrue( t < 2*Ts )
        self.assertTrue( clock.time - clock.time_origin < 2*Ts )

        clock.set_enabled(False)


if __name__ == '__main__':
    unittest.main()
