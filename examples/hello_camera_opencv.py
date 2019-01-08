#!/usr/bin/env python3

def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.opencv.camera import ComputerCamera

    # initialize controller
    opencv = Controller(period = 10)

    # add the signal image
    opencv.add_signal('image')

    # add a Camera as a source
    opencv.add_source('camera',
                      ComputerCamera(),
                      ['image'],
                      enable = True)
    
    ### Need to add a sink to show the screen ##
    
    try:
        # run the controller
        with opencv:
            # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        print('Done')
    
if __name__ == "__main__":
    
    main()
