import Adafruit_I2C as I2C 

if __name__ == "__main__":

    import sys
    sys.path.append('.')

import math
import struct

import ctrl.block as block

# SAMPLE RATE = GIRO_RATE / (1 + SMPLRT_DIV[7:0])
# GIRO_RATE = 1kHz if 0 < DLP_CFG < 7
#           = 8kHz if DLP_CFG = 0 or DLP_CFG = 7
SMPRT_DIV = 0x19

# CONFIG
CONFIG = 0x1a
# 
DLP_CFG_260 = 0x00
DLP_CFG_184 = 0x01
DLP_CFG_94  = 0x02
DLP_CFG_44  = 0x03
DLP_CFG_21  = 0x04
DLP_CFG_10  = 0x05
DLP_CFG_5   = 0x06

# ACCEL_CONFIG
ACCEL_CONFIG = 0x1c
# AFS_SEL
AFS_SEL_2  = 0x00 << 3
AFS_SEL_4  = 0x01 << 3
AFS_SEL_8  = 0x02 << 3
AFS_SEL_16 = 0x03 << 3

# SENSIVITY (LSB/g)
AFS_SCALE = { 
    AFS_SEL_2  : 16384,
    AFS_SEL_4  : 8192,
    AFS_SEL_8  : 4096,
    AFS_SEL_16 : 2048
}

# ACCEL_CONFIG
GIRO_CONFIG = 0x1c
# GFS_SEL
GFS_SEL_250  = 0x00 << 3
GFS_SEL_500  = 0x01 << 3
GFS_SEL_1000 = 0x02 << 3
GFS_SEL_2000 = 0x03 << 3

# SENSIVITY (LSB/^o/s)
GFS_SCALE = { 
    GFS_SEL_250  : 131,
    GFS_SEL_500  : 65.5,
    GFS_SEL_1000 : 32.8,
    GFS_SEL_2000 : 16.4
}

# ACCEL_OUT
ACCEL_XOUT_H = 0x3b
ACCEL_XOUT_L = 0x3c
ACCEL_YOUT_H = 0x3d
ACCEL_YOUT_L = 0x3e
ACCEL_ZOUT_H = 0x3f
ACCEL_ZOUT_L = 0x40

# TEMP_OUT_H
TEMP_OUT_H = 0x41
TEMP_OUT_L = 0x42

# GIRO_OUT
GIRO_XOUT_H = 0x43
GIRO_XOUT_L = 0x44
GIRO_YOUT_H = 0x45
GIRO_YOUT_L = 0x46
GIRO_ZOUT_H = 0x47
GIRO_ZOUT_L = 0x48

# PWR_MGMT_1
PWR_MGMT_1 = 0x6b
SLEEP    = 0x01 << 6
CYCLE    = 0x01 << 5
TEMP_DIS = 0x01 << 3

# PWR_MGMT_2
PWR_MGMT_2 = 0x6c
STDB_XA = 0x01 << 5
STDB_YA = 0x01 << 4
STDB_ZA = 0x01 << 3
STDB_XG = 0x01 << 2
STDB_YG = 0x01 << 1
STDB_ZG = 0x01 << 0

