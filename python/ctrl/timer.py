import warnings
import numpy
import math

import ctrl
import ctrl.block.clock as clock

class Controller(ctrl.Controller):
    """
    Controller() implements a controller with a TimerClock.

    The clock is enabled and disabled automatically when calling
    `start()` and `stop()`.

    :param period: the clock period (default 0.01)
    """

    def __init__(self, **kwargs):

        # period
        self.period = kwargs.pop('period', 0.01)

        # Initialize controller
        super().__init__(**kwargs)

    def __reset(self):

        # call super
        super().__reset()

        # add source: clock
        self.clock = self.add_device('clock',
                                     'ctrl.block.clock', 'TimerClock',
                                     type = 'source', 
                                     outputs = ['clock'],
                                     enable = True,
                                     period = self.period)
        self.signals['clock'] = self.clock.time
