import time

import rcpy
import pyctrl

class Controller(pyctrl.Controller):
    """
    :bases: :py:class:`pyctrl.Controller`

    :py:class:`pyctrl.rc.Controller` initializes a controller for the Robotics Cape equiped with a clock based on the MPU9250 periodic interrupts.

    :param float period: period in seconds (default 0.01)
    :param kwargs: other keyword parameters
    """
    def __init__(self, **kwargs):

        # period (default 100Hz)
        self.period = kwargs.pop('period', 0.01)

        # Initialize controller
        super().__init__(noclock = True, **kwargs)

        # set state as RUNNING
        rcpy.run()

        # register cleanup function
        # rcpy.add_cleanup(rcpy.exit, ())

    def __reset(self):

        # call super
        super().__reset()
      
        # print("pyctrl.rc.__reset: PERIOD = {}".format(self.period))
        
        # add device clock
        self.add_device('clock',
                        'pyctrl.rc.mpu9250', 'MPU9250',
                        type = 'source',
                        outputs = ['clock'],
                        period = self.period)

        # set clock period: it will be ignored at the construction time
        # because MPU9250 is a singleton
        # self.set_source('clock', period = self.period)
        
        # reset clock
        # self.set_source('clock', reset=True)
