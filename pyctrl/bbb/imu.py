import warnings
import math
import struct

import pyctrl.block as block
import pyctrl.bbb.mpu9150 as mpu9150

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
    from time import perf_counter

    T = 0.04
    K = 1000

    print("\n> Testing Inclinometer")
    
    giro = Inclinometer()
    print("\n> ")
    giro.set_enabled(enabled = True)

    N = 100
    for k in range(N):
        
        # read inclinometer
        (theta, thetadot) = giro.read()

        time.sleep(.1)

        print('\r> theta = {:+05.3f}  theta dot = {:+05.3f} 1/s'.format(theta, thetadot), end='')
