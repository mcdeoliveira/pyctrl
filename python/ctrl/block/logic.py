"""
This module provide logic Blocks
"""

import numpy
import math

from .. import block

# Blocks

class Compare(block.BufferBlock):
    """
    The Block Compare takes two inputs and writes `1` if 
    
    input[1] >= input[0] + threshold

    or `0` otherwise.
    """
    
    def __init__(self, threshold = 0, *vars, **kwargs):
        """
        Constructs a new *Compare* object.

        :param threshold: the threshold to be used for comparison
        """

        self.threshold = threshold
        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Compare* object.

        :param threshold: the threshold to be used for comparison
        """
        
        if 'threshold' in kwargs:
            self.threshold = kwargs.pop('threshold')

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Returns `1` if

            input[1] >= input[0] + threshold

        or `0` otherwise.

        :param values: list of values of length equal to two
        :return: tuple with 0 or 1
        """

        # call super
        super().write(*values)
        
        assert len(values) == 2
        if values[1] - values[0] >= self.threshold:
            self.buffer = (1, )
        else:
            self.buffer = (0, )

class CompareAbs(block.BufferBlock):
    """
    The Block *CompareAbs* takes one input and writes `1` if 
    
    `fabs(input[0]) <= threshold`

    or `0` otherwise if *invert* is `False`. 

    If *invert* is `True` writes `1` if 
    
    `fabs(input[0]) >= threshold`

    or `0` otherwise.
    """

    def __init__(self, threshold = 0.5, invert = False, *vars, **kwargs):
        """
        Constructs a new *CompareAbs* object.

        :param threshold: the threshold to be used for comparison (default 0.5)
        :param invert: if output is to be inverted or not (default False)
        """

        self.threshold = threshold
        self.invert = invert

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of *CompareAbs* object.

        :param threshold: the threshold to be used for comparison
        :param invert: if output is to be inverted or not
        """
        if 'threshold' in kwargs:
            self.threshold = kwargs.pop('threshold')

        if 'invert' in kwargs:
            self.invert = kwargs.pop('invert')

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Returns `1` if

        `input[0] <= threshold`

        or `0` otherwise if *invert* is `False`.

        If *invert* is `True` writes `1` if 
    
        `fabs(input[0]) >= threshold`
        
        or `0` otherwise.

        :param values: list of values of length equal to one
        :return: tuple with 0 or 1
        """

        # call super
        super().write(*values)
        
        assert len(values) == 1
        if math.fabs(values[0]) <= self.threshold:
            if self.invert:
                self.buffer = (0, )
            else:
                self.buffer = (1, )
        else:
            if self.invert:
                self.buffer = (1, )
            else:
                self.buffer = (0, )

class Trigger(block.BufferBlock):
    """
    The Block *Trigger* writes
    
    a tuple of zeros of length `len(values)-1`
    
    if *state* is `False` and function(values[0]) is
    False. Otherwise returns
    
    `values[1:]`
    
    Once function(values[0]) becomes True *state* is set
    to True and must be reset manually.
    """
    
    def __init__(self, function = (lambda x: x), state = False, *vars, **kwargs):
        """
        Constructs a new *Trigger* object.

        :param function: the test function (default identity)
        :param state: the initial state (default False)
        """

        self.function = function
        self.state = state

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Trigger* object.

        :param function: the test function
        :param state: the current state (True or False)
        """
        
        if 'function' in kwargs:
            self.state = kwargs.pop('function')
            
        if 'state' in kwargs:
            self.state = kwargs.pop('state')

        super().set(**kwargs)

    def reset(self):
        """
        Reset *Trigger* object state to False.
        """

        self.state = False
    
    def write(self, *values):
        """
        Returns 

        a tuple of zeros of length `len(values)-1`

        if *state* is `False` and function(values[0]) is
        False. Otherwise returns

        `values[1:]`

        Once function(values[0]) becomes True *state* is set
        to True and must be reset manually.
        
        :param values: list of values of length greater than one
        :return: see above
        """

        # call super
        super().write(*values)
        
        assert len(values) > 0
        if self.state:
            self.buffer = values[1:]
        elif self.function(values[0]):
            self.state = True
            self.buffer = values[1:]
        else:
            self.buffer = tuple((len(values)-1)*[0])
