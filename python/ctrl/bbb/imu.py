import warnings
import math
import struct

if __name__ == "__main__":

    import sys
    sys.path.append('.')

import ctrl.block as block
import mpu9150 as mpu9150

import numpy

class Raw(block.Block):

    def read(self):

        #print('> read')
        if self.enabled:

            # read imu
            self.output = mpu9150.read()
        
        #print('< read')
        return self.output

class Inclinometer(block.Block):

    def __init__(self, *vars, **kwargs):

        # turns initialization
        self.turns = 0
        self.theta = 0
        self.threshold = 0.25

        # call super
        super().__init__(*vars, **kwargs)

    def reset(self):

        self.turns = 0
        
    def read(self):

        #print('> read')
        if self.enabled:

            # read IMU
            ax, ay, az, gx, gy, gz = mpu9150.read()

            # compensate for turns
            theta = -math.atan2(az, ay) / (2 * math.pi)
            if (theta < 0 and self.theta > 0):
                if (self.theta - theta > self.threshold):
                    self.turns += 1
            elif (theta > 0 and self.theta < 0):
                if (theta - self.theta > self.threshold):
                    self.turns -= 1
            self.theta = theta
                    
            self.output = (self.turns + theta, gx / 360)
        
        #print('< read')
        return self.output

if __name__ == "__main__":

    import time, math

    if sys.version_info < (3, 3):
        from ctrl.gettime import gettime as perf_counter
    else:
        from time import perf_counter

    T = 0.04
    K = 1000

    print("\n> Testing Inclinometer")
    
    giro = Inclinometer()
    print("\n> ")
    giro.set_enabled(enabled = True)

    N = 10
    while True:

        t0 = perf_counter()
        for k in range(N):
            # read inclinometer
            (theta, thetadot) = giro.read()
        t1 = perf_counter() - t0
        period = t1 / N

        print('\r> theta = {:+05.3f}  theta dot = {:+05.3f} 1/s  period = {:+07.5f}'.format(theta, thetadot, period), end='')
