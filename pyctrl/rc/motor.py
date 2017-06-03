import pyctrl.block as block

import rcpy
import rcpy.motor as mtr

# enable motor
mtr.enable()

# make sure it is disabled when destroyed
import atexit; atexit.register(mtr.disable)

class Motor(block.Block):

    def __init__(self, **kwargs):

        self.ratio = float(kwargs.pop('ratio', 100))
        self.motor = kwargs.pop('motor', 2)

        # call super
        super().__init__(**kwargs)

        # disable motor
        self.set_enabled(False)

    def set(self, **kwargs):

        if 'ratio' in kwargs:
            # make sure ratio is a float
            self.ratio = float(kwargs.pop('ratio'))

        # call super
        super().set(**kwargs)
        
    def set_enabled(self, enabled = True):
        
        # call super
        super().set_enabled(enabled)

        if not enabled:

            # write 0 to motor
            mtr.set(self.motor, 0)
            mtr.set_free_spin(self.motor)

    def write(self, *values):

        #print('> write to motor')
        if self.enabled:

            assert len(values) == 1
            mtr.set(self.motor, values[0] / self.ratio)

if __name__ == "__main__":

    import time, math

    print("> Testing Motor1")

    motor1 = Motor(motor = 2)
    motor1.set_enabled(True)

    # run motor forward
    motor1.write(100)
    time.sleep(1)

    # stop motor
    motor1.write(0)
    time.sleep(1)

    # run back
    motor1.write(-100)
    time.sleep(1)

    # stop motor
    motor1.write(0)

    print("> Testing Motor2")

    motor2 = Motor(motor = 3)
    motor2.set_enabled(True)

    # run motor forward
    motor2.write(100)
    time.sleep(1)

    # stop motor
    motor2.write(0)
    time.sleep(1)

    # run back
    motor2.write(-100)
    time.sleep(1)

    # stop motor
    motor2.write(0)
