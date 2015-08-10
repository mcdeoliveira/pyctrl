import sys
sys.path.append('..')

import math
import pytest

import ctrl.block as block
import ctrl.clock as clk

def test():

    N = 100
    Ts = 0.01

    clock = clk.Clock(period = Ts)
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

if __name__ == "__main__":

    test()
