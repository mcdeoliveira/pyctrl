import pyctrl.block as block

import rcpy
import rcpy.gpio as gpio
import rcpy.led as led

class LED(block.Sink, block.Block):

    def __init__(self, **kwargs):

        self.pin = kwargs.pop('pin', gpio.GRN_LED)
        self.led = led.LED(self.pin)

        # call super
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):

        if 'pin' in kwargs:
            self.pin = kwargs.pop('pin')
            self.led = led.LED(self.pin)

        exclude += ('led', )
            
        # call super
        super().set(**kwargs)

    def get(self, *keys, exclude = ()):
        
        # call super
        return super().get(*keys, exclude = exclude + ('led',))
        
    def set_enabled(self, enabled = True):
        
        # call super
        super().set_enabled(enabled)

        if not enabled:

            # turn off led
            self.led.off()

    def write(self, *values):

        #print('> write to led')
        if self.enabled:

            assert len(values) == 1
            if values[0]:
                self.led.on()
            else:
                self.led.off()

