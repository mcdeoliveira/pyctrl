import time
import math
import numpy
import platform, sys

from ctrl.bbb import Controller
from ctrl.algo import Proportional, PID, OpenLoop

k = 0.11
a = 17 

controller = Controller()

controller.set_echo(1)
controller.set_logger(120)

gear = 1.5
pmax = gear * .5 

#controller.set_controller1(PID(1/k, .1, 0*a/k, pmax))
#controller.set_controller1(Proportional(200/k, pmax))
controller.set_controller1(OpenLoop())
controller.set_encoder1(0)

with controller:
    #controller.set_reference1(100 * gear * 15 / 360 / pmax)
    for ref in range(0, 105, 5):
        print('\nref = {}'.format(ref))
        controller.set_reference1(ref)
        time.sleep(2)

