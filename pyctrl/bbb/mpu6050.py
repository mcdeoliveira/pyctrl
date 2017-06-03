import warnings
import math
import struct

import pyctrl.block as block
import pycomms.mpu6050 as mpu6050

import numpy

class Quaternion:

    def __init__(self, w = 0, x = 0, y = 0, z = 1):
        self.x = float(x);
        self.y = float(y);
        self.z = float(z);
        self.w = float(w);

    def rotation(self):

        R = numpy.array(
            [[1 - 2*(self.y * self.y + self.z * self.z),
              2*(self.x * self.y - self.z * self.w),
              2*(self.x * self.z + self.y * self.w)],
             [2*(self.x * self.y + self.z * self.w),
              1 - 2*(self.x * self.x + self.z * self.z),
              2*(self.y * self.z - self.x * self.w)],
             [2*(self.x * self.z - self.y * self.w),
              2*(self.y * self.z + self.x * self.w),
              1 - 2*(self.x * self.x + self.y * self.y)]])

        return R

    def __str__(self):
        return "x:{:+5.4f} y:{:+5.4f} z:{:+5.4f} w:{:+5.4f}".format(self.x,self.y,self.z,self.w)


class Raw(block.Block):

    def __init__(self, *vars, **kwargs):

        # Sensor initialization
        self.mpu = mpu6050.MPU6050()
        self.mpu.initialize()

        # call super
        super().__init__(*vars, **kwargs)

    def set_enabled(self, enabled = True):

        super().set_enabled(enabled)
        
    def read(self):

        #print('> read')
        if self.enabled:

            self.output = self.mpu.getMotion6()
        
        #print('< read')
        return self.output

class IMU(block.Block):

    def __init__(self, *vars, **kwargs):

        # Sensor initialization
        self.mpu = mpu6050.MPU6050()
        self.mpu.dmpInitialize()

        # get expected DMP packet size for later comparison
        self.packetSize = self.mpu.dmpGetFIFOPacketSize() 

        # call super
        super().__init__(*vars, **kwargs)

    def set_enabled(self, enabled = True):

        super().set_enabled(enabled)
        
        if enabled:
            self.mpu.setDMPEnabled(True)
            self.mpu.resetFIFO()
            warnings.warn('> imu enabled')
            print('> resetFIFO, count = {}'.format(self.mpu.getFIFOCount()))
        else:
            self.mpu.setDMPEnabled(False)
            warnings.warn('> imu disabled')

    def read(self):

        #print('> read')
        if self.enabled:

            # get current FIFO count
            fifoCount = self.mpu.getFIFOCount()
            #print('> fifoCount1 = {}'.format(fifoCount))

            if fifoCount == 1024:
                # reset so we can continue cleanly
                self.mpu.resetFIFO()
                print('FIFO overflow!')
            
            fifoCount = self.mpu.getFIFOCount()
            #print('> fifoCount2 = {}'.format(fifoCount))
            while fifoCount < self.packetSize:
                fifoCount = self.mpu.getFIFOCount()
                #print('> fifoCount3 = {}'.format(fifoCount))

            result = self.mpu.getFIFOBytes(self.packetSize)
            q = self.mpu.dmpGetQuaternion(result)

            # reset fifo every time
            self.mpu.resetFIFO()
                
            self.output = (q['w'], q['x'], q['y'], q['z'])
        
        #print('< read')
        return self.output

class Inclinometer(IMU):

    def read(self):

        # read imu
        (w, x, y, z) = super().read()

        # construct quaternion
        ez = [2*(x * z + y * w),
              2*(y * z - x * w),
              1 - 2*(x * x + y * y)]
        theta = -math.atan2(ez[2], math.sqrt(ez[0]**2+ez[1]**2)) / (2 * math.pi)
        #print('\r {} {}'.format(ez, theta), end='')
        
        # # from quaternion to vector
        # (gx, gy, gz) = (float(2 * (x * z - w * y)),
        #                 float(2 * (w * x + y * z)),
        #                 float(w * w - x * x - y * y + z * z))

        # # calculate angle
        # # TODO: FIX FRAME
        # theta = - math.atan2(gz, math.sqrt(gx**2+gy**2)) / (2 * math.pi)

        return (theta, )

class InclinometerRaw(Raw):

    def read(self):

        #print('> read')
        if self.enabled:

            self.output = (self.mpu.getRotationX() / 360, )
        
        #print('< read')
        return self.output

class InclinometerRaw2(Raw):

    def __init__(self, *vars, **kwargs):

        # turns initialization
        self.turns = 0
        self.theta = 0
        self.threshold = 0.25

        # call super
        super().__init__(*vars, **kwargs)

        # setup giro
        self.mpu.setFullScaleGyroRange(self.mpu.MPU6050_GYRO_FS_1000)

    def reset(self):

        self.turns = 0
        
    def read(self):

        #print('> read')
        if self.enabled:

            # read IMU
            ax, ay, az, gx, gy, gz = self.mpu.getMotion6()
            
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
        from pyctrl.gettime import gettime as perf_counter
    else:
        from time import perf_counter

    T = 0.04
    K = 1000

    # print("> Testing Raw")
    
    # accel = Raw()

    # k = 0
    # while k < K:

    #     # read accelerometer
    #     (ax, ay, az, gx, gy, gz) = accel.read()

    #     print('\r> (ax, ay, az, gx, gy, gz) = ({:+5.3f}, {:+5.3f}, {:+5.3f}, {:+5.3f}, {:+5.3f}, {:+5.3f})'.format(ax, ay, az, gx, gy, gz), end='')

    #     time.sleep(T)
    #     k += 1

    # print("> Testing accelerometer")
    
    # accel = IMU()

    # k = 0
    # while k < K:

    #     # read accelerometer
    #     (w, x, y, z) = accel.read()

    #     print('\r> (w, x, y, z) = ({:+5.3f}, {:+5.3f}, {:+5.3f}, {:+5.3f})g'.format(w, x, y, z), end='')

    #     time.sleep(T)
    #     k += 1

    # print("\n> Testing inclinometer raw")
    
    # giro = InclinometerRaw()
    # print("\n> ")
    # giro.set_enabled(enabled = True)

    # k = 0
    # while True:

    #     # read inclinometer
    #     (theta, ) = giro.read()
    #     print('\r> theta dot = {:+05.3f} 1/s'.format(theta), end='')
        
    #     #time.sleep(T)
    #     k += 1

    print("\n> Testing inclinometer raw 2")
    
    giro = InclinometerRaw2()
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
