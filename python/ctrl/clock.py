import warnings
from threading import Thread, Timer, Condition

from . import block

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from . import gettime
    perf_counter = gettime.gettime
    warnings.warn('Using gettime instead of perf_counter',
                  RuntimeWarning)
else:
    import time
    perf_counter = time.perf_counter

class Clock(block.Block):

    def __init__(self, *pars, **kpars):
        self.period = kpars.pop('period', .01)
        self.condition = Condition()

        super().__init__(*pars, **kpars)

        self.timer = None
        self.running = False

        self.time_origin = perf_counter()
        self.time = self.time_origin
        self.counter = 0
        
        if self.enabled:
            self.enabled = False
            self.set_enabled(True)
    
    def get_average_period(self):
        if self.counter:
            return (self.time - self.time_origin) / self.counter
        else:
            return 0

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

    def reset(self):

        # reset clock
        self.time_origin = self.time
        self.counter = 0

    def read(self):

        #print('> read')
        if self.enabled:

            # Acquire condition
            self.condition.acquire()
            # Wait 
            self.condition.wait()
            # and release
            self.condition.release()
        
        return (self.time - self.time_origin, )

    # def calibrate(self, eps = 0.05, T = 5, K = 20):
        
    #     print('> Calibrating period...')
    #     print('  ITER   TARGET   ACTUAL ACCURACY')

    #     k = 1
    #     est_period = (1 + 2 * eps) * self.period
    #     error = abs(est_period - self.period) / self.period
    #     while error > eps:

    #         # run loop for T seconds
    #         k0 = self.current
    #         t0 = perf_counter()
    #         self.start()
    #         time.sleep(T)
    #         self.stop()
    #         t1 = perf_counter()
    #         k1 = self.current
            
    #         # estimate actual period
    #         est_period = (t1 - t0) / (k1 - k0)
    #         error = abs(est_period - self.period) / self.period
    #         print('  {:4}  {:6.5f}  {:6.5f}   {:5.2f}%'
    #               .format(k, self.period, est_period, 100 * error))
    #         self.delta_period += (est_period - self.period)
            
    #         # counter
    #         k = k + 1
    #         if k > K:
    #             warnings.warn("Could not calibrate to '{}' accuracy".format(eps))
    #             break

    #     print('< ...done.')

