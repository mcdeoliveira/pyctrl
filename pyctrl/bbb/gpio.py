import Adafruit_BBIO.GPIO as GPIO

import pyctrl.block as block

class Input(block.BufferBlock):

    def __init__(self,
                 pin = 'P8_24',
                 *vars, **kwargs):

        # set pin
        self.pin = pin

        # setup as input
        GPIO.setup(self.pin, GPIO.IN)

        # call super
        super().__init__(*vars, **kwargs)

    def read(self):

        #print('> read')
        if self.enabled:

            # read digital pin
            self.buffer = (GPIO.input(self.pin), )
        
        return self.buffer

class Output(block.BufferBlock):

    def __init__(self,
                 pin = 'P8_24',
                 *vars, **kwargs):

        # set pin
        self.pin = pin

        # setup as output
        GPIO.setup(self.pin, GPIO.OUT)

        # call super
        super().__init__(*vars, **kwargs)

    def write(self, *values):

        #print('> read')
        if self.enabled:

            # write to digital pin
            GPIO.output(self.pin, values[0])
        
if __name__ == "__main__":

    import time, math

    print("> Testing GPIO input")
    
    input = Input(pin='P8_24')
    (x,) = input.read()

    print('> GPIO {} = {:5.3f}'.format(input.pin, x))
    
    print("> Testing GPIO output")
    
    output = Output(pin='P8_24')
    input.write(1)
