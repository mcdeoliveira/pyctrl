import pyctrl.block as block
from pyctrl.rpi.PCA9685 import PCA9685

# initialize PCA9685
pwm = PCA9685(60)

class Throttle(block.Sink, block.Block):
    
    def __init__(self, **kwargs):

        self.channel = kwargs.pop('channel', 0)

        # call super
        super().__init__(**kwargs)

        # disable servo
        self.set_enabled(False)
                                                    
    def write(self, *values):

        #print('> write Throttle')
        if self.enabled:

            assert len(values) == 1
            pwm.set_pulse(self.channel, values[0])
            

if __name__ == "__main__":

    import time, math
                
    print("> Testing Throttle")
