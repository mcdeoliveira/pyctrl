#!/usr/bin/env python3


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.pygame.camera import Camera, Screen, SaveFrame

    # initialize controller
    Ts = 1/20
    hello = Controller(period=Ts)

    # add the signal image
    hello.add_signal('image')

    # add a Camera as a source
    resolution = (640, 480)
    hello.add_source('camera',
                     Camera(resolution=resolution),
                     ['image'],
                     enable=True)

    # add a Screen as a sink
    hello.add_sink('screen',
                   Screen(),
                   ['image'],
                   enable=True)

    # add a SaveFrame as a sink
    hello.add_sink('save',
                   SaveFrame(filename='dan', number_of_digits=2),
                   ['image'],
                   enable=True)
    
    try:
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
