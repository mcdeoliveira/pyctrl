import time
#from ctrl import Controller
from ctrl.bbb import Controller

controller = Controller()

#controller.calibrate()
controller.set_echo(1)
controller.set_logger(2)

with controller:
    time.sleep(1)
    controller.set_reference1(100)
    time.sleep(2)
    controller.set_reference1(-50)
    time.sleep(2)
    controller.set_reference1(0)
    time.sleep(1)
