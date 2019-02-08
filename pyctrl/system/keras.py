import keras
from pyctrl.system import SystemException

from .. import system


class Keras(system.System):
    r"""
    :py:class:`pyctrl.system.Keras` implements a keras model.

    :param model: keras model
    """
    
    def __init__(self,
                 model):

        # TODO: make sure it is keras model
        if not isinstance(model, keras.models.Model):
            raise SystemException('model must be keras.models.Model')

        self.model = model
    
    def update(self, uk):
        r"""
        Update :py:class:`pyctrl.system.Keras` model.

        :param numpy.array uk: input at time k
        """
        uk = uk.reshape((1,) + uk.shape)
        yk = self.model.predict(uk)

        return yk
