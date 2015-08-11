import warnings
import time
import math

from .. import block
import ctrl

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC

from .eqep import eQEP

from . import mpu6050

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

class Clock(block.Block):

    def __init__(self, *vars, **kwargs):

        # set period
        self.period = kwargs.pop('period')

        # call super
        super().__init__(*vars, **kwargs)
        
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
        
            # Read clock
            self.time = perf_counter()

        return (self.time - self.time_origin, )

class Encoder(block.Block):
        
    def __init__(self, *vars, **kwargs):

        # set period
        self.clock = kwargs.pop('clock')

        # gear ratio
        self.ratio = kwargs.pop('ratio', 48 * 98.78)

        # call super
        super().__init__(*vars, **kwargs)
        
        # output is in cycles/s
        self.output = (self.clock.encoder1 / self.ratio, )

    def write(self, values):

        self.clock.set_encoder1(int(next(values) * self.ratio))

    def read(self):

        #print('> read')
        if self.enabled:

            self.output = (self.clock.get_encoder1() / self.ratio, )
        
        return self.output

class Potentiometer(block.Block):
        
    def __init__(self, *vars, **kwargs):

        # set pin
        self.pin = kwargs.pop('pin', 'AIN0')

        # set full_scale
        self.full_scale = kwargs.pop('full_scale', 0.88)

        # call super
        super().__init__(*vars, **kwargs)

        # initialize adc
        ADC.setup()
        
    def read(self):

        #print('> read')
        if self.enabled:

            self.output = (min(100, 
                               100 * ADC.read(self.pin) / self.full_scale), )
        
        return self.output
        
class Motor(block.Block):
        
    def __init__(self, *vars, **kwargs):

        # PWM1 PINS
        self.dir_A   = kwargs.pop('dir_A', 'P9_15')
        self.dir_B   = kwargs.pop('dir_B', 'P9_23')
        self.pwm_pin = kwargs.pop('pwm_pin', 'P9_14')

        # call super
        super().__init__(*vars, **kwargs)

        # initialize pwm1
        PWM.start(self.pwm_pin)
        GPIO.setup(self.dir_A, GPIO.OUT)
        GPIO.setup(self.dir_B, GPIO.OUT)

    def set_enabled(self, enabled = True):

        # call super
        super().set_enabled(enabled)

        if not enabled:
            
            # write 0 to motor
            PWM.set_duty_cycle(self.pwm_pin, 0)

    def write(self, values):

        #print('> write to motor')
        if self.enabled:

            pwm = next(values)
            if pwm >= 0:

                pwm = min(100, pwm)
                GPIO.output(self.dir_A, 1)
                GPIO.output(self.dir_B, 0)

            else:

                pwm = min(100, -pwm)
                GPIO.output(self.dir_A, 0)
                GPIO.output(self.dir_B, 1)

            #print('> pwm = {}'.format(pwm))
            PWM.set_duty_cycle(self.pwm_pin, pwm)
        
class Controller(ctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # Initialize controller
        super().__init__(*vargs, **kwargs)

        # add source: clock
        self.clock = Clock(period = self.period)
        self.add_source('clock', self.clock, ['clock'])
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

        # add signals
        self.add_signals('motor1', 'encoder1', 'pot1', 'theta')

        # add source: encoder1
        self.encoder1 = Encoder(clock = self.clock)
        self.add_source('encoder1', self.encoder1, ['encoder1'])

        # add source: pot1
        self.pot1 = Potentiometer()
        self.add_source('pot1', self.pot1, ['pot1'])

        # add source: incl1
        self.incl = mpu6050.Inclinometer()
        self.add_source('theta', self.incl, ['theta']) 

        # add sink: motor1
        self.motor1 = Motor()
        self.add_sink('motor1', self.motor1, ['motor1'])

    def stop(self):

        # stop
        super().stop()

        # then disable motor
        self.motor1.set_enabled(False)


    def start(self):

        # enable motor
        self.motor1.set_enabled(True)

        # then start
        super().start()
