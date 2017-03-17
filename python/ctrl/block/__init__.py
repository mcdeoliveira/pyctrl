"""
This module provides the basic building blocks for implementing controllers.
"""

import contextlib
import numpy
import sys

class BlockException(Exception):
    pass

class Block:
    """
    *Block* provides the basic functionality for all types of blocks.
        
    `Block` does not take any parameters other than *enable* and will raise
    *BlockException* if any of the *vars* or *kwargs* is left
    unprocessed.
        
    :param enable: set block as enabled (default True)
    """
    
    def __init__(self, *vars, **kwargs):
        
        self.enabled = kwargs.pop('enabled', True)

        if len(vars) > 0:
            raise BlockException("Unknown parameter(s) '{}'".format(', '.join(str(v) for v in vars)))
        elif len(kwargs) > 0:
            raise BlockException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

    def is_enabled(self):
        """
        Return *enabled* state

        :return: enabled
        """
        return self.enabled
        
    def set_enabled(self, enabled  = True):
        """
        Set *enabled* state

        :param enabled: True or False (default True)
        """
        self.enabled = enabled

    def reset(self):
        """
        Reset block

        Does nothing here but allows another *Block* to reset itself.
        """
        pass

    def set(self, **kwargs):
        """
        Set properties of blocks. Will raise *BlockException* if any
        *kwargs* is left unprocessed.

        :param reset: if `True` calls `self.reset()`
        """

        if 'reset' in kwargs:
            if kwargs.pop('reset'):
                self.reset()

        if 'enabled' in kwargs:
            self.set_enabled(kwargs.pop('enabled'))
            
        if len(kwargs) > 0:
            raise BlockException("Does not know how to set '{}'".format(kwargs))

    def get(self, keys = None, exclude = ()):
        """
        Get properties of blocks. For example:

        `block.get('enabled')`

        will retrieve the value of the property *enabled*. Returns a
        tuple with key values if argument *keys* is a list.

        Will raise *KeyError* if key is not defined.

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        """

        if keys is None or isinstance(keys, (list, tuple)):
            #print('keys = {}'.format(keys))
            if keys is None:
                retval = self.__dict__.copy()
            else:
                retval = { k : self.__dict__[k] for k in keys }
            for key in exclude:
                del retval[key]
            return retval

        if len(exclude) == 0 or keys not in exclude:
            return self.__dict__[keys]

        raise KeyError()

    def read(self):
        """
        Read from *Block*.

        Will raise *BlockException* if block does not support read.
        """
        raise BlockException('This block does not support read')

    def write(self, *values):
        """
        Write to *Block*

        Will raise *BlockException* if block does not support write.
        """
        raise BlockException('This block does not support write')

class BufferBlock(Block):
    """
    *BufferBlock* provides the basic functionality for blocks that
    implement *read*. 

    A *BufferBlock* has the property *buffer*.
    
    Reading from a *BufferBlock* reads the *buffer*.

    An object that inherits from BufferBlock need not
    implement `read()` but simply write to `self.buffer`.
    """

    def __init__(self, *vars, **kwargs):
        
        self.buffer = ()

        super().__init__(*vars, **kwargs)

    def get(self, keys = None, exclude = ()):
        """
        Get properties of a *BufferBlock*.

        This method excludes *buffer* from the list of properties. 

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        """
        # call super
        return super().get(keys, exclude = exclude + ('buffer',))
        
    def read(self):
        """
        Returns the private *buffer* property.

        :returns: `buffer`
        """
        # get buffer
        return self.buffer

    
