import warnings

from .. import packet
import ctrl

from .eqep import eQEP
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC

# PWM1 PINS
dir_A = "P9_15"
dir_B = "P9_23"
pwm1  = "P9_14"

# ENC1 PINS
# eQEP2A_in(P8_12)
# eQEP2B_in(P8_11)
eQEP2 = "/sys/devices/ocp.3/48304000.epwmss/48304180.eqep"

class Controller(ctrl.Controller):

    def __init__(self, *pars, **kpars):

        super().__init__(*pars, **kpars)

        # initialize eqep2
        self.eqep2 = eQEP(eQEP2, eQEP.MODE_ABSOLUTE)

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))

        # initialize pwm1
        PWM.start(pwm1)
        GPIO.setup(dir_A,GPIO.OUT)
        GPIO.setup(dir_B,GPIO.OUT)

        # initialize adc
        ADC.setup()

    def set_period(self, value):

        # call super().set_period
        super().set_period(value)

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))

    def read_sensors(self):

        # Read encoder1 in cycles/s
        self.encoder1 = float(self.eqep2.poll_position()) / (48 * 9.68)

        # Read pot1 [0,100]
        self.pot1 = min(100, 100 * ADC.read("AIN0") / 0.88)

        # Read encoder2
        self.encoder2 = 0 # EDUARDO

        # Read pot2
        self.pot2 = 0 # EDUARDO

        return (self.encoder1, self.pot1, self.encoder2, self.pot2)

    def set_encoder1(self, value):
        self.eqep2.set_position(int(value * 48 * 9.68))
        super().set_encoder1(value)

    def set_motor1_pwm(self, value = 0):

        super().set_motor1_pwm(value)

        if self.motor1_dir == 1:
            GPIO.output(dir_A,1)
            GPIO.output(dir_B,0)

        if self.motor1_dir == -1:
            GPIO.output(dir_A,0)
            GPIO.output(dir_B,1)

        PWM.set_duty_cycle(pwm1, self.motor1_pwm)

    def set_motor2_pwm(self, pwm2):
        pass

    def stop(self):
        super().stop()

        # stop motors
        self.set_motor1_pwm(0)
        self.set_motor2_pwm(0)
