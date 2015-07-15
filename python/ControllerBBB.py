import warnings
from Controller import Controller
from eqep import eQEP
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
import time
import sys

# PWM1 PINS
dir_A = "P9_15"
dir_B = "P9_23"
pwm1  = "P9_14"

# ENC1 PINS
# eQEP2A_in(P8_12)
# eQEP2B_in(P8_11)
eQEP2 = "/sys/devices/ocp.3/48304000.epwmss/48304180.eqep"

class ControllerBBB(Controller):

    def __init__(self, *pars, **kpars):

        super().__init__(*pars, **kpars)

        self.eqep2 = eQEP(eQEP2, eQEP.MODE_ABSOLUTE)
        self.set_period(self.period)

        PWM.start(pwm1)
        GPIO.setup(dir_A,GPIO.OUT)
        GPIO.setup(dir_B,GPIO.OUT)

        ADC.setup()

    def set_period(self, value):

        # call super().set_period
        super().set_period(value)

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))

    def read_sensors(self):

        # Read encoder1
        encoder1 = self.eqep2.poll_position()

        # Read pot1
        pot1 = min(100, 100 * ADC.read("AIN0") / 0.88)

        # Read encoder2
        encoder2 = 0 # EDUARDO

        # Read pot2
        pot2 = 0 # EDUARDO

        return (encoder1, pot1, encoder2, pot2)

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


if __name__ == "__main__":

    from ControlAlgorithm import *

    controller = ControllerBBB()

    controller.set_echo(1)
    controller.set_logger(2)

    controller.start()
    time.sleep(1)
    controller.set_reference1(100)
    time.sleep(5)
    controller.set_reference1(-50)
    time.sleep(5)
    controller.set_reference1(0)
    time.sleep(1)
    controller.set_reference1_mode(1)
    time.sleep(30)
    controller.stop()
