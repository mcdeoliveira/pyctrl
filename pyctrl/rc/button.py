import pyctrl.block as block

import rcpy
import rcpy.gpio as gpio
import rcpy.button as button

class Button(block.Source, block.Block):

    def __init__(self, **kwargs):

        self.pin = kwargs.pop('pin', gpio.PAUSE_BTN)
        self.button = button.Button(self.pin)
        self.invert = kwargs.pop('invert', False)

        # call super
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):

        if 'pin' in kwargs:
            self.pin = kwargs.pop('pin')
            self.button = button.Button(self.pin)

        exclude += ('button', )
            
        # call super
        super().set(**kwargs)

    def get(self, *keys, exclude = ()):
        
        # call super
        return super().get(*keys, exclude = exclude + ('button',))
        
    def read(self):

        #print('> write to led')
        if self.enabled:

            if self.invert:
                if self.button.is_pressed():
                    return (0,)
                else:
                    return (1,)
            else:
                if self.button.is_pressed():
                    return (1,)
                else:
                    return (0,)


