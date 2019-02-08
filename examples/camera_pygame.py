#!/usr/bin/env python3


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.pygame.camera import Camera, Screen, SaveFrame

    # initialize controller
    pygame = Controller(period = 1)

    # add the signal image
    pygame.add_signal('image')

    # add a Camera as a source
    pygame.add_source('camera',
                      Camera(),
                      ['image'],
                      enable=True)

    # add a Screen as a sink
    pygame.add_sink('screen',
                    Screen(),
                    ['image'],
                    enable=True)

    # add a SaveFrame as a sink
    pygame.add_sink('save',
                    SaveFrame(filename='dan', number_of_digits=2),
                    ['image'],
                    enable=True)
    
    try:
        # run the controller
        with pygame:
            # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        print('Done')


if __name__ == "__main__":
    
    main()
