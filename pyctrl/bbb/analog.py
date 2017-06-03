import Adafruit_BBIO.ADC as ADC

import pyctrl.block as block

class Analog(block.BufferBlock):

    # initialize adc
    ADC.setup()
        
    def __init__(self, 
                 pin = 'AIN0', 
                 full_scale = 1., 
                 invert = False,
                 *vars, **kwargs):

        # set pin
        self.pin = pin

        # set full_scale
        self.full_scale = full_scale

        # set invert
        self.invert = invert

        # call super
        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        
        if 'full_scale' in kwargs:
            self.full_scale = kwargs.pop('full_scale')

        if 'invert' in kwargs:
            self.invert = kwargs.pop('invert')

        super().set(**kwargs)

    def read(self):

        #print('> read')
        if self.enabled:

            # read analog pin
            measure = min(100, 
                          100 * ADC.read(self.pin) / self.full_scale)

            # invert?
            if self.invert:
                measure = 100 - measure

            self.buffer = (measure, )
        
        return self.buffer

if __name__ == "__main__":

    import time, math

    T = 0.1
    K = 1000

    print("> Testing ADC")
    
    adc = Analog(pin='AIN2')

    k = 0
    while k < K:

        # read accelerometer
        (x,) = adc.read()

        print('\r> ADC {} = {:5.3f}'.format(adc.pin, x), end='')

        time.sleep(T)
        k += 1
