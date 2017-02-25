import pytest
import time

import sys
if sys.version_info < (3, 3):
    from ctrl.gettime import gettime as perf_counter
else:
    from time import perf_counter

import ctrl.bbb.mpu9150 as mpu

def test1():

    # reset stats
    mpu.reset_stats()

    # sleep for 10 s
    time.sleep(10)

    # get stats
    (count, avg_duty, max_duty) = mpu.get_stats()

    # read sensor
    (ax,ay,az,gx,gy,gz) = mpu.read()

    print("\ncount = {}, avg_duty = {:+06.4f}, max_duty = {:+06.4f}".format(count, avg_duty, max_duty))

    print("ax = {:+06.4f}, ay = {:+06.4f}, az = {:+06.4f}".format(ax,ay,az))
    print("gx = {:+06.4f}, gy = {:+06.4f}, gz = {:+06.4f}".format(gx,gy,gz))

    assert avg_duty < 0.01
    assert max_duty < 0.02
    assert count > 10*avg_duty

if __name__ == "__main__":

    test1()
    test2()
