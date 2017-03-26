if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

# import python libraries
import time
import math
import numpy
import sys
import warnings

def brief_warning(message, category, filename, lineno, line=None):
    return "*{}\n".format(message)

warnings.formatwarning = brief_warning


from ctrl.rc.mip import Controller
import ctrl.block as block

# initialize mip
Ts = 0.25
mip = Controller(period = Ts)

# define tests

def test(k, args, query_msg, failed_msg, test_function):

    print('\n> TEST #{}'.format(k))
    passed, retval = test_function(args)
    if not passed:
        print("> Failed test #{}: {}".format(k, retval))
        sys.exit(2)
    time.sleep(.1)
    if query_msg:
        answer = input('\n< ' + query_msg + ' [Y/n]').lower()
        if 'n' in answer:
            print("> Failed test #{}: {}".format(k, failed_msg))
            sys.exit(2)
    return retval

def test_motor_forward(args):

    motor, encoder = args[0], args[1]
    with mip:
        position1 = mip.get_signal(encoder)
        mip.set_signal(motor,100)
        time.sleep(2)
        position2 = mip.get_signal(encoder)
        mip.set_signal(motor,0)
    return True, (position1, position2)

def test_encoder(args):

    position1, position2 = args[0], args[1]
    if position2 == position1:
        return False, 'encoder1 not working'
    elif position2 < position1:
        return False, 'encoder1 reading reversed'
    return True, []

def test_reset_clock(args):

    t1 = mip.get_signal('clock')
    mip.set_source('clock', reset = True)
    with mip:
        time.sleep(.1)
    t2 = mip.get_signal('clock')
    if t2 > t1:
        return False, 'clock did not reset ({} > {})'.format(t2,t1)
    return True, []

def test_motor_backward(args):

    motor, encoder = args[0], args[1]
    with mip:
        mip.set_source('clock', reset = True)
        position1 = mip.get_signal(encoder)
        mip.set_signal(motor,-100)
        time.sleep(2)
        position2 = mip.get_signal(encoder)
        mip.set_signal(motor,0)
    return True, (position1, position2)

def test_motor_speeds(args):

    motor, encoder = args[0], args[1]
    with mip:
        mip.set_source('clock', reset = True)
        mip.set_signal(motor,100)
        time.sleep(1)
        mip.set_signal(motor,50)
        time.sleep(1)
        mip.set_signal(motor,0)
    return True, []

def test_reset_encoder(args):

    encoder = args[0]
    with mip:
        time.sleep(.1) # sleep to make sure it is stoped
        position1 = mip.get_signal(encoder)
        mip.set_source(encoder, reset = True)
        time.sleep(.1) # sleep to make sure it did not move
        position2 = mip.get_signal(encoder)

    if position2 != 0:
        return False, 'could not reset encoder1 ({} != 0)'.format(position2)
    return True, [position1, position2]

def test_theta(args):

    with mip:

        # Test IMU
        answer = input('< Lean the MIP near the +90 deg position and hit <ENTER>').lower()
        (theta, thetaDot) = mip.read_source('inclinometer')
        if theta < 0:
            return False, 'Motors are likely reversed'
        if theta < .2:
            return False, 'MIP does not seem to be leaning at +90 degree position'
        
        answer = input('< Lean the MIP near the -90 deg position and hit <ENTER>').lower()
        (theta, thetaDot) = mip.read_source('inclinometer')
        if theta > 0:
            return False, 'Motors are likely reversed'
        if theta > -.2:
            return False, 'MIP does not seem to be leaning at -90 degree position'

    return True, []

