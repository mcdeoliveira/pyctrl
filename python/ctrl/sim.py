from threading import Timer
import warnings
import numpy
import time

from . import lti
import ctrl

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from . import gettime
    perf_counter = gettime.gettime
    warnings.warn('Using gettime instead of perf_counter',
                  RuntimeWarning)
else:
    perf_counter = time.perf_counter

class Controller(ctrl.Controller):

    def __init__(self, *pars, **kpars):

        super().__init__(*pars, **kpars)

        # Set model 1
        self.model1 = lti.SISOLTISystem(self.period)

        # Set model 2
        self.model2 = lti.SISOLTISystem(self.period)

        # Timer thread
        self.timer = None
        self.timer_is_running = False

        # Set delta mode to 1: delta T = period
        self.delta_period = 0
        self.set_delta_mode(1)

    def timer_start(self):
        if not self.timer_is_running:
            self.timer = Timer(self.period - self.delta_period, 
                               self.timer_run)
            self.timer.start()
            self.timer_is_running = True

    def timer_run(self):
        # Initiate timer thread
        self.timer_is_running = False
        self.timer_start()

        # Call run
        super().run()

    def stop(self):
        self.timer_is_running = False
        self.timer.cancel()

        # Call stop
        super().stop()

    def run(self):
        # hijack control to timer
        self.timer_start()

        # and return
        self.is_running = False

    def set_period(self, value = 0.1):
        super().set_period(value)
        self.model1.set_period(value)
        self.model2.set_period(value)

    def set_model1(self, 
                   num = numpy.array((1,)),
                   den = numpy.array((1,)),
                   state = None ):
        self.model1.set_model(self.period, num, den, state)

    def set_model2(self, 
                   num = numpy.array((1,)),
                   den = numpy.array((1,)),
                   state = None ):
        self.model2.set_model(self.period, num, den, state)

    def read_sensors(self):

        # Read current inputs
        uk1 = self.motor1_dir * self.motor1_pwm
        uk2 = self.motor2_dir * self.motor2_pwm

        # Read current outputs
        self.encoder1 = float(self.model1.update(uk1))
        self.encoder2 = float(self.model2.update(uk2))

        # Read potentiometers
        self.pot1 = 0
        self.pot2 = 0

        # Return outputs
        return (self.encoder1, self.pot1, self.encoder2, self.pot2)

    def set_encoder1(self, value):
        self.model1.set_position(value)
        super().set_encoder1(value)

    def set_encoder2(self, value):
        self.model2.set_position(value)
        super().set_encoder2(value)

if __name__ == "__main__":

    import time
    from Algorithms import *
    
    controller = Controller()

    # Motor produces 9800 RPM @ 100% duty
    #
    # Model is
    #
    # .                    .
    # w + a w = b u,   w = x
    #
    # Units are:
    #   x = cycles
    #   w = cycles/s
    #
    # Conversions:
    #   1 RPM      = 1 cycle / 60 s = 1/60 cycles/s
    #
    # a = 1/tau = 1/0.1 = 10 (1/s)
    # b/a = w/u = 9800 RPM / 100 duty = 98 /60 cycles/s/duty
    #                                 = 1.63 cycles/s/duty
    #             a
    # G(s) = k -------, k = b/a
    #           s + a
    #
    # Zero-order hold equivalent (Ts < pi/a = 0.3):
    #
    #                            -1      
    #           1 - c           z  (1 - c)        -a Ts
    # G(z) = k ----------- = k ------------, c = e
    #           z - c                -1
    #                           1 - z  c
    #
    #                                     Ts  
    # x[k] = int_{t-Ts}^t w dt = x[k-1] + --- ( w[k] + w[k-1] )
    #                                      2
    #                  -1
    #        Ts   1 + z  
    # H(z) = --- ---------
    #         2        -1
    #             1 - z
    #                            -1           -2
    #                     k Ts   z  (1 - c) + z  (1 - c)
    # T(z) = H(z) G(z) = ----- -------------------------
    #                      2         -1            -2
    #                           1 - z   (1 + c) + z  c
    
    Ts = 0.01              # s
    a = 17                 # 1/s
    k = 1.63               # cycles/s duty
    c = math.exp(-a * Ts)  # adimensional
        
    controller.set_period(Ts)
    controller.set_model1( numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                           numpy.array((1, -(1 + c), c)),
                           numpy.array((0,0)) )

    controller.set_echo(.1/Ts)
    controller.calibrate()
    controller.set_delta_mode(0)

    print('> OPEN LOOP')
    controller.start()
    time.sleep(1)
    controller.set_reference1(100)
    time.sleep(1)
    controller.set_reference1(-100)
    time.sleep(1)
    controller.set_reference1(0)
    time.sleep(1)
    controller.stop()
    
    reference = 2
    controller.set_controller1(
        ProportionalController(0.09 / (k*Ts), reference / 100)
    )
    
    print('> CLOSED LOOP ON POSITION')
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

    reference = 2000 / 60

    controller.set_controller1(
        VelocityController(ProportionalController(5 / k, reference / 100))
    )

    print('> CLOSED LOOP ON VELOCITY')
    #controller.set_reference1(0)
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

    controller.set_controller1(
        VelocityController(PIDController(1 / k, a / k, 0, reference / 100))
    )

    print('> CLOSED LOOP ON VELOCITY INTEGRAL')
    controller.set_logger(20*controller.period)
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

    # print('page = {}\tcurrent = {}'.format(controller.page, controller.current))
    # print('data = {}'.format(controller.data))
    # print('log = {}'.format(controller.get_log()))
