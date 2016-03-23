import Adafruit_BBIO.PWM as PWM

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

            # wait
            time.sleep(0.1)

            # and write 0 to motor
            PWM.set_duty_cycle(self.pwm_pin, 0)

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

    T = 1

    print("> Testing motor")
    
    motor = Motor()

    % step motor
    pwm = 100
    print('\r> MOTOR @ {:5.3f}'.format(pwm), end='')
    motor.write((pwm,))
    time.sleep(T)

    pwm = 50
    print('\r> MOTOR @ {:5.3f}'.format(pwm), end='')
    motor.write((pwm,))
    time.sleep(T)

    pwm = -50
    print('\r> MOTOR @ {:5.3f}'.format(pwm), end='')
    motor.write((pwm,))
    time.sleep(T)

    pwm = -100
    print('\r> MOTOR @ {:5.3f}'.format(pwm), end='')
    motor.write((pwm,))
    time.sleep(T)
