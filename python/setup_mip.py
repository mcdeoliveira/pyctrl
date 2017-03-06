import time
import math
import numpy
import platform, sys, select

from mip import Controller
import ctrl.block as block
import ctrl.block.logger as logger

# initialize controller
#HOST, PORT = "192.168.10.101", 9999
#controller = Controller(host = HOST, port = PORT)
Ts = 0.25;
controller = Controller(period = Ts)
logger_signals = ['clock','encoder1','encoder2']
controller.add_sink('logger', 
                    logger.Logger(), 
                    logger_signals)
controller.add_sink('printer', block.Printer(endln = '\r'), 
                    ['clock',
                     'motor1','encoder1',
                     'motor2','encoder2',
                     'theta','theta_dot'])
    
print(controller.info('all'))

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
    with controller:
        position1 = controller.get_signal(encoder)
        controller.set_signal(motor,100)
        time.sleep(2)
        position2 = controller.get_signal(encoder)
        controller.set_signal(motor,0)
    return True, (position1, position2)

def test_encoder(args):

    position1, position2 = args[0], args[1]
    if position2 == position1:
        return False, 'encoder1 not working'
    elif position2 < position1:
        return False, 'encoder1 reading reversed'
    return True, []

def test_reset_clock(args):

    t1 = controller.get_signal('clock')
    controller.set_source('clock', reset = True)
    with controller:
        time.sleep(.1)
    t2 = controller.get_signal('clock')
    if t2 > t1:
        return False, 'clock did not reset ({} > {})'.format(t2,t1)
    return True, []

def test_motor_backward(args):

    motor, encoder = args[0], args[1]
    with controller:
        controller.set_source('clock', reset = True)
        position1 = controller.get_signal(encoder)
        controller.set_signal(motor,-100)
        time.sleep(2)
        position2 = controller.get_signal(encoder)
        controller.set_signal(motor,0)
    return True, (position1, position2)

def test_motor_speeds(args):

    motor, encoder = args[0], args[1]
    with controller:
        controller.set_source('clock', reset = True)
        controller.set_signal(motor,100)
        time.sleep(1)
        controller.set_signal(motor,50)
        time.sleep(1)
        controller.set_signal(motor,0)
    return True, []

def test_reset_encoder(args):

    encoder = args[0]
    with controller:
        time.sleep(.1) # sleep to make sure it is stoped
        position1 = controller.get_signal(encoder)
        controller.set_source(encoder, reset = True)
        time.sleep(.1) # sleep to make sure it did not move
        position2 = controller.get_signal(encoder)

    if position2 != 0:
        return False, 'could not reset encoder1 ({} != 0)'.format(position2)
    return True, [position1, position2]

def test_theta(args):

    with controller:

        # Test IMU
        answer = input('> Lean the MIP near the +90 deg position and hit <ENTER>').lower()
        (theta, thetaDot) = controller.read_source('imu')
        if theta < 0:
            return False, 'Motors are likely reversed'
        if theta < .2:
            return False, 'MIP does not seem to be leaning at +90 degree position'
        
        answer = input('> Lean the MIP near the -90 deg position and hit <ENTER>').lower()
        (theta, thetaDot) = controller.read_source('imu')
        if theta > 0:
            return False, 'Motors are likely reversed'
        if theta > -.2:
            return False, 'MIP does not seem to be leaning at -90 degree position'

    return True, []

def identify_motor(motor, encoder, T = 2):

    # Identify motors
    print("\n> Identifying motor '{}' parameters...".format(motor))
    with controller:

        controller.set_signal(motor,0)
        controller.set_source(encoder, reset = True)

        controller.set_sink('logger', reset = True)
        controller.set_source('clock', reset = True)
        time.sleep(1)
        controller.set_signal(motor,100)
        time.sleep(2*T)

        controller.set_signal(motor,0)
        
    clock = controller.get_source('clock', 'period')
    Ts = clock['period']
    print('>> controller period = {}'.format(Ts))
    print('>> test time = {}'.format(T))
     
    log = controller.read_sink('logger')
    tind = logger_signals.index('clock')
    eind = logger_signals.index(encoder)

    t = log[:,tind]
    position = log[:,eind]
    velocity = numpy.zeros(t.shape, float)
    velocity[1:] = (position[1:]-position[:-1])/(t[1:]-t[:-1])
        
    max_velocity = numpy.max(velocity)
    print('>> max velocity = {:5.3f}'.format(max_velocity))

    ind = numpy.argwhere(velocity > .5*max_velocity)[0]
    ind = int((t.size + ind)/2)
    mean_velocity = numpy.mean(velocity[ind:])
    print('>> average terminal velocity = {:5.3f}'.format(mean_velocity))

    ind = numpy.argwhere( (velocity > 0.1*mean_velocity ) & 
                          (velocity < 0.9*mean_velocity ) )
    t10 = float(t[ind[0]])
    t90 = float(t[ind[-1]])
    tau = (t90 - t10) / 2.2
    print('>> rise time = {:5.3f}'.format(t90 - t10))
    
    print('>> lambda    = {:5.3f}'.format(1/tau))

    KMAX = 10 
    k = 0
    tau = 0;
    while k < KMAX:

        k += 1
        print('>> TEST {} out of {}'.format(k, KMAX))
        
        with controller:

            controller.set_source(encoder, reset = True)
            controller.set_source('clock', reset = True)
            controller.set_sink('logger', reset = True)
            
            controller.set_signal(motor,100)
            time.sleep(T)
            controller.set_signal(motor,0)

            log = controller.read_sink('logger')
            tind = logger_signals.index('clock')
            eind = logger_signals.index(encoder)

            t = log[:,tind]
            position = log[:,eind]
            velocity = numpy.zeros(t.shape, float)
            velocity[1:] = (position[1:]-position[:-1])/(t[1:]-t[:-1])
            
            ind = numpy.argwhere( (velocity > 0.1*mean_velocity ) & 
                                  (velocity < 0.9*mean_velocity ) )
            t10 = float(t[ind[0]])
            t90 = float(t[ind[-1]])
            tau += (t90 - t10) / 2.2 / KMAX

            time.sleep(0.1)

    print('>> lambda    = {:5.3f}'.format(1/tau))

def main():

    print('> MIP Test Routine')

    try:

        print("""
* * * * * * * * * *
* T E S T   M I P *
* * * * * * * * * *

This test will help you make sure the MIP is wired correctly. The
following tests are meant to be performed with the MIP oriented as

      /
     /
    O
  ======

The angle theta is measured relative to the vertical with zero being 
above the wheels.

""")

        input('Hit <ENTER> to start the tests.')
        
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

        k += 1
        test('{}: MOTOR 1 TWO SPEEDS'.format(k),
             ('motor1','encoder1'),
             'Did wheel nearest to you spin counter-clockwise at full speed then slowed down to half speed?', 
             'motor1 not working properly',
             test_motor_speeds)

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

        T = 2
        identify_motor('motor1', 'encoder1', T)
        identify_motor('motor2', 'encoder2', T)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        print('Exiting...')
    
if __name__ == "__main__":
    main()
