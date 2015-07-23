import time
import platform, sys

def test(k, s):
    print('> TEST #{}'.format(k))
    answer = input('< ' + s + ' ').lower()
    if 'n' in answer:
        print("> Failed test #{}".format(k))
        sys.exit(2)

# Are we on the beaglebone?
if 'bone' in platform.uname()[2]:
    from ctrl.bbb import Controller
    simulated = False
else:
    from ctrl import Controller
    simulated = True
    
controller = Controller()

if simulated:
    controller.calibrate()

controller.set_echo(1)
controller.set_logger(2)

print('Controller Test Routine')

k = 1
with controller:
    controller.set_reference1(100)
    time.sleep(2)
test(k, 'Did the motor spin clockwise for two seconds?')

k += 1
with controller:
    controller.set_reference1(-100)
    time.sleep(2)
test(k, 'Did the motor spin counterclockwise for two seconds?')

k += 1
with controller:
    controller.set_reference1(100)
    time.sleep(1)
    controller.set_reference1(50)
    time.sleep(2)
test(k, 'Did the motor spin clockwise at full speed then slowed down to half speed?')
