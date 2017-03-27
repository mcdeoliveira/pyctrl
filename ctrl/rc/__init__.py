import time

import rcpy
import ctrl

class Controller(ctrl.Controller):
    """
    :bases: :py:class:`ctrl.Controller`

    :py:class:`ctrl.rc.Controller` initializes a controller for the Robotics Cape equiped with a clock based on the MPU9250 periodic interrupts.

    :param float period: period in seconds (default 0.01)
    :param kwargs: other keyword parameters
    """
    def __init__(self, **kwargs):

        # period (default 100Hz)
        self.period = kwargs.pop('period', 0.01)

        # Initialize controller
        super().__init__(**kwargs)

        # set state as RUNNING
        rcpy.set_state(rcpy.RUNNING)

        # register cleanup function
        rcpy.add_cleanup(rcpy.set_state, (rcpy.EXITING,))

    def __reset(self):

        # call super
        super().__reset()
      
        # print("ctrl.bbb.reset: PERIOD = {}".format(self.period))
        
        # remove current clock
        self.remove_source('clock')
        
        # add device clock
        self.add_device('clock',
                        'ctrl.rc.mpu9250', 'MPU9250',
                        type = 'source',
                        outputs = ['clock'],
                        period = self.period)

        # set clock period: it will be ignored at the construction time
        # because MPU9250 is a singleton
        self.set_source('clock', period = self.period)
        
        # reset clock
        self.set_source('clock', reset=True)
