import pytest
import math

import pyctrl.block as block
import pyctrl.block.clock as clk

def test():

    N = 100
    Ts = 0.01

    clock = clk.TimerClock(period = Ts)
    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    print('*** {}'.format(clock.get()))
        
    average = clock.calculate_average_period()

    clock.set_enabled(False)
    clock.set_enabled(True)

    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    average = clock.calculate_average_period()
    assert abs(average - Ts)/Ts < 5e-1

    clock.set_enabled(False)
    clock.set_enabled(True)

    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    average = clock.calculate_average_period()
    assert abs(average - Ts)/Ts < 3e-1
    
    clock.set_enabled(False)

def test_calibrate():
    
    Ts = 0.01
    eps = 1/10

    clock = clk.TimerClock(period = Ts)

    (success, period) = clock.calibrate(eps)
    assert success 
    assert abs(period - Ts) / Ts < eps
    
    clock.set_enabled(False)

def test_reset():

    N = 10
    Ts = 0.01
    eps = 1/10

    clock = clk.TimerClock(period = Ts)
    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    assert t > 0.9 * N * Ts

    clock.reset()
    (t,) = clock.read()

    assert t < 2*Ts
    assert clock.time - clock.time_origin < 2*Ts

    k = 0
    while k < N:
        (t,) = clock.read()
        k += 1

    assert t > 0.9 * N * Ts

    clock.reset()
    (t,) = clock.read()

    assert t < 2*Ts
    assert clock.time - clock.time_origin < 2*Ts

    clock.set_enabled(False)
    
if __name__ == "__main__":

    test()
    test_calibrate()
    test_reset()
