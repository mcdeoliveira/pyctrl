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
    *BlockException* if any of the *kwargs* is left unprocessed.
        
    :param enable: set block as enabled (default True)
    """
    
    def __init__(self, **kwargs):
        
        self.enabled = kwargs.pop('enabled', True)

        if len(kwargs) > 0:
            raise BlockException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

    def is_enabled(self):
        """
        Return *enabled* state.

        :return: enabled
        """
        return self.enabled
        
    def set_enabled(self, enabled  = True):
        """
        Set *enabled* state.

        :param enabled: True or False (default True)
        """
        self.enabled = enabled

    def reset(self):
        """
        Reset block.

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
        Write to *Block*.

        Will raise *BlockException* if block does not support write.
        """
        raise BlockException('This block does not support write')

class BufferBlock(Block):
    """
    *BufferBlock* provides the basic functionality for blocks that
    implement `read` and `write` through a local `buffer`. 

    A *BufferBlock* has the property `buffer`.
    
    Writing from a *BufferBlock* writes to the `buffer`.

    Reading from a *BufferBlock* reads from the `buffer`.

    Multiplexing and demultiplexing options are available.

    If `mux` is `False` (`demux` is `False`) then `read` (`write`) are
    simply copied to (from) the `buffer`.

    If `mux` is `True` then `read` writes a numpy array with the
    contents of `*values` to `buffer`.

    If `demux` is `True` then `write` splits `buffer` into a tuple
    with scalar entries.

    Objects that inherit from *BufferBlock* overwrite the methods
    `buffer_read` and `buffer_write` instead of `read` and `write`.
    """
    def __init__(self, **kwargs):
        
        self.buffer = ()

        self.mux = kwargs.pop('mux', False)
        self.demux = kwargs.pop('demux', False)

        super().__init__(**kwargs)

    def get(self, keys = None, exclude = ()):
        """
        Get properties of a *BufferBlock*.

        This method excludes `buffer` from the list of properties. 

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        """
        # call super
        return super().get(keys, exclude = exclude + ('buffer',))
        
    def write(self, *values):
        """
        Writes to the private `buffer` property then call `self.buffer_write`.

        If `mux` is `False` then `*values` are simply copied to the
        `buffer`.

        If `mux` is `True` then `*values` writes a numpy array with the
        contents of `*values` to the first entry of `buffer`.

        :param values: list of values
        """

        if self.enabled:
            
            if values and self.mux:
                # convert values to numpy array
                self.buffer = (numpy.hstack(values),)
            else:
                # simply copy to buffer
                self.buffer = values

            # call buffer_write
            self.buffer_write()

    def read(self):
        """
        Calls `self.buffer_read` then returns the private `buffer` property.

        If `demux` is `False` then read returns a copy of the local `buffer`. 

        If `demux` is `True` then `buffer` is split into a tuple with
        scalar entries.

        :returns: `buffer`
        """
        if self.enabled:

            # call buffer_read
            self.buffer_read()
        
            # return buffer
            if self.buffer and self.demux:
                self.buffer = tuple(numpy.hstack(self.buffer).tolist())
                
            return self.buffer

        # else return None

    def buffer_read(self):
        pass

    def buffer_write(self):
        pass
        
    
class Printer(Block):
    """
    A *Printer* block prints the values of signals to the screen.

    :param endl: end-of-line character (default `'\\\\n'`)
    :param frmt: format string (default `{: 12.4f}`)
    :param sep: field separator (default `' '`)
    :param file: file to print on (default `sys.stdout`)
    """
    
    def __init__(self, **kwargs):
        
        self.endln = kwargs.pop('endln', '\n')
        self.frmt = kwargs.pop('frmt', '{: 12.4f}')
        self.sep = kwargs.pop('sep', ' ')
        self.file = kwargs.pop('sep', sys.stdout)

        super().__init__(**kwargs)

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


class Signal(BufferBlock):
    """
    A *Signal* block outputs values of a vector `signal` sequentially
    each time `read` is called.

    If `repeat` is True, signal repeats periodically.

    :param signal: `numpy` vector with values
    :param repeat: if `True` then signal repeats periodically
    """

    def __init__(self, **kwargs):

        # signal
        self.signal = numpy.array(kwargs.pop('signal', []))

        # repeat?
        self.repeat = kwargs.pop('repeat', False)

        # index
        self.index = 0
       
        super().__init__(**kwargs)

    def reset(self):
        """
        Reset *Signal* index back to `0`.
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
            if not self.repeat:
                assert index >= 0 and index < len(self.signal)
            else:
                index = index % len(self.signal)
            self.index = index 
            
        if 'repeat' in kwargs:
            self.repeat = kwargs.pop('repeat')
            
        super().set(**kwargs)

    def buffer_read(self):
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
        
        self.buffer = (xk,)

class Map(BufferBlock):
    """
    A *Map* block applies 'function' to each input and returns tuple
    with results.

    :param function: the function to be applied
    """

    def __init__(self,  **kwargs):

        # function
        self.function = kwargs.pop('function', lambda x: x)
        
        super().__init__(**kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Map* object.

        :param function: the function to be mapped (default identity)
        """
        
        if 'function' in kwargs:
            self.function = kwargs.pop('function')

        super().set(**kwargs)
        
    def buffer_write(self):
        """
        Writes a tuple with the result of `function` applied to each
        input to the private `buffer`.
        """

        self.buffer = tuple(map(self.function, self.buffer))

class Apply(BufferBlock):
    """
    The Block *Apply* applies `function` to all inputs and returns tuple
    with the result.

    :param function: the function to be applied
    """

    def __init__(self, **kwargs):

        # function
        self.function = kwargs.pop('function', lambda x: x)
        
        super().__init__(**kwargs)

    def set(self, **kwargs):
        """
        Set properties of *Apply* object.

        :param function: the function to be applied (default identity)
        """
        
        if 'function' in kwargs:
            self.function = kwargs.pop('function')

        super().set(**kwargs)
        
    def buffer_write(self):
        """
        Writes a tuple with the result of `function` applied to all
        inputs to the private `buffer`.
        """

        self.buffer = (self.function(*self.buffer), )
