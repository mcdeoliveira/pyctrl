from Adafruit_I2C import Adafruit_I2C
from time import sleep
import math

# initialize i2c connection to MPU6050
# i2c address is 0x68
i2c = Adafruit_I2C(0x68)

# wake up the device (out of sleep mode)
# bit 6 on register 0x6B set to 0
i2c.write8(0x6B, 0)

print("X, Y, Z axis accelerations (in g's)")

# read and print acceleration on x axis
# Most significant byte on 0x3b
# Least significant byte on 0x3c
# Combined to obtain raw acceleration data
for x in range(0, 10):
        # getting values from the registers
    bx = i2c.readS8(0x3b)
    sx = i2c.readU8(0x3c)
    by = i2c.readS8(0x3d)
    sy = i2c.readU8(0x3e)
    bz = i2c.readS8(0x3f)
    sz = i2c.readU8(0x40)
        # converting 2 8 bit words into a 16 bit
        # signed "raw" value
    x = -(bx * 256 + sx)
    y = -(by * 256 + sy)
    z = -(bz * 256 + sz)

        # still needs to be converted into G-forces
    gx = x / 16384.
    gy = y / 16384.
    gz = z / 16384.

    #r = gy/gx
    rad = math.atan2(gy,gx)
    deg = rad*180/math.pi


    print (str(gx)+'\t' + str(gy)+'\t' + str(gz))
    print (str(rad) + '\t' + str(deg))
    sleep(0.2)
