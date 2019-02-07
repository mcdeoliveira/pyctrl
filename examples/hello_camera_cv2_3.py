#!/usr/bin/env python3

import pyctrl.system as system
import pyctrl.block as block
#import pyctrl.block.system as blksys
import numpy as np
    
def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.opencv.camera import Camera, Screen, SaveFrame, BlurFrame
    #from pyctrl.block import Printer

    # initialize controller
    Ts = 1/20
    hello = Controller(period = Ts)

    # add the signal myclock
    hello.add_signal('image')

    resolution = (640, 480)
    # add a Camera as a source
    hello.add_source('camera',
                     Camera(resolution=resolution, flip=1, transpose=False),
                     ['image'],
                     enable = True)
    
    # add a SharpenFrame as a Filter
    hello.add_filter('blur_screen',
                     BlurFrame(),
                     ['image'],
                     ['blurImage'])
    
    # add a Screen as a sink
    hello.add_sink('BlurredScreen',
                   Screen(),
                   ['blurImage'],
                   enable = True)
                   
    # Save frames
    hello.add_sink('frames',
                    SaveFrame(filename='tmp/frame'),
                    ['blurImage'],
                    enable = True)
    # add printer
    #hello.add_sink('printer',
    #               Printer(message = 'avg1 = {:3.1f}, avg2 = {:3.1f}',
    #                       endln = '\r'),
    #               ['avg1', 'avg2'])
    
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
