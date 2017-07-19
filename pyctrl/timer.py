import pyctrl
import pyctrl.block.clock as clock

class Controller(pyctrl.Controller):
    """
    :py:class:`pyctrl.timer.Controller` implements a controller 
    with a :py:class:`pyctrl.block.clock.TimerClock`.

    The clock is enabled and disabled automatically when calling
    `start()` and `stop()`.

    :param period: the clock period (default 0.01)
    """

    def __init__(self, **kwargs):

        # period
        self.period = kwargs.pop('period', 0.01)

        # discard argument 'noclock'
        kwargs.pop('noclock', None)
       
        # Initialize controller
        super().__init__(noclock = True, **kwargs)

    def _reset(self):

        # call super
        super()._reset()

        # add signal clock
        self.add_signal('clock')
        
        # add device clock
        self.add_source('clock',
                        ('pyctrl.block.clock', 'TimerClock'),
                        ['clock'],
                        enable = True,
                        kwargs = {'period': self.period})
        
        # reset clock
        self.set_source('clock', reset=True)
