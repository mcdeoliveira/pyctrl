#!/usr/bin/env python3

import keras

def build_model(shape):
        
    img_in = keras.layers.Input(shape=shape, name='img_in')
    x = img_in

    # Convolution2D class name is an alias for Conv2D
    x = keras.layers.Convolution2D(filters=24,
                                   kernel_size=(5, 5),
                                   strides=(2, 2),
                                   activation='relu')(x)
    x = keras.layers.Convolution2D(filters=32,
                                   kernel_size=(5, 5),
                                   strides=(2, 2),
                                   activation='relu')(x)
    x = keras.layers.Convolution2D(filters=64,
                                   kernel_size=(5, 5),
                                   strides=(2, 2),
                                   activation='relu')(x)
    x = keras.layers.Convolution2D(filters=64,
                                   kernel_size=(3, 3),
                                   strides=(2, 2),
                                   activation='relu')(x)
    x = keras.layers.Convolution2D(filters=64,
                                   kernel_size=(3, 3),
                                   strides=(1, 1),
                                   activation='relu')(x)
    
    x = keras.layers.Flatten(name='flattened')(x)
    x = keras.layers.Dense(units=100, activation='linear')(x)
    x = keras.layers.Dropout(rate=.1)(x)
    x = keras.layers.Dense(units=50, activation='linear')(x)
    x = keras.layers.Dropout(rate=.1)(x)
    
    # categorical output of the angle
    angle_out = keras.layers.Dense(units=1,
                                   activation='linear',
                                   name='angle_out')(x)
    
    # continous output of throttle
    throttle_out = keras.layers.Dense(units=1,
                                      activation='linear',
                                      name='throttle_out')(x)
    
    model = keras.models.Model(inputs=[img_in],
                               outputs=[angle_out, throttle_out])
    
    model.compile(optimizer='adam',
                  loss={'angle_out': 'mean_squared_error',
                        'throttle_out': 'mean_squared_error'},
                  loss_weights={'angle_out': 0.5, 'throttle_out': .5})
    
    return model


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block.opencv.camera import Camera, Screen
    from pyctrl.block import Printer
    from pyctrl.block.system import System
    from pyctrl.system.keras import Keras
    
    # initialize controller
    Ts = 1/20
    hello = Controller(period = Ts)

    # build default model
    resolution = (160, 120)
    shape = (120, 160, 3)
    keras_model = build_model(shape)

    # add the signal myclock
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
    hello.add_filter('keras',
                     System(model = Keras(keras_model)),
                     ['image'],
                     ['angles'])
    
    # add printer
    hello.add_sink('printer',
                   Printer(),
                   ['angles'])

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
