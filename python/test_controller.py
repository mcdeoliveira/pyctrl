import time
import platform, sys

def test(k, s, msg):
    print('> TEST #{}'.format(k))
    answer = input('< ' + s + ' ').lower()
    if 'n' in answer:
        print("> Failed test #{}: {}".format(k, msg))
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
    position1 = controller.get_encoder1()
    controller.set_reference1(100)
    time.sleep(2)
    position2 = controller.get_encoder1()
test(k, 'Did the motor spin clockwise for two seconds?', 'motor1 not working')

if position2 == position1:
    print("> Failed test #{}: encoder1 not working".format(k))
    sys.exit(2)
elif position2 < position1:
    print("> Failed test #{}: encoder1 reading reversed".format(k))
    sys.exit(2)

k += 1
with controller:
    position1 = controller.get_encoder1()
    controller.set_reference1(-100)
    time.sleep(2)
    position2 = controller.get_encoder1()
test(k, 'Did the motor spin counterclockwise for two seconds?', 'motor1 not working')

if position2 == position1:
    print("> Failed test #{}: encoder1 not working".format(k))
    sys.exit(2)
elif position2 > position1:
    print("> Failed test #{}: encoder1 reading reversed".format(k))
    sys.exit(2)

k += 1
with controller:
    controller.set_reference1(100)
    time.sleep(1)
    controller.set_reference1(50)
    time.sleep(2)
test(k, 'Did the motor spin clockwise at full speed then slowed down to half speed?', 'motor1 not working')

k += 1
with controller:
    controller.set_reference1(0)
    position1 = controller.get_encoder1()
    controller.set_encoder1(0)
    time.sleep(5*controller.period)
    position2 = controller.get_encoder1()

if position2 != 0:
    print("> Failed test #{}: could not reset encoder1".format(k))
    sys.exit(2)

