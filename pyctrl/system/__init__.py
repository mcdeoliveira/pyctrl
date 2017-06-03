"""
This module provides objects that can be used to represent time-invariant and time-varying dynamic systems.
"""

class System:
    """
    Base class for dynamic time-invariant systems.
    """

    def set_output(self, yk):
        """
        Sets the internal state of the :py:class:`pyctrl.system.System` so
        that a call to :py:meth:`pyctrl.system.System.update` with
        :py:data:`uk = 0` yields :py:attr:`yk`.
        
        :param yk: scalar desired :py:attr:`yk`
        """
        raise SystemException("Method not implemented")
    
    def shape(self):
        """
        Shape of a :py:class:`pyctrl.system.System`

        :return: tuple with number of inputs, number of outputs and order
        """
        pass

    def update(self, uk):
        """
        Time update :py:class:`pyctrl.system.System` model.

        :param uk: the input :py:attr:`uk`
        :return: the output of the model
        """
        pass

class TVSystem(System):
    """
    Base class for dynamic time-varying systems.
    """
    
    def set_output(self, tk, yk):
        """
        Sets the internal state of the :py:class:`pyctrl.system.TVSystem` so
        that a call to :py:meth:`pyctrl.system.System.update` with
        :py:data:`uk = 0` and :py:attr:`tk` yields :py:attr:`yk`.
        
        :param yk: scalar desired :py:attr:`yk`
        """
        raise SystemException("Method not implemented")
    
    def shape(self):
        """
        Shape of a :py:class:`pyctrl.system.System`

        :return: tuple with number of inputs, number of outputs and order
        """
        pass

    def update(self, tk, uk):
        """
        Time update :py:class:`pyctrl.system.System` model.

        :param tk: the time :py:attr:`tk`
        :param uk: the input :py:attr:`uk`
        :return: the output of the model
        """
        pass

class SystemException(Exception):
    """
    Exception class for module :py:mod:`pyctrl.system`.
    """
    pass
