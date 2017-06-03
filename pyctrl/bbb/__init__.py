import pyctrl

class Controller(pyctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # period (default 100Hz)
        self.period = kwargs.pop('period', 0.01)

        # Initialize controller
        super().__init__(*vargs, **kwargs)

    def __reset(self):

        # call super
        super().__reset()
      
        # print("pyctrl.bbb.reset: PERIOD = {}".format(self.period))
        
        # add source: clock
        self.clock = self.add_device('clock',
                                     'pyctrl.bbb.encoder', 'Clock',
                                     type = 'source',
                                     outputs = ['clock'],
                                     period = self.period)
        # set period
        self.clock.set_period(self.period)

        # initialize clock signals
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

    # period
    def set_period(self, value):
        self.period = value

    def get_period(self):
        return self.period
