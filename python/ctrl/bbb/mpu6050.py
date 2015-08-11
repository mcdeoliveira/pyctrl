import Adafruit_I2C as I2C 

from .. import block

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
ACCEL_SCALE = { 
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
GIRO_SCALE = { 
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

class Accelerometer(block.Block):

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

        # call super
        super().__init__(*vars, **kwargs)

        # initialize i2c connection to MPU6050
        self.i2c = I2C.Adafruit_I2C(self.address)

        # Enable low pass filter
        self.i2c.write8(CONFIG, self.dlp_cfg_44)

        # Set sample rate
        self.i2c.write8(SMPRT_DIV, self.smprt_div)
        
        # Set sensitivity
        self.i2c.write8(ACCEL_CONFIG, self.accel_sensitivity)

        if not self.giro_enabled:

            # Disable giroscope
            self.i2c.write8(PWR_MGMT_2, STDB_XG + STDB_YG + STDB_ZG)

        # enable
        self.set_enabled(True)

    def set_enabled(self, enabled  = True):

        # call super
        super().set_enabled(enabled)

        if enabled:
            
            # put in sleep mode
            self.i2c.write8(PWR_MGMT_1, SLEEP)

        else:

            # wake up
            self.i2c.write8(PWR_MGMT_1, 0)

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
                x = -(xh * 256 + xl) / self.afs_scale
                y = -(yh * 256 + yl) / self.afs_scale
                z = -(zh * 256 + zl) / self.afs_scale

                gx = -(gxh * 256 + gxl) / self.gfs_scale
                gy = -(gyh * 256 + gyl) / self.gfs_scale
                gz = -(gzh * 256 + gzl) / self.gfs_scale

                self.output = (x, y, z, gx, gy, gz)

            else: # no giro

                # Burst-read accelerometer registers
                xh, xl, yh, yl, zh, zl = self.i2c.readList(ACCEL_XOUT_H, 6)
                
                # convert 8 bit words into a 16 bit signed "raw" value
                x = -(xh * 256 + xl) / self.afs_scale
                y = -(yh * 256 + yl) / self.afs_scale
                z = -(zh * 256 + zl) / self.afs_scale

                self.output = (x, y, z)
        
            #self.encoder1 = math.atan2(y, x) / (2 * math.pi)

        return self.output
