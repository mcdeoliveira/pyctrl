#!/usr/bin/env python3


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.cv2.camera import Camera, Screen, SaveFrame, SharpenFrame

    # initialize controller
    Ts = 1/20
    hello = Controller(period=Ts)

    # add the signal myclock
    hello.add_signal('image')

    # add a Camera as a source
    resolution = (640, 480)
    hello.add_source('camera',
                     Camera(resolution=resolution, flip=1, transpose=False),
                     ['image'],
                     enable=True)

    # add a SharpenFrame as a Filter
    hello.add_filter('sharpen',
                     SharpenFrame(),
                     ['image'],
                     ['sharp_image'])

    # add a Screen as a sink
    hello.add_sink('screen',
                   Screen(),
                   ['sharp_image'],
                   enable=True)

    # Save frames
    hello.add_sink('frames',
                   SaveFrame(filename='tmp/frame'),
                   ['sharp_image'],
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
