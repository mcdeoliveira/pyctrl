import time
import numpy

from ctrl.algo import Proportional
import ctrl.client

HOST, PORT = "192.168.10.107", 9999
HOST, PORT = "localhost", 9999

controller = ctrl.client.Controller(HOST, PORT)
print(controller.help())

print(controller.help('s'))
print(controller.help('S'))

controller.set_echo(0)
controller.reset_logger()

with controller:
    time.sleep(1)
    controller.set_reference1(100)
    time.sleep(1)
    controller.set_reference1(-50)
    time.sleep(1)
    controller.set_reference1(0)
    time.sleep(1)
    
print(controller.get_log())
print(controller.get_encoder1())

    # controller.set_logger(2)

    # controller.start()
    # time.sleep(1)
    # controller.set_reference1(100)
    # time.sleep(1)
    # controller.set_reference1(-100)
    # time.sleep(1)
    # controller.stop()

    # print(controller.get_log())

    # controller.set_controller1(Proportional(1, 1))
