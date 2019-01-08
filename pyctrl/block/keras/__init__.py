import pyctrl.block as block

import keras

# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
####################################################

# This class is for keras
class Keras(block.Filter, block.BufferBlock):

    @staticmethod
    def default_model(shape):
        
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
    
    def __init__(self, **kwargs):

        shape = kwargs.pop('shape', (120, 160, 3))
        if not isinstance(shape, (list, tuple)):
            raise block.BlockException('shape must be a list or tuple')
        self.shape = shape
        
        model = kwargs.pop('model', Keras.default_model(shape))
        if not isinstance(model, keras.models.Model):
            raise block.BlockException('model must be keras.models.Model')
        self.model = model
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.keras.Keras` block.
        :param gain: multiplier (default `1`)
        :param kwargs kwargs: other keyword arguments
        """

        if 'shape' in kwargs:
            shape = kwargs.pop('shape')
            if not isinstance(shape, (list, tuple)):
                raise block.BlockException('shape must be a list or tuple')
            self.shape = shape
            # TODO: do we need to reshape the model?
        
        if 'model' in kwargs:
            model = kwargs.pop('model')
            if not isinstance(model, keras.models.Model):
                raise block.BlockException('model must be keras.models.Model')
            self.model = model

        super().set(**kwargs)

    def write(self, *values):
        """
        Writes product of :py:attr:`gain` times current input to the 
        private :py:attr:`buffer`.
        :param vararg values: values
        """

        # call super
        super().write(*values)

        assert len(self.buffer) == 1
        self.buffer = self.model.predict(self.buffer[0])

# Main Method
if __name__ == "__main__":

    print("> Testing Keras")
                
    keras = Keras()

    import numpy as np
    image = np.random.rand(*keras.shape)
    image = image.reshape((1,) + image.shape)

    keras.write(image)
    (angle, throttle) = keras.read()

    
