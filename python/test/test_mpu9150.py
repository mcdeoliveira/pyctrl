import pytest

import sys
if sys.version_info < (3, 3):
    from ctrl.gettime import gettime as perf_counter
else:
    from time import perf_counter

import ctrl.bbb.mpu9150 as mpu

def test1():

    N = 1000
    t0 = perf_counter()
    for k in range(N):
        (ax,ay,az,gx,gy,gz) = mpu.read()
    t1 = perf_counter() - t0
    print("period = {})".format(t1 / N))

    answer = 1
    assert answer == 1

if __name__ == "__main__":

    test1()
    test2()
