import warnings
import numpy
import math

import pyctrl
import pyctrl.block.clock as clock
import pyctrl.block.system as system
import pyctrl.block.nl as nl
import pyctrl.system.tf as tf

class Controller(pyctrl.Controller):
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

        # period
        self.period = kwargs.pop('period', 0.01) # deadzone

        # Model parameters
        self.a = kwargs.pop('a', 17)   # 1/s
        self.k = kwargs.pop('k', 0.11) # cycles/s duty
        self.X = kwargs.pop('X', 10)   # deadzone

        # Initialize controller
        super().__init__(*vargs, **kwargs)

    def __reset(self):

        # call super
        super().__reset()

        self.remove_source('clock')
        self.remove_signal('clock')
        
        # add source: clock
        # self.clock = clock.TimerClock(self.period)
        # self.add_source('clock', self.clock, ['clock'])
        # self.signals['clock'] = self.clock.time
        # self.time_origin = self.clock.time_origin
        self.clock = self.add_device('clock',
                                     'pyctrl.block.clock', 'TimerClock',
                                     type = 'source', 
                                     outputs = ['clock'],
                                     enable = True,
                                     period = self.period)
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

        # add signals
        self.add_signals('motor1', 'encoder1', 'pot1', 'input1')

        # add filter: deadzone
        self.add_filter('dz1', nl.DeadZone(X = self.X), 
                        ['motor1'], ['input1'])

        # add filter: model
        Ts = self.period
        c = math.exp(-self.a * Ts)
        self.model3 = system.System(model = \
            tf.DTTF(
                numpy.array((0, (self.k*Ts)*(1-c)/2, (self.k*Ts)*(1-c)/2)), 
                numpy.array((1, -(1 + c), c))))
        self.add_filter('model1', self.model3, 
                        ['input1'], ['encoder1'])

    def start(self):
        self.clock.set_enabled(True)
        super().start()

    def stop(self):
        super().stop()
        self.clock.set_enabled(False)

    # period
    def set_period(self, value):
        self.period = value

    def get_period(self):
        return self.period

if __name__ == "__main__":

    import time
    import pyctrl.sim as sim
    import pyctrl.block as block
    import pyctrl.block.logger as logger

    a = 17   # 1/s
    k = 0.11 # cycles/s duty
    controller = sim.Controller(a = a, k = k)
    controller.add_sink('printer', block.Printer(endln = '\r'), 
                        ['clock', 'motor1', 'input1', 'encoder1'])

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
                          system.Feedback(block = system.Gain(gain = Kp)),
                          ['encoder1', 'reference1'], ['motor1'])
    controller.set_sink('printer', 
                        inputs = ['clock', 'encoder1', 'reference1', 'motor1'])
    print(controller.info('all'))

    with controller:
        time.sleep(1)
        controller.set_signal('reference1', pmax)
        print('\n> REFERENCE = {}'.format(pmax))
        time.sleep(3)
        controller.set_signal('reference1', pmax/2)
        print('\n> REFERENCE = {}'.format(pmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -pmax/2)
        print('\n> REFERENCE = {}'.format(-pmax/2))
        time.sleep(3)

    print('\n> CLOSED LOOP ON POSITION SHOWING VELOCITY')

    controller.add_signal('velocity1')
    controller.add_filter('differentiator1', 
                          system.Differentiator(),
                          ['clock', 'encoder1'], ['velocity1'])
    controller.set_sink('printer', 
                        inputs = ['clock', 'encoder1', 'velocity1', 'reference1', 'motor1'])
    print(controller.info('all'))

    with controller:
        time.sleep(1)
        controller.set_signal('reference1', pmax)
        print('\n> REFERENCE = {}'.format(pmax))
        time.sleep(3)
        controller.set_signal('reference1', pmax/2)
        print('\n> REFERENCE = {}'.format(pmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -pmax/2)
        print('\n> REFERENCE = {}'.format(-pmax/2))
        time.sleep(3)

    print('\n> CLOSED LOOP ON VELOCITY')

    vmax = 11
    Kp = 1/k
    controller.remove_filter('controller1') 
    controller.add_filter('controller1', 
                          system.Feedback(block = system.Gain(gain = Kp)),
                          ['velocity1', 'reference1'], ['motor1'])
    print(controller.info('all'))

    controller.set_signal('reference1', 0)
    with controller:
        time.sleep(1)
        controller.set_signal('reference1', vmax)
        print('\n> REFERENCE = {}'.format(vmax))
        time.sleep(3)
        controller.set_signal('reference1', vmax/2)
        print('\n> REFERENCE = {}'.format(vmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -vmax/2)
        print('\n> REFERENCE = {}'.format(-vmax/2))
        time.sleep(3)

    print('\n> CLOSED LOOP ON VELOCITY WITH INTEGRAL CONTROL')

    Kp = 1/k
    Ki = a/k
    controller.remove_filter('controller1') 
    pi = system.System(model = \
                     tf.PID(Kp = Kp, Ki = Ki, period = controller.period))
    controller.add_filter('controller1', 
                          system.Feedback(block = pi),
                          ['velocity1', 'reference1'], ['motor1'])
    print(controller.info('all'))

    controller.set_signal('reference1', 0)
    with controller:
        time.sleep(1)
        controller.set_signal('reference1', vmax)
        print('\n> REFERENCE = {}'.format(vmax))
        time.sleep(3)
        controller.set_signal('reference1', vmax/2)
        print('\n> REFERENCE = {}'.format(vmax/2))
        time.sleep(3)
        controller.set_signal('reference1', -vmax/2)
        print('\n> REFERENCE = {}'.format(-vmax/2))
        time.sleep(3)

    print()
