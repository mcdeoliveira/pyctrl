import sys
sys.path.append('..')

import math
import pytest

import ctrl.block as block
import ctrl.block.clock as clk

def test():

    N = 100
    Ts = 0.01

    clock = clk.TimerClock(period = Ts)
    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    assert abs(clock.get_average_period() - Ts)/Ts < 2e-1

    clock.set_enabled(False)
    clock.set_enabled(True)

    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    assert abs(clock.get_average_period() - Ts)/Ts < 2e-1

    clock.set_enabled(False)
    clock.set_enabled(True)

    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    assert abs(clock.get_average_period() - Ts)/Ts < 2e-1
    
    clock.set_enabled(False)

def test_calibrate():
    
    Ts = 0.01
    eps = 1/10

    clock = clk.TimerClock(period = Ts)

    (success, period) = clock.calibrate(eps)
    assert success 
    assert abs(period - Ts) / Ts < eps
    
    clock.set_enabled(False)
    
if __name__ == "__main__":

    test()
    test_calibrate()
