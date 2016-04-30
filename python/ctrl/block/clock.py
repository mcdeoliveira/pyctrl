import warnings
import time

from .. import block

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from ..gettime import gettime as perf_counter
else:
    from time import perf_counter

class Clock(block.Block):

    def __init__(self, period = 0.01, *pars, **kpars):

        self.period = period

        super().__init__(*pars, **kpars)

        self.time_origin = perf_counter()
        self.time = self.time_origin
        self.counter = 0
        
    def set_period(self, period):
        
        self.period = period

    def reset(self):

        # Make sure time is current
        self.read()

        # reset clock and counter
        self.time_origin = self.time
        self.counter = 0

    def get_average_period(self):

        if self.counter:
            return (self.time - self.time_origin) / self.counter
        else:
            return 0

    def calibrate(self, eps = 1/100, N = 100, K = 20):
                
        enabled = self.enabled
        if not enabled:
            warnings.warn('Enabling clock for calibration.')
            self.set_enabled(True)

        print('> Calibrating clock...')
        print('  ITER   TARGET   ACTUAL ACCURACY')

        k = 1
        target = self.period
        while True:

            # reset and run for T seconds
            self.reset()
            for n in range(N):
                self.read()
            period = self.get_average_period()
            
            # estimate actual period
            error = abs(period - target) / target
            print('  {:4}  {:6.5f}  {:6.5f}   {:5.2f}%'
                  .format(k, target, period, 100 * error))

            # counter
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
            self.set_period(self.period + target - period)

        print('< Done!')

        if not enabled:
            warnings.warn('Disabling clock.')
            self.set_enabled(False)

        return (success, period)

    def read(self):

        if self.enabled:

            self.time += self.period
            self.counter += 1

        return (self.time - self.time_origin, )


from threading import Thread, Timer, Condition

class TimerClock(Clock):

    def __init__(self, *pars, **kpars):

        super().__init__(*pars, **kpars)

        self.condition = Condition()
        self.timer = None
        self.running = False

        if self.enabled:
            self.enabled = False
            self.set_enabled(True)
    
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

            # Add to counter
            self.counter += 1

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

        #print('> read')
        if self.enabled:

            # Acquire condition
            self.condition.acquire()
            # wait 
            self.condition.wait()
            # and release
            self.condition.release()
        
        return (self.time - self.time_origin, )
