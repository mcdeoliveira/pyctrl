import time
import ctrl

controller = ctrl.Controller()

controller.calibrate()
controller.set_echo(1)
controller.set_logger(2)

controller.start()
time.sleep(1)
controller.set_reference1(100)
time.sleep(1)
controller.set_reference1(-50)
time.sleep(1)
controller.set_reference1(0)
time.sleep(1)
controller.stop()
