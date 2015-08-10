import warnings
import numpy
import math

if __name__ == "__main__":

    import sys
    sys.path.append('.')

import ctrl
import ctrl.linear as linear
import ctrl.clock as clock

class Controller(ctrl.Controller):
    """Controller(a, k) implements a simulated controlled.

    It adds a *clock* source and the signals *motor1* and *encoder1*.

    Default model is that of a second order system which could be used
    to model, for instance, a motor:

      .                    .
      w + a w = b u,   w = x

    Units are:

      x = cycles
      w = cycles/s (Hz)

    Default parameters are:

      a = 1/tau = 17 (1/s)
      k = b/a   = 11 Hz / 100 duty = 0.11 cycles/s/duty

    Transfer-function (continuous):

             W(s)       a
      G(s) = ---- = k ------, k = b/a
             U(s)     s + a

    Zero-order hold equivalent (Ts < pi/a = 0.3):

                                 -1      
                1 - c           z  (1 - c)        -a Ts
      G(z) = k ----------- = k ------------, c = e
                z - c                -1
                                1 - z  c

    Transfer-function (continuous):

              X(s)     1
      H(s) = ------ = ---
              W(s)     s

    Zero-order hold equivalent:

                       -1
             Ts   1 + z  
      H(z) = --- ---------
              2        -1
                  1 - z

    Complete discrete model is:

                                 -1           -2
                          k Ts   z  (1 - c) + z  (1 - c)
      T(z) = H(z) G(z) = ----- -------------------------
                           2         -1            -2
                                1 - z   (1 + c) + z  c

    """

    def __init__(self, *vargs, **kwargs):

        # Model parameters
        a = kwargs.pop('a', 17)   # 1/s
        k = kwargs.pop('k', 0.11) # cycles/s duty

        # Initialize controller
        super().__init__(*vargs, **kwargs)
        
        Ts = self.period
        c = math.exp(-a * Ts)  # adimensional

        # add source: clock
        self.clock = clock.Clock(self.period)
        self.add_source('clock', self.clock, ['clock'])
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

        # add signals
        self.add_signals('motor1', 'encoder1', 'pot1')

        # add filter: model
        self.model3 = linear.TransferFunction(model = \
                linear.TFModel(
                    numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                    numpy.array((1, -(1 + c), c))))
        self.add_filter('model1', self.model3, 
                        ['motor1'], ['encoder1'])

    def start(self):
        self.clock.set_enabled(True)
        super().start()

    def stop(self):
        super().stop()
        self.clock.set_enabled(False)

if __name__ == "__main__":

    import ctrl.sim as sim
    import ctrl.block as block
    import ctrl.logger as logger
    import time

    a = 17   # 1/s
    k = 0.11 # cycles/s duty
    controller = sim.Controller(a = a, k = k)
    controller.add_sink('printer', block.Printer(endln = '\r'), 
                        ['clock', 'motor1', 'encoder1'])

    print(controller.info('all'))

    logger = logger.Logger()
    controller.add_sink('logger', logger, ['clock','encoder1'])

    print('> IDLE')
    with controller:
        time.sleep(1)

    log = controller.read_sink('logger')
    print('\n> LOG HAS {} ROWS and {} COLUMNS'.format(log.shape[0], log.shape[1]))

    controller.remove_sink('logger')

    print('\n> OPEN LOOP')

    with controller:
        time.sleep(1)
        controller.set_signal('motor1', 100)
        time.sleep(1)
        controller.set_signal('motor1', -100)
        time.sleep(1)
        controller.set_signal('motor1', 0)
        time.sleep(1)

    print('\n> CLOSED LOOP ON POSITION')

    pmax = 2
    Kp = 10/k

    controller.add_signal('reference1')
    controller.add_filter('controller1', 
                          linear.Feedback(gamma = pmax,
                                         block = linear.Gain(gain = Kp)),
                          ['encoder1', 'reference1'], ['motor1'])
    controller.set_sink('printer', 'inputs',
                        ['clock', 'encoder1', 'reference1', 'motor1'])
    print(controller.info('all'))

    with controller:
        time.sleep(1)
        controller.set_signal('reference1', 100)
        print('\n> REFERENCE = {}'.format(pmax))
        time.sleep(3)
        controller.set_signal('reference1', 50)
        print('\n> REFERENCE = {}'.format(pmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -50)
        print('\n> REFERENCE = {}'.format(-pmax/2))
        time.sleep(3)

    print('\n> CLOSED LOOP ON POSITION SHOWING VELOCITY')

    controller.add_signal('velocity1')
    controller.add_filter('differentiator1', 
                          linear.Differentiator(),
                          ['clock', 'encoder1'], ['velocity1'])
    controller.set_sink('printer', 'inputs',
                        ['clock', 'encoder1', 'velocity1', 'reference1', 'motor1'])
    print(controller.info('all'))

    with controller:
        time.sleep(1)
        controller.set_signal('reference1', 100)
        print('\n> REFERENCE = {}'.format(pmax))
        time.sleep(3)
        controller.set_signal('reference1', 50)
        print('\n> REFERENCE = {}'.format(pmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -50)
        print('\n> REFERENCE = {}'.format(-pmax/2))
        time.sleep(3)

    print('\n> CLOSED LOOP ON VELOCITY')

    vmax = 11
    Kp = 1/k
    controller.remove_filter('controller1') 
    controller.add_filter('controller1', 
                          linear.Feedback(gamma = vmax,
                                         block = linear.Gain(gain = Kp)),
                          ['velocity1', 'reference1'], ['motor1'])
    print(controller.info('all'))

    controller.set_signal('reference1', 0)
    with controller:
        time.sleep(1)
        controller.set_signal('reference1', 100)
        print('\n> REFERENCE = {}'.format(vmax))
        time.sleep(3)
        controller.set_signal('reference1', 50)
        print('\n> REFERENCE = {}'.format(vmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -50)
        print('\n> REFERENCE = {}'.format(-vmax/2))
        time.sleep(3)

    print('\n> CLOSED LOOP ON VELOCITY WITH INTEGRAL CONTROL')

    Kp = 1/k
    Ki = a/k
    controller.remove_filter('controller1') 
    pi = linear.TransferFunction(model = \
                                 linear.PID(Kp = Kp, Ki = Ki, period = controller.period))
    controller.add_filter('controller1', 
                          linear.Feedback(gamma = vmax, block = pi),
                          ['velocity1', 'reference1'], ['motor1'])
    print(controller.info('all'))

    controller.set_signal('reference1', 0)
    with controller:
        time.sleep(1)
        controller.set_signal('reference1', 100)
        print('\n> REFERENCE = {}'.format(vmax))
        time.sleep(3)
        controller.set_signal('reference1', 50)
        print('\n> REFERENCE = {}'.format(vmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -50)
        print('\n> REFERENCE = {}'.format(-vmax/2))
        time.sleep(3)

    print()
