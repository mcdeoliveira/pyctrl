import time
import math
import numpy
import platform, sys, select

from ctrl.client import Controller
import ctrl.block as block
import ctrl.block.logger as logger

# initialize controller
HOST, PORT = "192.168.10.105", 9999
controller = Controller(host = HOST, port = PORT)
controller.add_sink('logger', 
                    logger.Logger(), 
                    ['clock','encoder1'])
controller.add_sink('printer', block.Printer(endln = '\r'), 
                    ['clock', 'motor1', 'encoder1'])
    
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

    with controller:
        position1 = controller.get_signal('encoder1')
        controller.set_signal('motor1',100)
        time.sleep(2)
        position2 = controller.get_signal('encoder1')
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
    controller.set_signal('motor1',0)
    with controller:
        time.sleep(.1)
    t2 = controller.get_signal('clock')
    if t2 > t1:
        return False, 'clock did not reset ({} > {})'.format(t2,t1)
    return True, []

def test_motor_backward(args):

    with controller:
        controller.set_source('clock', reset = True)
        position1 = controller.get_signal('encoder1')
        controller.set_signal('motor1',-100)
        time.sleep(2)
        position2 = controller.get_signal('encoder1')
    return True, (position1, position2)

def test_motor_speeds(args):

    with controller:
        controller.set_source('clock', reset = True)
        controller.set_signal('motor1',100)
        time.sleep(1)
        controller.set_signal('motor1',50)
        time.sleep(1)
    return True, []

def test_reset_encoder(args):

    with controller:
        controller.set_signal('motor1',0)
        time.sleep(.1) # sleep to make sure it is stoped
        position1 = controller.get_signal('encoder1')
        controller.set_source('encoder1', reset = True)
        time.sleep(.1) # sleep to make sure it did not move
        position2 = controller.get_signal('encoder1')

    if position2 != 0:
        return False, 'could not reset encoder1 ({} != 0)'.format(position2)
    return True, [position1, position2]

def test_potentiometer(args):
    
    # Calibrate potentiometer
    KMAX = 600 
    TOL = 2
    #controller.get_source('pot1', ['full_scale', 'invert'])
    controller.set_source('pot1', full_scale = 1, invert = False)
    inverted = False
    full_scale = 100
    print("> Set the potentiometer to the minimum position and hit <ENTER>") 
    k = 0
    while k < KMAX:
        pot_min, = controller.read_source('pot1')
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
        pot_max, = controller.read_source('pot1')
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

def main():

    print('Controller Test Routine')

    k = 1
    position1, position2 \
        = test('{}: MOTOR FORWARD'.format(k), (),
               'Did the motor spin clockwise for two seconds?', 
               'motor1 not working',
               test_motor_forward)
  
    k += 1
    test('{}: ENCODER FORWARD'.format(k), (position1, position2),
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
        = test('{}: MOTOR BACKWARD'.format(k), (),
               'Did the motor spin counter-clockwise for two seconds?', 
               'motor1 not working',
               test_motor_backward)

    k += 1
    test('{}: ENCODER BACKWARD'.format(k), (position2, position1),
         '',
         '',
         test_encoder)

    k += 1
    test('{}: MOTOR TWO SPEEDS'.format(k), (),
         'Did the motor spin at full speed then slowed down to half speed?', 
         'motor1 not working',
         test_motor_speeds)

    k += 1
    position1, position2 \
        = test('{}: ENCODER RESET'.format(k), (),
               '', 
               '',
               test_reset_encoder)
        
    
        
    if 'pot1' in controller.list_sources():
        k += 1
        position1, position2 \
            = test('{}: POTENTIOMETER RANGE'.format(k), (),
                   '', 
                   '',
                   test_potentiometer)

    # Identify motor
    print('> Identifying motor parameters...')
    with controller:
        controller.set_signal('motor1',0)
        controller.set_source('encoder1', reset = True)

        controller.set_sink('logger', reset = True)
        controller.set_source('clock', reset = True)
        time.sleep(1)
        controller.set_signal('motor1',100)
        time.sleep(5)
        
        Ts = controller.get_source('clock', 'period')
        print('> period = {}'.format(Ts))

        log = controller.read_sink('logger')
        t = log[:,0]
        position = log[:,1]
        velocity = numpy.zeros(t.shape, float)
        velocity[1:] = (position[1:]-position[:-1])/(t[1:]-t[:-1])
        
        #print('>> max  = {}'.format(max_velocity))
        max_velocity = numpy.max(velocity)
        ind = numpy.argwhere(velocity > .5*max_velocity)[0]
        
        #print('ind = {}'.format(ind))
        ind += int(2/Ts)
        #print('>> len = {}'.format(len(velocity)))
        #print('>> ind = {}'.format(ind))
        k = numpy.mean(velocity[ind:])
        print('\n> gain      = {:5.3f}'.format(k))
        
        ind = numpy.argwhere( (velocity > 0.1*k ) & 
                              (velocity < 0.9*k ) )
        t10 = float(t[ind[0]])
        t90 = float(t[ind[-1]])
        tau = (t90 - t10) / 2.2
        print('> rise time = {:5.3f}'.format(t90 - t10))
        print('> lambda    = {:5.3f}'.format(1/tau))
        
    
if __name__ == "__main__":
    main()