def main():

    try:
        
        print("""
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                         S E T U P   M I P                         *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

Welcome to SETUP MIP. This program will help you make sure that your
MIP is working and wired correctly.

The following tests are meant to be performed with the MIP oriented 
as in the following diagram

         /
        /
        O
    =========

The angle theta is measured relative to the vertical with zero being 
above the wheels. For example

                    |
                    |             ---
      ___O           O           O
    ==========   =========   ==========
     +90 deg       0 deg      -90 deg

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    """)

        input('< Hit <ENTER> to start')

        verbose = False
        if verbose:
            mip.add_sink('printer', block.Printer(endln = '\r'), 
                                ['clock',
                                 'motor1','encoder1',
                                 'motor2','encoder2',
                                 'theta','theta_dot'])

            print(mip.info('all'))

        input('< We will spin the wheels. Lift your MIP up in the air and hit <ENTER>')

        k = 1
        position1, position2 \
            = test('{}: MOTOR 1 COUNTER-CLOCKWISE'.format(k), 
                   ('motor1','encoder1'),
                   'Did the wheel nearest to you spin counter-clockwise for two seconds?', 
                   'motor1 not working properly',
                   test_motor_forward)

        k += 1
        test('{}: ENCODER 1 COUNTER-CLOCKWISE'.format(k), 
             (position1, position2),
             '',
             '',
             test_encoder)

        input('< We will spin the wheels. Lift your MIP up in the air and hit <ENTER>')

        k += 1
        position1, position2 \
            = test('{}: MOTOR 2 COUNTER-CLOCKWISE'.format(k), 
                   ('motor2','encoder2'),
                   'Did the wheel farthest from you spin counter-clockwise for two seconds?', 
                   'motor2 not working properly',
                   test_motor_forward)

        k += 1
        test('{}: ENCODER 2 COUNTER-CLOCKWISE'.format(k), 
             (position1, position2),
             '',
             '',
             test_encoder)

        k += 1
        test('{}: CLOCK RESET'.format(k), (), 
             '',
             '',
             test_reset_clock)

        input('< We will spin the wheels. Lift your MIP up in the air and hit <ENTER>')

        k += 1
        position1, position2 \
            = test('{}: MOTOR 1 CLOCKWISE'.format(k),
                   ('motor1','encoder1'),
                   'Did the wheel nearest to you spin clockwise for two seconds?', 
                   'motor1 not working properly',
                   test_motor_backward)

        k += 1
        test('{}: ENCODER 1 CLOCKWISE'.format(k), 
             (position2, position1),
             '',
             '',
             test_encoder)

        input('< We will spin the wheels. Lift your MIP up in the air and hit <ENTER>')

        k += 1
        position1, position2 \
            = test('{}: MOTOR 2 CLOCKWISE'.format(k),
                   ('motor2','encoder2'),
                   'Did the wheel farthest from you spin clockwise for two seconds?', 
                   'motor2 not working properly',
                   test_motor_backward)

        k += 1
        test('{}: ENCODER 2 CLOCKWISE'.format(k), 
             (position2, position1),
             '',
             '',
             test_encoder)

        input('< We will spin the wheels. Lift your MIP up in the air and hit <ENTER>')

        k += 1
        test('{}: MOTOR 1 TWO SPEEDS'.format(k),
             ('motor1','encoder1'),
             'Did wheel nearest to you spin counter-clockwise at full speed then slowed down to half speed?', 
             'motor1 not working properly',
             test_motor_speeds)

        input('< We will spin the wheels. Lift your MIP up in the air and hit <ENTER>')

        k += 1
        test('{}: MOTOR 2 TWO SPEEDS'.format(k),
             ('motor2','encoder2'),
             'Did the wheel farthest from you spin counter-clockwise at full speed then slowed down to half speed?', 
             'motor2 not working properly',
             test_motor_speeds)

        k += 1
        position1, position2 \
            = test('{}: ENCODER 1 RESET'.format(k), 
                   ('encoder1',),
                   '', 
                   '',
                   test_reset_encoder)

        k += 1
        position1, position2 \
            = test('{}: ENCODER 2 RESET'.format(k), 
                   ('encoder2',),
                   '', 
                   '',
                   test_reset_encoder)

        k += 1
        test('{}: TEST THETA'.format(k), 
             ('imu',),
             '', 
             '',
             test_theta)

        print("""
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*            ! ! ! C O N G R A T U L A T I O N S ! ! !              *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

Your MIP seems to be working and is wired correctly.
""")

    except KeyboardInterrupt:
        print("> SETUP MIP aborted...")
        
if __name__ == "__main__":
    main()
