import time
import math
import numpy
import platform, sys

def test(k, args, query_msg, failed_msg, test_function):
    print('> TEST #{}'.format(k))
    passed, retval = test_function(args)
    if not passed:
        print("> Failed test #{}: {}".format(k, retval))
        sys.exit(2)
    if query_msg:
        answer = input('< ' + query_msg + ' [Y/n]').lower()
        if 'n' in answer:
            print("> Failed test #{}: {}".format(k, failed_msg))
            sys.exit(2)
    return retval

def test_motor_forward(args):

    with controller:
        position1 = controller.get_encoder1()
        controller.set_reference1(100)
        time.sleep(2)
        position2 = controller.get_encoder1()
    return True, (position1, position2)

def test_encoder(args):

    position1, position2 = args[0], args[1]
    if position2 == position1:
        return (False, 'encoder1 not working')
    elif position2 < position1:
        return (False, 'encoder1 reading reversed')
    return (True, [])

def test_motor_backward(args):

    with controller:
        position1 = controller.get_encoder1()
        controller.set_reference1(-100)
        time.sleep(2)
        position2 = controller.get_encoder1()
    return True, (position1, position2)

def test_motor_speeds(args):

    with controller:
        controller.set_reference1(100)
        time.sleep(1)
        controller.set_reference1(50)
        time.sleep(2)
    return (True, [])

def test_reset_encoder(args):

    with controller:
        controller.set_reference1(0)
        time.sleep(10*controller.period) # sleep to make sure it is stoped
        position1 = controller.get_encoder1()
        controller.set_encoder1(0)
        time.sleep(10*controller.period) # sleep to make sure it did not move
        position2 = controller.get_encoder1()

    if position2 != 0:
        return (False, 'could not reset encoder1')
    return (True, [position1, position2])

def main():

    # Are we on the beaglebone?
    if 'bone' in platform.uname()[2]:
        from ctrl.bbb import Controller
        import Adafruit_BBIO.ADC as ADC
        simulated = False
    else:
        from ctrl.sim import Controller
        simulated = True

    global controller
    controller = Controller()

    if simulated:

        Ts = 0.01              # s
        a = 17                 # 1/s
        k = 0.11               # cycles/s duty
        c = math.exp(-a * Ts)  # adimensional

        controller.set_period(Ts)
        controller.set_model1( numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                               numpy.array((1, -(1 + c), c)),
                               numpy.array((0,0)) )

        # controller.calibrate()

    controller.set_echo(1)
    controller.set_logger(2)

    print('Controller Test Routine')

    k = 1
    position1, position2 \
        = test(k, (),
               'Did the motor spin clockwise for two seconds?', 
               'motor1 not working',
               test_motor_forward)
  
    k += 1
    test(k, (position1, position2),
         '',
         '',
         test_encoder)

    k += 1
    position1, position2 \
        = test(k, (),
               'Did the motor spin counter-clockwise for two seconds?', 
               'motor1 not working',
               test_motor_backward)

    k += 1
    test(k, (position2, position1),
         '',
         '',
         test_encoder)

    k += 1
    test(k, (),
         'Did the motor spin at full speed then slowed down to half speed?', 
         'motor1 not working',
         test_motor_speeds)

    k += 1
    position1, position2 \
        = test(k, (),
               '', 
               '',
               test_reset_encoder)

    # Identify motor
    print('> Identifying motor parameters...')
    with controller:
        controller.set_reference1(0)
        controller.set_encoder1(0)
        controller.set_logger(10)
        time.sleep(1)
        controller.set_reference1(100)
        time.sleep(5)
        
        Ts = controller.get_period()
        log = controller.get_log()
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
        
    if False:

        if not simulated:

            # Calibrate potentiometer
            k += 1
            print("> Set the potentiometer to the minimum position\n") 
            time.sleep(5)
            pot_min = min(100, 100 * ADC.read("AIN0") / 0.88)
            print(pot_min)
            print("\n> Set the potentiometer to the maximum position\n") 
            time.sleep(5)
            pot_max = min(100, 100 * ADC.read("AIN0") / 0.88)
            print(pot_max)
            pot_zero = (pot_min + pot_max)/2
            print("\> pot_zero = {}".format(pot_zero))
            for i in range(1,100):
                p = min(100, 100 * ADC.read("AIN0") / 0.88)
                print(p)
                time.sleep(0.2)

    
if __name__ == "__main__":
    main()
