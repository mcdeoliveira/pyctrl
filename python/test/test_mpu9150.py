import pytest

import ctrl.bbb.mpu9150 as mpu

def test1():

    (ax,ay,az,gx,gy,gz) = mpu.read()
    print("ACCEL = ({},{},{})".format(ax,ay,az))
    print("GYRO = ({},{},{})".format(gx,gy,gz))

if __name__ == "__main__":

    test1()
    test2()
