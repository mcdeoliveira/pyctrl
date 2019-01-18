#!/usr/bin/env python3

import pyctrl.system as system
import pyctrl.block as block
import pyctrl.block.system as blksys
import numpy as np

class AverageArray(block.Filter, block.BufferBlock):

    def read(self):

        # print('> read')
        if self.enabled:

            self.buffer = (np.average(self.buffer[0]), )
        
        return self.buffer

class Model(system.System):

    def update(self, uk):

        return np.average(uk)

    
def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.opencv.camera import Camera, Screen
    from pyctrl.block import Printer

    # initialize controller
    Ts = 1/20
    hello = Controller(period = Ts)

    # add the signal myclock
    hello.add_signal('image')

    # add a Camera as a source
    hello.add_source('camera',
                     Camera(resolution=(160,120), flip=1, transpose=False),
                     ['image'],
                     enable = True)

    # add a Screen as a sink
    hello.add_sink('screen',
                   Screen(),
                   ['image'],
                   enable = True)

    # add a AverageArray as a filter
    hello.add_filter('average1',
                     AverageArray(),
                     ['image'],
                     ['avg1'])

    # add a ImageToNumpy as a filter
    hello.add_filter('average2',
                     blksys.System(model = Model()),
                     ['image'],
                     ['avg2'])
    
    # add printer
    hello.add_sink('printer',
                   Printer(message = 'avg1 = {:3.1f}, avg2 = {:3.1f}',
                           endln = '\r'),
                   ['avg1', 'avg2'])
    
    try:

        print(hello.info('all'))
        
        # run the controller
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        print('Done')
    
if __name__ == "__main__":
    
    main()
