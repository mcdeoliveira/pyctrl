import ctrl.bbb
from ctrl.algo import *

def main():

    Ts = 0.01              # s
    a = 17                 # 1/s
    k = 0.163               # cycles/s duty

    controller = Controller(Ts, 1)
    controller.set_logger(2)

    # open loop controller
    print('> OPEN LOOP CONTROL (REFERENCE)')
    controller.start()
    time.sleep(1)
    controller.set_reference1(100)
    time.sleep(2)
    controller.set_reference1(50)
    time.sleep(2)
    controller.set_reference1(-50)
    time.sleep(2)
    controller.set_reference1(-100)
    time.sleep(2)
    controller.set_reference1(0)
    time.sleep(1)
    controller.stop()

    print('> OPEN LOOP CONTROL (POTENTIOMETER)')
    controller.set_reference1_mode(1)
    controller.start()
    time.sleep(2)
    controller.stop()

    reference = 6
    print('> CLOSED LOOP CONTROL (POSITION, REFERENCE = {})'.format(reference))
    controller.set_reference1_mode(0)
    controller.set_controller1(
        ProportionalController(30 / k, reference / 100)
    )
    controller.start()
    time.sleep(1)
    controller.set_reference1(100)
    time.sleep(2)
    controller.stop()

    print('> CLOSED LOOP CONTROL (POSITION, POTENTIOMETER)')
    controller.set_reference1_mode(1)
    controller.set_controller1(
        ProportionalController(30 / k, reference / 100)
    )
    controller.start()
    time.sleep(5)
    controller.stop()

    reference = 11

    controller.set_controller1(
        VelocityController(ProportionalController(5 / k, reference / 100))
    )

    print('> CLOSED LOOP ON VELOCITY')
    controller.set_reference1_mode(0)
    controller.start()
    time.sleep(1)
    controller.set_reference1(100)
    print('\n> REFERENCE = {}'.format(reference))
    time.sleep(3)
    controller.set_reference1(50)
    print('\n> REFERENCE = {}'.format(reference/2))
    time.sleep(3)
    controller.set_reference1(-50)
    print('\n> REFERENCE = {}'.format(-reference/2))
    time.sleep(3)
    controller.stop()



if __name__ == "__main__":

    main()
