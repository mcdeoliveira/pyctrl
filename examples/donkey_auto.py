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

def build_model(shape):
        
    from keras.models import Sequential
    from keras.layers import Conv2D, Dense, Flatten, Dropout

    #img_in = keras.layers.Input(shape=shape, name='img_in')
    #x = img_in

    # Convolution2D class name is an alias for Conv2D
    model = Sequential()
    model.add(Conv2D(filters=24,
                     kernel_size=(5, 5),
                     strides=(2, 2),
                     activation='relu',
                     input_shape=shape))
    model.add(Conv2D(filters=32,
                     kernel_size=(5, 5),
                     strides=(2, 2),
                     activation='relu'))
    model.add(Conv2D(filters=64,
                     kernel_size=(5, 5),
                    strides=(2, 2),
                     activation='relu'))
    model.add(Conv2D(filters=64,
                     kernel_size=(3, 3),
                     strides=(2, 2),
                     activation='relu'))
    model.add(Conv2D(filters=64,
                     kernel_size=(3, 3),
                     strides=(1, 1),
                     activation='relu'))

    model.add(Flatten(name='flattened'))
    model.add(Dense(units=100, activation='linear'))
    model.add(Dropout(rate=.1))
    model.add(Dense(units=50, activation='linear'))
    model.add(Dropout(rate=.1))
    
    # categorical output of the angle
    model.add(Dense(units=2,
                    activation='linear',
                    name='angles_out'))
    
    #model = keras.models.Model(inputs=[img_in],
    #                           outputs=[angle_out, throttle_out])
    
    model.compile(optimizer='adam',
                  loss={'angles_out': 'mean_squared_error'},
                  loss_weights={'angles_out': [.5, .5]})
    
    return model


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.cv2.camera import Camera, Screen, SaveFrameValues
    from pyctrl.block import Printer
    from pyctrl.block.system import System
    from pyctrl.system.keras import Keras

    # open file index
    index = open('tmp/index.txt', 'w')
    
    # initialize controller
    Ts = 1
    hello = Controller(period = Ts)

    # build default model
    resolution = (160, 120)
    shape = (160, 120, 3)
    keras_model = build_model(shape)

    # add the signal the hello controller
    hello.add_signal('image')

    # add a Camera as a source
    hello.add_source('camera',
                     Camera(resolution=resolution),
                     ['image'],
                     enable = True)

    # add a Screen as a sink
    hello.add_sink('screen',
                   Screen(),
                   ['image'],
                   enable = True)

    # add keras model
    # hello.add_filter('keras',
    #                 System(model = Keras(keras_model)),
    #                  ['image'],
    #                 ['angles'])

    hello.add_signals('throttle', 'steering')
    hello.set_signal('throttle', 0)
    hello.set_signal('steering', 0)
    
    # add printer
    hello.add_sink('imgwrtr',
                   SaveFrameValues(filename='tmp/frame', index=index),
                   ['image', 'throttle', 'steering'])
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        print(hello.info('all'))

        # start the controller
        hello.start()

        print("Press Ctrl-C or press the <PAUSE> button to exit")

        # fire thread to update velocities
        thread = threading.Thread(target = get_arrows,
                                  args = (hello, fd))
        thread.daemon = False
        thread.start()
        
        # and wait until controller dies
        hello.join()

    except KeyboardInterrupt:
        pass

    finally:
        print('Done')
        index.close()

if __name__ == "__main__":
    
    main()
