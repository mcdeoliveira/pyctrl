import warnings
from threading import Thread, Timer, Condition
import numpy
import time
import random
import math

from . import algo

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from . import gettime
    perf_counter = gettime.gettime
    warnings.warn('Using gettime instead of perf_counter',
                  RuntimeWarning)
else:
    perf_counter = time.perf_counter

class Controller:

    def __init__(self, period = .01, echo = 0):

        # debug
        self.debug = 0

        # real-time loop
        self.period = period
        self.delta_period = 0.
        self.is_running = False

        # echo
        self.echo = echo
        self.echo_counter = 0

        # data logger
        self.set_logger(60./period)

        # motor1
        self.motor1_on = False
        self.motor1_pwm = 0
        self.motor1_dir = 1

        # motor2
        self.motor2_on = False
        self.motor2_pwm = 0
        self.motor2_dir = 1

        # controller
        self.controller1 = algo.OpenLoop()
        self.controller2 = None
        self.delta_mode = 0

        # references
        self.reference1_mode = 0 # 0 -> software, 1 -> potentiometer
        self.reference1 = 0
        self.reference2_mode = 0 # 0 -> software, 1 -> potentiometer
        self.reference2 = 0

    def __enter__(self):
        if self.debug > 0:
            print('> Starting controller')
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if self.debug > 0:
            print('> Stoping controller')
        self.stop()

    def set_motor1_pwm(self, value = 0):
        if value > 0:
            self.motor1_pwm = value
            self.motor1_dir = 1
        else:
            self.motor1_pwm = -value
            self.motor1_dir = -1

    def set_motor2_pwm(self, value = 0):
        if value > 0:
            self.motor2_pwm = value
            self.motor2_dir = 1
        else:
            self.motor2_pwm = -value
            self.motor2_dir = -1

    def set_delta_mode(self, value = 0):
        self.delta_mode = value

    def calibrate(self, eps = 0.05, T = 5, K = 20):
        
        # save controllers
        controller1 = self.controller1
        controller2 = self.controller2
        echo = self.echo
        
        # remove controllers
        self.controller1 = None
        self.controller2 = None
        self.echo = 0

        print('> Calibrating period...')
        print('  ITER   TARGET   ACTUAL ACCURACY')

        k = 1
        est_period = (1 + 2 * eps) * self.period
        error = abs(est_period - self.period) / self.period
        while error > eps:

            # run loop for T seconds
            k0 = self.current
            t0 = perf_counter()
            self.start()
            time.sleep(T)
            self.stop()
            t1 = perf_counter()
            k1 = self.current
            
            # estimate actual period
            est_period = (t1 - t0) / (k1 - k0)
            error = abs(est_period - self.period) / self.period
            print('  {:4}  {:6.5f}  {:6.5f}   {:5.2f}%'
                  .format(k, self.period, est_period, 100 * error))
            self.delta_period += (est_period - self.period)
            
            # counter
            k = k + 1
            if k > K:
                warnings.warn("Could not calibrate to '{}' accuracy".format(eps))
                break

        print('< ...done.')

        # restore controllers
        self.controller1 = controller1
        self.controller2 = controller2
        self.echo = echo

    def run(self):

        # Run the loop
        encoder1, pot1, encoder2, pot2 = self.read_sensors()
        time_stamp = perf_counter() - self.time_origin

        # Calculate delta T
        if self.delta_mode:
            time_delta = self.period
        else:
            time_delta = time_stamp - self.time_current
            # if abs(time_delta / self.period) > 1.2:
            #     print('time_delta = {}'.format(time_delta))

        # Update reference
        if self.reference1_mode:
            reference1 = 2 * (pot1 - 50)
        else:
            reference1 = self.reference1

        if self.reference2_mode:
            reference2 = 2 * (pot2 - 50)
        else:
            reference2 = self.reference2

        # Call controller
        pwm1 = pwm2 = 0
        if self.controller1 is not None:
            pwm1 = self.controller1.update(encoder1, reference1, time_delta)
            if pwm1 > 0:
                pwm1 = min(pwm1, 100)
            else:
                pwm1 = max(pwm1, -100)
            self.set_motor1_pwm(pwm1)

        if self.controller2 is not None:
            pwm2 = self.controller2.update(encoder2, reference2, time_delta)
            if pwm2 > 0:
                pwm2 = min(pwm2, 100)
            else:
                pwm2 = max(pwm2, -100)
            self.set_motor2_pwm(pwm2)

        # Log data
        self.data[self.current, :] = ( time_stamp,
                                       encoder1, reference1, pwm1,
                                       encoder2, reference2, pwm2 )

        if self.current < self.data.shape[0] - 1:
            # increment current pointer
            self.current += 1
        else:
            # reset current pointer
            self.current = 0
            self.page += 1

        # Echo
        if self.echo:
            coeff, self.echo_counter = divmod(self.echo_counter, self.echo)
            if self.echo_counter == 0:
                print('\r  {0:12.4f}'.format(time_stamp), end='')
                if self.controller1 is not None:
                    if isinstance(self.controller1, algo.VelocityController):
                        print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
                              .format(self.controller1.velocity,
                                      reference1, pwm1),
                              end='')
                    else:
                        print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
                              .format(encoder1, reference1, pwm1),
                              end='')
                if self.controller2 is not None:
                    if isinstance(self.controller2, algo.VelocityController):
                        print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
                              .format(self.controller2.velocity,
                                      reference2, pwm2),
                              end='')
                    else:
                        print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
                              .format(encoder2, reference2, pwm2),
                              end='')
            self.echo_counter += 1

        # Update current time
        self.time_current = time_stamp

    def _release(self):
        # Acquire lock
        self.condition.acquire()
        # Notify lock
        self.condition.notify()
        # Release lock
        self.condition.release()

    def _run(self):
        # Loop
        self.is_running = True
        self.condition = Condition()
        self.time_current = perf_counter() - self.time_origin
        while self.is_running:

            # Acquire condition
            self.condition.acquire()

            # Setup timer
            timer = Timer(self.period - self.delta_period, self._release)
            timer.start()

            # Call run
            self.run()

            # Wait 
            self.condition.wait()
            
            # and release
            self.condition.release()
                            
    def read_sensors(self):
        # Randomly generate sensor outputs
        return (random.randint(0,65355)/653.55,
                random.randint(0,65355)/65.355,
                random.randint(0,65355)/653.55,
                random.randint(0,65355)/65.355)

    def set_encoder1(self, value):
        pass

    def set_encoder2(self, value):
        pass

    # "public"

    def set_controller1(self, algorithm = None):
        self.controller1 = algorithm
        self.set_reference1(0)

    def set_controller2(self, algorithm = None):
        self.controller2 = algorithm
        self.set_reference2(0)

    def set_reference1(self, value = 0):
        self.reference1 = value

    def set_reference2(self, value = 0):
        self.reference2 = value

    def set_reference1_mode(self, value = 0):
        self.reference1_mode = value

    def set_reference2_mode(self, value = 0):
        self.reference2_mode = value

    def set_echo(self, value):
        self.echo = int(value)

    def set_period(self, value = 0.1):
        self.period = value

    # TODO: Complete get methods
    # TODO: Test Controller

    def get_echo(self):
        return self.echo

    def get_period(self):
        return self.period

    def set_logger(self, duration):
        self.data = numpy.zeros((math.ceil(duration/self.period), 7), float)
        self.reset_logger()

    def reset_logger(self):
        self.page = 0
        self.current = 0
        self.time_origin = perf_counter()
        self.time_current = 0 

    def get_log(self):
        if self.page == 0:
            return self.data[:self.current,:]
        else:
            return numpy.vstack((self.data[self.current:,:],
                                 self.data[:self.current,:]))

    def get_sample_number(self):
        return self.page * self.data.shape[0] + self.current
            
    def start(self):
        """Start controller loop"""
        # Heading
        if self.echo:
            print('          TIME', end='')
            if self.controller1 is not None:
                if isinstance(self.controller1, algo.VelocityController):
                    print('       VEL1   REF1   PWM1', end='')
                else:
                    print('       ENC1   REF1   PWM1', end='')
            if self.controller2 is not None:
                if isinstance(self.controller2, algo.VelocityController):
                    print('       VEL1   REF1   PWM1', end='')
                else:
                    print('       ENC1   REF1   PWM1', end='')
            if self.controller2 is not None:
                if isinstance(self.controller2, algo.VelocityController):
                    print('       VEL2   REF2   PWM2', end='')
                else:
                    print('       ENC2   REF2   PWM2', end='')
            print('')

        # Start thread
        self.thread = Thread(target = self._run)
        self.thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            # Release condition lock
            self._release()
        if self.echo:
            print('')
