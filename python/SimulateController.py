from threading import Timer
import random
import numpy
import math
import SISOLTISystem as siso
from Controller import Controller

class SimulateController(Controller):

    def __init__(self, *pars, **kpars):

        super().__init__(*pars, **kpars)

        # Set model 1
        self.model1 = siso.SISOLTISystem(self.period)
        self.input1_range = 1;
        self.output1_range = 1;

        # Set model 2
        self.model2 = siso.SISOLTISystem(self.period)
        self.input2_range = 1;
        self.output2_range = 1;

        # Timer thread
        self.timer = None
        self.timer_is_running = False

    def timer_start(self):
        if not self.timer_is_running:
            self.timer = Timer(self.period, self.timer_run)
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

    def set_input1_range(self, value = 1):
        self.input1_range = value;

    def set_output1_range(self, value = 65535):
        self.output1_range = value;

    def set_input2_range(self, value = 1):
        self.input2_range = value;

    def set_output2_range(self, value = 65535):
        self.output2_range = value;
        
    def read_sensors(self):

        # Read current inputs
        uk1 = self.input1_range * self.motor1_dir * self.motor1_pwm
        uk2 = self.input2_range * self.motor2_dir * self.motor2_pwm

        # Read current outputs
        yk1 = self.model1.update(uk1)
        yk2 = self.model2.update(uk2)

        # Read potentiometers
        pot1 = 0
        pot2 = 0

        # Return outputs
        return (int(self.output1_range * yk1), pot1,
                int(self.output2_range * yk2), pot2)


if __name__ == "__main__":

    import time
    from ControlAlgorithm import *
    
    controller = SimulateController()

    # Motor produces 9800 RPM @ 100% duty
    #
    # Model is
    #
    # .                    .
    # w + a w = b u,   w = x
    #
    # Units are:
    #   x = counts
    #   w = counts/s
    #
    # Conversions:
    #   360 degree = 48*9.68 counts
    #     1 degree = 48*9.68/360 counts = 1.2907 counts
    #
    #   1 RPM      = 360 degrees / 60 s = 6 degrees/s
    #              = 6*1.2907 counts/s  = 7.7440 counts/s
    #
    # a = 1/tau = 1/0.1 = 10 (1/s)
    # b/a = w/u = 9800 RPM / 100 duty = 98 * 7.740 counts/s/duty
    #                                 = 758.9 counts/s/duty
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
    a = 10                 # 1/s
    k = 758.9              # counts/s duty
    c = math.exp(-a * Ts)  # adimensional
        
    controller.set_period(Ts)
    controller.set_model1( numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                           numpy.array((1, -(1 + c), c)),
                           numpy.array((0,0)) )

    controller.set_input1_range(1)
    controller.set_output1_range(1)
    controller.set_echo(.1/Ts)

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

    reference = 2 * 360 * 1.2907
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

    reference = 5000 * 7.7440
    controller.set_controller1(
        VelocityController(ProportionalController(1 / k, reference / 100))
    )

    print('> CLOSED LOOP ON VELOCITY')
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
        VelocityController(PIDController(1 / k, 0.03, 0, reference / 100))
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

    print('page = {}\tcurrent = {}'.format(controller.page, controller.current))
    print('data = {}'.format(controller.data))
    print('log = {}'.format(controller.get_log()))
