import warnings

from .. import packet
import ctrl

from .eqep import eQEP
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
import Adafruit_I2C as I2C 
import math

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from .. import gettime
    perf_counter = gettime.gettime
    warnings.warn('Using gettime instead of perf_counter',
                  RuntimeWarning)
else:
    import time
    perf_counter = time.perf_counter

class Clock():

    def __init__(self, period):
        
        # set period
        self.period = period

        # set time_origin
        self.time_origin = perf_counter()
        self.time = self.time_origin
        self.counter = 0

        # ENC1 PINS
        # eQEP2A_in(P8_12)
        # eQEP2B_in(P8_11)
        eQEP2 = "/sys/devices/ocp.3/48304000.epwmss/48304180.eqep"

        # initialize eqep2
        self.eqep2 = eQEP(eQEP2, eQEP.MODE_ABSOLUTE)
        self.encoder1 = 0

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))

    def set_period(self, period):
        
        # set period
        self.period = period

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))

    def get_encoder1(self):

        return self.encoder1
        
    def set_encoder1(self, value):

        self.eqep2.set_position(int(value))
        
    def read(self):

        #print('> read')
        if self.enabled:

            # Read encoder1 (blocking call)
            self.encoder1 = self.eqep2.poll_position()
        
        return (self.time - self.time_origin, )

class Encoder():
        
    def __init__(self, clock):
        
        # set clock
        self.clock = clock

        # gear ratio
        self.ratio = 48 * 9.6
        
        # output is in cycles/s
        self.output = (self.clock.encoder1 / self.ratio, )

    def write(self, values):

        self.clock.set_encoder1(int(values[0] * self.ratio))

    def read(self):

        #print('> read')
        if self.enabled:

            self.output = (self.clock.get_encoder1() / self.ratio, )
        
        return self.output

class Potentiometer():
        
    def __init__(self):

        # initialize adc
        ADC.setup()
        
        self.pin = "AIN0"
        self.full_scale = 0.88

    def read(self):

        #print('> read')
        if self.enabled:

            self.output = (min(100, 
                               100 * ADC.read(self.pin) / self.full_scale), )
        
        return self.output
        
class Accelerometer():

    def __init__(self):

        # initialize i2c connection to MPU6050
        # i2c address is 0x68
        self.i2c = I2C.Adafruit_I2C(0x68)

        # wake up the device (out of sleep mode)
        # bit 6 on register 0x6B set to 0
        self.i2c.write8(0x6B, 0)

    def read(self):

        #print('> read')
        if self.enabled:

            # getting values from the registers
            bx = self.i2c.readS8(0x3b)
            sx = self.i2c.readU8(0x3c)
            by = self.i2c.readS8(0x3d)
            sy = self.i2c.readU8(0x3e)
            bz = self.i2c.readS8(0x3f)
            sz = self.i2c.readU8(0x40)

            # converting 2 8 bit words into a 16 bit
            # signed "raw" value
            x = -(bx * 256 + sx)
            y = -(by * 256 + sy)
            z = -(bz * 256 + sz)

            self.output = (x, y, z)
        
            #self.encoder1 = math.atan2(y, x) / (2 * math.pi)

        return self.output

class Motor():
        
    def __init__(self):
        
        # PWM1 PINS
        self.dir_A   = "P9_15"
        self.dir_B   = "P9_23"
        self.pwm_pin = "P9_14"

        # initialize pwm1
        PWM.start(self.pwm)
        GPIO.setup(self.dir_A, GPIO.OUT)
        GPIO.setup(self.dir_B, GPIO.OUT)

    def write(self, values):

        #print('> read')
        if self.enabled:

            self.motor_pwm = values[0]
            if self.motor_pwm > 0:

                pwm = self.motor_pwm
                GPIO.output(self.dir_A, 1)
                GPIO.output(self.dir_B, 0)

            else:

                pwm = - self.motor_pwm
                GPIO.output(self.dir_A, 0)
                GPIO.output(self.dir_B, 1)

            PWM.set_duty_cycle(self.pwm_pin, pwm)
        
        return self.output

class Controller(ctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # Initialize controller
        super().__init__(*vargs, **kwargs)

        # add source: clock
        self.clock = Clock(self.period)
        self.add_source('clock', self.clock, ['clock'])
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

        # add signals
        self.add_signals('motor1', 'encoder1', 'pot1')

        # add source: encoder1
        self.encoder1 = Encoder(self.clock)
        self.add_source('encoder1', self.encoder1, ['encoder1'])

        # add source: pot1
        self.pot1 = Potentiometer()
        self.add_source('pot1', self.pot1, ['pot1'])

        # add sink: motor1
        self.motor1 = Motor()
        self.add_source('motor1', self.motor1, ['motor1'])

    def stop(self):

        super().stop()

        # stop motors
        self.motor1.write((0,))