class IMU(block.Block):

    def __init__(self, *vars, **kwargs):

        # set address
        # default i2c address is 0x68
        self.address = kwargs.pop('address', 0x68)

        # set low pass filter
        self.dlp_cfg = kwargs.pop('dlp_cfg', DLP_CFG_44)

        # sample rate divider
        # default = 1kHz / (1 + 9) = 100Hz
        self.smprt_div = kwargs.pop('smprt_div', 0x09)

        # accel sensitivity
        self.accel_sensitivity = kwargs.pop('accel_sensitivity', AFS_SEL_2)
        self.afs_scale = AFS_SCALE[self.accel_sensitivity]

        # giro enabled (default is False)
        self.giro_enabled = kwargs.pop('giro_enabled', False)

        # giro sensitivity
        self.giro_sensitivity = kwargs.pop('accel_sensitivity', GFS_SEL_250)
        self.gfs_scale = GFS_SCALE[self.giro_sensitivity]

        # debug_I2C?
        self.debug_I2C = kwargs.pop('debug_I2C', False)

        # call super
        super().__init__(*vars, **kwargs)

        # initialize i2c connection to MPU6050
        self.i2c = I2C.Adafruit_I2C(self.address, debug = self.debug_I2C)

        # Enable low pass filter
        if self.i2c.write8(CONFIG, self.dlp_cfg) is not None:
            raise Exception('Failed to connect to i2c device.')

        # Set sample rate
        self.i2c.write8(SMPRT_DIV, self.smprt_div)
        
        # Set sensitivity
        self.i2c.write8(ACCEL_CONFIG, self.accel_sensitivity)

        if self.giro_enabled:

            # TO DO: Configure giroscope
            pass

        else:
            
            # Disable giroscope
            self.i2c.write8(PWR_MGMT_2, STDB_XG + STDB_YG + STDB_ZG)

        # enable
        self.set_enabled(True)

    def set_enabled(self, enabled  = True):

        # call super
        super().set_enabled(enabled)

        if enabled:
            
            # wake up
            self.i2c.write8(PWR_MGMT_1, 0)

        else:

            # put in sleep mode
            self.i2c.write8(PWR_MGMT_1, SLEEP)

    def read(self):

        #print('> read')
        if self.enabled:

            if self.giro_enabled:

                # Burst-read accelerometer, temp and giro registers
                xh, xl, yh, yl, zh, zl, \
                    th, tl, \
                    gxh, gxl, gyh, gyl, gzh, gzl = \
                        self.i2c.readList(ACCEL_XOUT_H, 14)
                
                # convert 8 bit words into a 16 bit signed "raw" value
                (x,) = struct.unpack('<h', bytes([xl, xh]))
                (y,) = struct.unpack('<h', bytes([yl, yh]))
                (z,) = struct.unpack('<h', bytes([zl, zh]))

                # convert 8 bit words into a 16 bit signed "raw" value
                (gx,) = struct.unpack('<h', bytes([gxl, gxh]))
                (gy,) = struct.unpack('<h', bytes([gyl, gyh]))
                (gz,) = struct.unpack('<h', bytes([gzl, gzh]))

                self.output = (x / self.afs_scale, 
                               y / self.afs_scale, 
                               z / self.afs_scale, 
                               gx / self.gfs_scale, 
                               gy / self.gfs_scale, 
                               gz / self.gfs_scale)

            else: # no giro

                # Burst-read accelerometer registers
                xh, xl, yh, yl, zh, zl = self.i2c.readList(ACCEL_XOUT_H, 6)

                # convert 8 bit words into a 16 bit signed "raw" value
                (x,) = struct.unpack('<h', bytes([xl, xh]))
                (y,) = struct.unpack('<h', bytes([yl, yh]))
                (z,) = struct.unpack('<h', bytes([zl, zh]))

                self.output = (x / self.afs_scale,
                               y / self.afs_scale,
                               z / self.afs_scale)
        
        return self.output

class Inclinometer(IMU):

    def __init__(self, *vars, **kwargs):

        # zero: location of the zero angle
        self.zero = kwargs.pop('zero', 0)

        self.turns = 0
        self.quadrant = 0

        # call super
        super().__init__(*vars, **kwargs)

    def reset(self):

        # call super
        super().reset()

        self.turns = 0
        self.quadrant = 0

    def set(self, **kwargs):
        
        if 'zero' in kwargs:
            self.zero = kwargs.pop('zero')

        super().set(**kwargs)

    def read(self):

        # read accelerometer
        (x, y, z) = super().read()

        # calculate angle
        theta = math.atan2(y, x) / (2 * math.pi)

        # calculate quadrant
        if x >= 0:
            if y >= 0:
                quadrant = 1
            else:
                quadrant = 4
        elif y >= 0:
            quadrant = 2
        else:
            quadrant = 3

        if not self.quadrant:
            self.quadrant = quadrant

        else:

            if quadrant == 3 and self.quadrant == 2:
                self.turns += 1
            elif quadrant == 2 and self.quadrant == 3:
                self.turns -= 1

        #print('quadrant = {}, last = {}, turns = {}'.format(quadrant,
        #                                                    self.quadrant,
        #                                                    self.turns))

        self.quadrant = quadrant

        return (self.turns + theta, )

if __name__ == "__main__":

    import time, math

    T = 0.1
    K = 10

    print("> Testing accelerometer")
    
    accel = IMU()

    k = 0
    while k < K:

        # read accelerometer
        (x, y, z) = accel.read()

        print('\r> (x, y, z) = ({:5.3f}, {:5.3f}, {:5.3f})g'.format(x, y, z), end='')

        time.sleep(T)
        k += 1

    K = 100
    print("\n> Testing inclinometer")

    accel = Inclinometer()

    k = 0
    while k < K:

        # read inclinometer
        (theta, ) = accel.read()
        print('\r> theta = {:5.3f}deg'.format(360*theta), end='')

        time.sleep(T)
        k += 1
