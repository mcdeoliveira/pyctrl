import warnings
import math
import struct

if __name__ == "__main__":

    import sys
    sys.path.append('.')

import ctrl.block as block
import pycomms.mpu6050 as mpu6050

class IMU(block.Block):

    def __init__(self, *vars, **kwargs):

        # Sensor initialization
        self.mpu = mpu6050.MPU6050()
        self.mpu.dmpInitialize()
        self.mpu.setDMPEnabled(True)

        # get expected DMP packet size for later comparison
        self.packetSize = self.mpu.dmpGetFIFOPacketSize() 

        # call super
        super().__init__(*vars, **kwargs)

    def read(self):

        #print('> read')
        if self.enabled:

            q = self.mpu.dmpGetQuaternion(self.mpu.getFIFOBytes(self.packetSize))
            self.output = (q['w'], q['x'], q['y'], q['z'])
        
        return self.output

class Inclinometer(IMU):

    def read(self):

        # read imu
        (w, x, y, z) = super().read()

        # from quaternion to vector
        (gx, gy, gz) = (float(2 * (x * z - w * y)),
                        float(2 * (w * x + y * z)),
                        float(w * w - x * x - y * y + z * z))

        # calculate angle
        theta = math.atan2(gz, math.sqrt(gx**2+gy**2)) / (2 * math.pi)

        return (theta, )

if __name__ == "__main__":

    import time, math

    T = 0.01
    K = 1000

    print("> Testing accelerometer")
    
    accel = IMU()

    k = 0
    while k < K:

        # read accelerometer
        (w, x, y, z) = accel.read()

        print('\r> (w, x, y, z) = ({:+5.3f}, {:+5.3f}, {:+5.3f}, {:+5.3f})g'.format(w, x, y, z), end='')

        time.sleep(T)
        k += 1

    print("\n> Testing inclinometer")

    accel = Inclinometer()

    k = 0
    while k < K:

        # read inclinometer
        (theta, ) = accel.read()
        print('\r> theta = {:+05.3f}deg'.format(360*theta), end='')

        time.sleep(T)
        k += 1


