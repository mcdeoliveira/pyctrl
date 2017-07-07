#!/usr/bin/env python3

import time
import math
import numpy
import platform, sys, select

from pyctrl.client import Controller
import pyctrl.block as block
import pyctrl.block.logger as logger

# initialize robut
HOST, PORT = "192.168.10.101", 9999
robut = Controller(host = HOST, port = PORT)
logger_signals = ['clock','encoder1','encoder2']
robut.add_sink('logger', 
               logger.Logger(), 
               logger_signals)
robut.add_sink('printer', block.Printer(endln = '\r'), 
               ['clock',
                'motor1', 'encoder1',
                'motor2', 'encoder2',
                #'imu',
                'mic1','mic2',
                'prox1','prox2'])

print(robut.info('all'))

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
    with robut:
        position1 = robut.get_signal(encoder)
        robut.set_signal(motor,100)
        time.sleep(2)
        position2 = robut.get_signal(encoder)
        robut.set_signal(motor,0)
    return True, (position1, position2)

def test_encoder(args):

    position1, position2 = args[0], args[1]
    if position2 == position1:
        return False, 'encoder1 not working'
    elif position2 < position1:
        return False, 'encoder1 reading reversed'
    return True, []

def test_reset_clock(args):

    t1 = robut.get_signal('clock')
    robut.set_source('clock', reset = True)
    with robut:
        time.sleep(.1)
    t2 = robut.get_signal('clock')
    if t2 > t1:
        return False, 'clock did not reset ({} > {})'.format(t2,t1)
    return True, []

def test_motor_backward(args):

    motor, encoder = args[0], args[1]
    with robut:
        robut.set_source('clock', reset = True)
        position1 = robut.get_signal(encoder)
        robut.set_signal(motor,-100)
        time.sleep(2)
        position2 = robut.get_signal(encoder)
        robut.set_signal(motor,0)
    return True, (position1, position2)

def test_motor_speeds(args):

    motor, encoder = args[0], args[1]
    with robut:
        robut.set_source('clock', reset = True)
        robut.set_signal(motor,100)
        time.sleep(1)
        robut.set_signal(motor,50)
        time.sleep(1)
        robut.set_signal(motor,0)
    return True, []

def test_reset_encoder(args):

    encoder = args[0]
    with robut:
        time.sleep(.1) # sleep to make sure it is stoped
        position1 = robut.get_signal(encoder)
        robut.set_source(encoder, reset = True)
        time.sleep(.1) # sleep to make sure it did not move
        position2 = robut.get_signal(encoder)

    if position2 != 0:
        return False, 'could not reset encoder1 ({} != 0)'.format(position2)
    return True, [position1, position2]

def test_potentiometer(args):
    
    # Calibrate potentiometer
    KMAX = 600 
    TOL = 2
    #robut.get_source('pot1', ['full_scale', 'invert'])
    robut.set_source('pot1', full_scale = 1, invert = False)
    inverted = False
    full_scale = 100
    print("> Set the potentiometer to the minimum position and hit <ENTER>") 
    k = 0
    while k < KMAX:
        pot_min, = robut.read_source('pot1')
        print('\r  reading = {:4.1f}'.format(pot_min), end='')
        time.sleep(.1)
        if select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if pot_min > TOL:
                inverted = True
                full_scale = pot_min
            break
        k += 1

    #if pot_min > TOL:
    #    return (False, 'potentiometer did not reach minimum')

    print("\n> Set the potentiometer to the maximum position and hit <ENTER>") 
    k = 0
    pot_max = 0
    while k < KMAX:
        pot_max, = robut.read_source('pot1')
        print('\r  reading = {:4.1f}'.format(pot_max), end='')
        time.sleep(.1)
        if select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if pot_max > TOL:
                inverted = False
                full_scale = pot_max
            break
        k += 1

    #if pot_max < 100 - TOL:
    #    return (False, 'potentiometer did not reach maximum')

    if inverted:
        print('> Potentiometer is INVERTED')
    else:
        print('> Potentiometer IS NOT inverted')
    print('> Full scale is {}'.format(full_scale))

    return True, [pot_min, pot_max]

def identify_motor(motor, encoder, T = 2):

    # Identify motors
    print("\n> Identifying motor '{}' parameters...".format(motor))
    with robut:

        robut.set_signal(motor,0)
        robut.set_source(encoder, reset = True)

        robut.set_sink('logger', reset = True)
        robut.set_source('clock', reset = True)
        time.sleep(1)
        robut.set_signal(motor,100)
        time.sleep(T)

        robut.set_signal(motor,0)
        
    clock = robut.get_source('clock', 'period')
    Ts = clock['period']
    print('>> robut period = {}'.format(Ts))
    print('>> test time = {}'.format(T))
     
    log = robut.get_sink('logger', 'log')

    t = log['clock']
    position = log[encoder]
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

def main():

    print('Robut Test Routine')

    k = 1
    position1, position2 \
        = test('{}: MOTOR 1 FORWARD'.format(k), 
               ('motor1','encoder1'),
               'Did the motor spin clockwise for two seconds?', 
               'motor1 not working',
               test_motor_forward)
  
    k += 1
    test('{}: ENCODER 1 FORWARD'.format(k), 
         (position1, position2),
         '',
         '',
         test_encoder)
    
    k += 1
    position1, position2 \
        = test('{}: MOTOR 2 FORWARD'.format(k), 
               ('motor2','encoder2'),
               'Did the motor spin clockwise for two seconds?', 
               'motor1 not working',
               test_motor_forward)
    
    k += 1
    test('{}: ENCODER 2 FORWARD'.format(k), 
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
        = test('{}: MOTOR 1 BACKWARD'.format(k),
               ('motor1','encoder1'),
               'Did the motor spin counter-clockwise for two seconds?', 
               'motor1 not working',
               test_motor_backward)

    k += 1
    test('{}: ENCODER 1 BACKWARD'.format(k), 
         (position2, position1),
         '',
         '',
         test_encoder)

    k += 1
    position1, position2 \
        = test('{}: MOTOR 2 BACKWARD'.format(k),
               ('motor2','encoder2'),
               'Did the motor spin counter-clockwise for two seconds?', 
               'motor1 not working',
               test_motor_backward)
    
    k += 1
    test('{}: ENCODER 2 BACKWARD'.format(k), 
         (position2, position1),
         '',
         '',
         test_encoder)
    
    k += 1
    test('{}: MOTOR 1 TWO SPEEDS'.format(k),
         ('motor1','encoder1'),
         'Did the motor spin at full speed then slowed down to half speed?', 
         'motor1 not working',
         test_motor_speeds)

    k += 1
    test('{}: MOTOR 2 TWO SPEEDS'.format(k),
         ('motor2','encoder2'),
         'Did the motor spin at full speed then slowed down to half speed?', 
         'motor1 not working',
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

    with robut:
        time.sleep(60)
    
    #T = 2
    #identify_motor('motor1', 'encoder1', T)
    #identify_motor('motor2', 'encoder2', T)

    
if __name__ == "__main__":
    main()
