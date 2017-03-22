import warnings
import time

from .. import block

# alternative perf_counter
import sys
from time import perf_counter

class Clock(block.Block):
    """
    `Clock` provides a basic clock that writes the current time to its
    output.
    """
    def __init__(self, **kwargs):

        #print("Clock.__init__: pars {}".format(pars))
        #print("Clock.__init__: kwargs {}".format(kwargs))
        
        super().__init__(**kwargs)

        self.time_origin = perf_counter()
        self.time = self.time_origin
        self.count = 0
        self.average_period = 0
        
    def set_period(self, period):
        """
        Set `Clock` period.

        :param float period: clock period
        :raise: `BlockExcpetion` if not supported
        """
        raise BlockException('Clock does not have a period')

    def get_period(self):
        """
        Get `Clock` period.

        :return: clock period
        :retype: float
        :raise: `BlockExcpetion` if not supported
        """
        raise BlockException('Clock does not have a period')

    def reset(self):
        """
        Reset `Clock` by setting the origin of time to the present time
        and the clock count to zero.
        """

        # Make sure time is current
        self.read()

        # reset clock and count
        self.time_origin = self.time
        self.count = 0

    def get(self, keys = None, exclude = ()):
        """
        Get properties of `Clock`. 

        Available properties are:

        1. `average_period`
        2. `time_origin`
        3. `count`

        The elapsed time since initialization or last reset can be
        obtained using the method `read()`

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        """

        if keys is None or 'average_period' in keys:
            self.calculate_average_period()

        # call super excluding time and last
        return super().get(keys, exclude = exclude)
        
    def read(self):
        """
        Read from `Clock`.

        :return: tuple with elapsed time since initialization or last reset
        """

        if self.enabled:

            self.time = perf_counter()
            self.count += 1

        return (self.time - self.time_origin, )

    
    def calculate_average_period(self):
        """
        Calculate the average period since the clock was initialized
        or reset.
        
        :return: average period
        :retype: float
        """
        if self.count:
            self.average_period = (self.time - self.time_origin) / self.count
        else:
            self.average_period = 0
            
        return self.average_period

    def calibrate(self, eps = 1/100, N = 100, K = 20):
        """
        Calibration routine that attempts to callibrate clock
        by fine tuning the `clock`'s period.

        `Clock` must support `get_period()` and `set_period()` must
        be able to accept arbitrary floats.
        """
        enabled = self.enabled
        if not enabled:
            warnings.warn('Enabling clock for calibration.')
            self.set_enabled(True)

        print('> Calibrating clock...')
        print('  ITER   TARGET   ACTUAL ACCURACY')

        k = 1
        target = self.get_period()
        while True:

            # reset and run for T seconds
            self.reset()
            for n in range(N):
                self.read()
            period = self.calculate_average_period()
            
            # estimate actual period
            error = abs(period - target) / target
            print('  {:4}  {:6.5f}  {:6.5f}   {:5.2f}%'
                  .format(k, target, period, 100 * error))

            # count
            k = k + 1

            # Success?
            if error < eps:
                # success!
                success = True
                break

            elif k > K:
                warnings.warn("Could not calibrate to '{}' accuracy".format(eps))
                success = False
                break

            # compensate error
            self.set_period(self.get_period() + target - period)

        print('< Done!')

        if not enabled:
            warnings.warn('Disabling clock.')
            self.set_enabled(False)

        return (success, period)



from threading import Thread, Timer, Condition

class TimerClock(Clock):
    """
    `TimerClock` provides a clock that reads the current time
    periodically.

    :param float period: period in seconds
    """
    
    def __init__(self, **kwargs):

        self.period = kwargs.pop('period', 0.01)
        
        super().__init__(**kwargs)

        self.condition = Condition()
        self.timer = None
        self.running = False

        if self.enabled:
            self.enabled = False
            self.set_enabled(True)
    
    def set_period(self, period):
        """
        Set `TimerClock` period.

        :param float period: clock period
        """
        self.period = period

    def get_period(self):
        """
        Get `TimerClock` period.

        :return: clock period
        :retype: float
        """
        return self.period
        
    def get(self, keys = None, exclude = ()):
        """
        Get properties of `TimerClock`. 

        Available properties those from :py:meth:`ctrl.block.clock.Clock.get` and:

        1. `period`

        The elapsed time since initialization or last reset can be
        obtained using the method `read()`

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        """
        
        # call super excluding time and last
        return super().get(keys, exclude + ('condition', 'timer', 'running',
                                            'thread') )
    
    def tick(self):

        # Acquire lock
        self.condition.acquire()

        # Get time
        t = perf_counter()
        dt = t - self.time

        if dt < .9 * self.period and self.running and self.enabled:

            # reload timer
            #self.timer = Timer(self.period - dt, self.tick)
            #self.timer.start()

            #print('would reload {}'.format(dt))
            pass

        else:

            # Got a tick
            self.time = t

            # Add to count
            self.count += 1

            #print('> tick {}'.format(self.time))

            # Notify lock
            self.condition.notify_all()

        # Release lock
        self.condition.release()

    def run(self):

        #print('> run')
        self.running = True
        while self.enabled and self.running:

            # Acquire condition
            self.condition.acquire()

            # Setup timer
            self.timer = Timer(self.period, self.tick)
            self.timer.start()

            # Wait 
            self.condition.wait()

            # and release
            self.condition.release()

        self.running = False
        #print('> Disabled!')

    def set_enabled(self, enabled = True):
        """
        Set `TimerClock` *enabled* state.

        :param enabled: True or False (default True)
        """

        # quick return
        if enabled == self.enabled:
            return

        # enable
        if enabled:
            
            #print('> Enabling clock')
            
            # set enabled
            super().set_enabled(enabled)

            # Start thread
            self.thread = Thread(target = self.run)
            self.thread.start()

        # disable
        else:
        
            # Acquire condition
            self.condition.acquire()

            #print('> Will disable')

            # Prepare to stop
            self.running = False
            
            # Notify lock
            self.condition.notify_all()

            # set enabled
            super().set_enabled(enabled)

            # and release
            self.condition.release()

    def read(self):
        """
        Read from `TimerClock`.

        :return: tuple with elapsed time since initialization or last reset
        """

        #print('> read')
        if self.enabled:

            # Acquire condition
            self.condition.acquire()
            # wait 
            self.condition.wait()
            # and release
            self.condition.release()
        
        return (self.time - self.time_origin, )
