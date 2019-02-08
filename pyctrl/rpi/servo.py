import pyctrl.block as block

from pyctrl.rpi.PCA9685 import PCA9685

# initialize PCA9685
pwm = PCA9685(60)


class Servo(block.Sink, block.Block):
    
    def __init__(self, **kwargs):

        self.channel = kwargs.pop('channel', 0)

        # call super
        super().__init__(**kwargs)

        # disable servo
        self.set_enabled(False)
                                                    
    def write(self, *values):

        #print('> write to motor')
        if self.enabled:

            assert len(values) == 1
            pwm.set_pulse(self.channel, values[0])
            

if __name__ == "__main__":

    import time, math
                
    print("> Testing Servo")
                
    servo1 = Servo(channel = 1)
    servo1.set_enabled(True)

    # run servo
    servo1.write(150)
    time.sleep(1)

    # run servo
    servo1.write(600)
    time.sleep(1)

    # stop motor
    servo1.write(0)