class Printer(Block):
    """
    A *Printer* block prints the values of signals to the screen.

    :param endl: end-of-line character (default `'\\\\n'`)
    :param frmt: format string (default `{: 12.4f}`)
    :param sep: field separator (default `' '`)
    :param file: file to print on (default `sys.stdout`)
    """
    
    def __init__(self, *vars, **kwargs):
        
        self.endln = kwargs.pop('endln', '\n')
        self.frmt = kwargs.pop('frmt', '{: 12.4f}')
        self.sep = kwargs.pop('sep', ' ')
        self.file = kwargs.pop('sep', sys.stdout)

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Printer*.

        :param endl: end-of-line character
        :param frmt: format string
        :param sep: field separator
        :param file: file to print on
        """
        
        if 'endln' in kwargs:
            self.endln = kwargs.pop('endln')
        
        if 'frmt' in kwargs:
            self.frmt = kwargs.pop('frmt')

        if 'sep' in kwargs:
            self.sep = kwargs.pop('sep')

        if 'file' in kwargs:
            self.file = kwargs.pop('file')
            
        super().set(**kwargs)
    
    def write(self, *values):
        """
        Write formated entries of `values` to `file`.
        """
        
        if self.enabled:

            @contextlib.contextmanager
            def printoptions(*args, **kwargs):
                original = numpy.get_printoptions()
                numpy.set_printoptions(*args, **kwargs)
                yield 
                numpy.set_printoptions(**original)

            row = numpy.hstack(values)
            print(self.sep.join(self.frmt.format(val) for val in row),
                  file=self.file, end=self.endln)


class Signal(Block):
    """
    A *Signal* block outputs values of a vector `signal` sequentially
    each time `read` is called.

    If `repeat` is True, signal repeats periodically.

    :param signal: `numpy` vector with values
    :param repeat: if `True` then signal repeats periodically
    """

    def __init__(self, signal, repeat = False, *vars, **kwargs):

        # signal
        self.signal = numpy.array(signal)

        # repeat?
        self.repeat = repeat

        # index
        self.index = 0
       
        super().__init__(*vars, **kwargs)

    def reset(self):
        """
        Reset *Signal* index back to `0`
        """

        self.index = 0

    def set(self, **kwargs):
        """
        Set properties of *Signal*. 

        :param signal: `numpy` vector with values
        :param index: current index
        """

        if 'signal' in kwargs:
            self.signal = numpy.array(kwargs.pop('signal'))
            self.reset()

        if 'index' in kwargs:
            index = kwargs.pop('index')
            assert isinstance(index, int)
            assert index >= 0 and index < len(self.signal)
            self.index = index 
            
        super().set(**kwargs)

    def read(self, *values):
        """
        Read from *Signal*.

        Reading increments current `index`.

        If `repeat` is True, `index` becomes `0` after end of `signal`.
        """

        # return 0 if over the edge
        if self.index >= len(self.signal):

            xk = 0 * self.signal[0]

        else:

            # get entry
            xk = self.signal[self.index]
            
            # increment
            self.index += 1
            
            if self.repeat and self.index == len(self.signal):

                # reset
                self.index = 0
        
        return (xk, )

class Map(BufferBlock):
    """
    A *Map* block applies 'function' to each input and returns tuple
    with results.

    :param function: the function to be applied
    """

    def __init__(self, function = (lambda x: x), *vars, **kwargs):

        self.function = function
        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Map* object.

        :param function: the function to be mapped (default identity)
        """
        
        if 'function' in kwargs:
            self.function = kwargs.pop('function')

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes a tuple with the result of *function* applied to each
        input to the private *buffer*.

        :param values: list of values of any length
        :return: tuple with results of map(function, values)
        """

        if self.enabled:
            self.buffer = tuple(map(self.function, values))

class Apply(BufferBlock):
    """
    The Block *Apply* applies *function* to all inputs and returns tuple
    with the result.

    :param function: the function to be applied
    """

    def __init__(self, function = (lambda x: x), *vars, **kwargs):

        self.function = function
        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Apply* object.

        :param function: the function to be applied (default identity)
        """
        
        if 'function' in kwargs:
            self.function = kwargs.pop('function')

        super().set(**kwargs)
        
    def write(self, *values):
        """
        Writes a tuple with the result of *function* applied to all
        inputs to the private *buffer*.

        :param values: list of values of any length
        :return: tuple with results of `function(*values)`
        """

        if self.enabled:
            eval = self.function(*values)
            if isinstance(eval, (list, tuple)):
                self.buffer = tuple(eval)
            else:
                self.buffer = (eval,)

