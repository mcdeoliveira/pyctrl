import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

import time

if __name__ == "__main__":

    import sys
    sys.path.append('.')

import ctrl.block as block

class Motor(block.Block):
        
    def __init__(self, *vars, **kwargs):

        # PWM1 PINS
        self.pwm_pin = kwargs.pop('pwm_pin', 'P9_14')
        self.dir_A   = kwargs.pop('dir_A', 'P9_15')
        self.dir_B   = kwargs.pop('dir_B', 'P9_23')
        self.enable_pin = kwargs.pop('enable_pin', None)

        # call super
        super().__init__(*vars, **kwargs)

        # initialize pwm1
        PWM.start(self.pwm_pin)
        GPIO.setup(self.dir_A, GPIO.OUT)
        GPIO.setup(self.dir_B, GPIO.OUT)
        if self.enable_pin:
            GPIO.setup(self.enable_pin, GPIO.OUT)

    def set_enabled(self, enabled = True):

        # turn on first?
        if (not self.enabled) and enabled:

            # raise enable pint
            if self.enable_pin:
                GPIO.output(self.enable_pin, 1)

        # call super
        super().set_enabled(enabled)

        if not enabled:

            # wait
            time.sleep(0.1)

            # and write 0 to motor
            PWM.set_duty_cycle(self.pwm_pin, 0)

            # lower enable pint
            if self.enable_pin:
                GPIO.output(self.enable_pin, 0)

    def write(self, *values):

        #print('> write to motor')
        if self.enabled:

            pwm = values[0]
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

        
if __name__ == "__main__":

    import time, math

    print("> Testing Motor1")
    
    motor1 = Motor(dir_A='P9_15',
                   dir_B='P9_23',
                   pwm_pin='P9_14')

    # run motor forward
    motor1.write(100)
    time.sleep(1)

    # stop motor
    motor1.write(0)
    time.sleep(1)

    # run back
    motor1.write(-100)
    time.sleep(1)

    # stop motor
    motor1.write(0)

    print("> Testing Motor2")

    motor2 = Motor(dir_A='P9_12',
                   dir_B='P9_27',
                   pwm_pin='P9_16')

    # run motor forward
    motor2.write(100)
    time.sleep(1)

    # stop motor
    motor2.write(0)
    time.sleep(1)

    # run back
    motor2.write(-100)
    time.sleep(1)

    # stop motor
    motor2.write(0)
