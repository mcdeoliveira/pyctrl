#!/usr/bin/env python3

import sys, tty, termios
import threading

import pyctrl

# read key stuff
ARROW_UP    = "\033[A"
ARROW_DOWN  = "\033[B"
ARROW_RIGHT = "\033[C"
ARROW_LEFT  = "\033[D"
DEL         = "."
END         = "/"
SPACE       = " "


def read_key():

    key = sys.stdin.read(1)
    if ord(key) == 27:
        key = key + sys.stdin.read(2)
    elif ord(key) == 3:
        raise KeyboardInterrupt    

    return key


def get_arrows(hello, fd):

    throttle = 0
    steering = 0
    
    tty.setcbreak(fd)
    while hello.get_state() != pyctrl.EXITING:
        
        print('\rthrottle = {:+5.2f} deg/s'
              '  steering = {:+5.2f} %'
              .format(throttle,
                      steering),
              end='')
        
        key = read_key()
        if key == ARROW_LEFT:
            steering = max(steering - 20/360, -1)
            hello.set_signal('steering', steering)
        elif key == ARROW_RIGHT:
            steering = min(steering + 20/360, 1)
            hello.set_signal('steering', steering)
        elif key == ARROW_UP:
            throttle = throttle + 0.05
            hello.set_signal('throttle', - throttle)
        elif key == ARROW_DOWN:
            throttle = throttle - 0.05
            hello.set_signal('throttle', - throttle)
        elif key == SPACE:
            throttle = 0
            hello.set_signal('throttle', - throttle)
            steering = 0
            hello.set_signal('steering', steering)
        elif key == DEL:
            steering = 0
            hello.set_signal('steering', steering)
        elif key == END:            
            throttle = 0
            hello.set_signal('throttle', - throttle)


def main():

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
<<<<<<< HEAD
    from pyctrl.block.cv2.camera import Camera, Screen, SaveFrameValues
    from pyctrl.rpi.servo import Servo
    from pyctrl.rpi.throttle import Throttle
=======
    # from pyctrl.block.cv2.camera import Camera, Screen, SaveFrameValues
    from pyctrl.rpi.camera import Camera, SaveFrameValues
>>>>>>> devel

    # open file index
    index = open('tmp/index.txt', 'w')
    
    # initialize controller
    Ts = 1/20
    donkey = Controller(period=Ts)

    # add the signal the hello controller
    donkey.add_signal('image')

    # add a Camera as a source
    resolution = (160, 120)
    donkey.add_source('camera',
                      Camera(resolution=resolution),
                      ['image'],
                      enable=True)

    donkey.add_signals('throttle', 'steering')
    donkey.set_signal('throttle', 0)
    donkey.set_signal('steering', 0)
    
    # add printer
    donkey.add_sink('imgwrtr',
                    SaveFrameValues(filename='tmp/frame', index=index),
                    ['image', 'throttle', 'steering'])

    # TODO: add the pwm modules for throttle and steering
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        print(donkey.info('all'))

        # start the controller
        donkey.start()

        print("Press Ctrl-C or press the <PAUSE> button to exit")

        # fire thread to update velocities
        thread = threading.Thread(target=get_arrows,
                                  args=(donkey, fd))
        thread.daemon = False
        thread.start()
        
        # and wait until controller dies
        donkey.join()

    except KeyboardInterrupt:
        pass

    finally:

        # make sure it exits
        donkey.set_state(pyctrl.EXITING)

        print("Press any key to exit")

        thread.join()

        # close index file
        index.close()

        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    
    main()
