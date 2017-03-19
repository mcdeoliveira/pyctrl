import pytest

import time, math

try:
    
    import rc
    rc.set_state(rc.RUNNING)

    import ctrl.rc.clock as clk

    def run_clock(Ts):

        clock = clk.Clock()
        clock.set_period(Ts)

        print("\n> Testing Clock @{} Hz".format(1/Ts))

        N = int(5/Ts)
        (t0,) = clock.read()
        avg = 0
        mx = 0
        for k in range(1,N):

            (t1,) = clock.read()
            dt = 1000 * (t1 - t0)
            t0 = t1
            avg = ((k-1)/k) * avg + (1/k) * dt
            mx = max(dt, mx)
            print('\r dt = {:7.3f} ms  average = {:7.3f} ms   max = {:7.3f} ms'.format(dt, avg, mx), end='')

        assert avg < Ts*1000
        assert mx < 2*Ts*1000

    def test_clock():

        run_clock(0.01)
        run_clock(0.25)

except:

    print('rc library not installed, skipping test...')
    
    def test():
        pass
        
