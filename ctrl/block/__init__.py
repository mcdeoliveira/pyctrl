"""
This module provides the basic building blocks for implementing controllers.
"""

import contextlib
import numpy
import sys

np_major, np_minor, np_release = numpy.version.version.split('.')
if int(np_major) == 1 and int(np_minor) >= 10:

    # can handle period
    #print('CAN HANDLE PERIOD')
    interp = numpy.interp

else:

    # handle period
    def interp(x,xp,fp,left,right,period):
        return numpy.interp(x,xp,fp,left,right)

class BlockException(Exception):
    pass

class Block:
    """
    *Block* provides the basic functionality for all types of blocks.
        
    `Block` does not take any parameters other than `enable`
        
    :param enable: set block as enabled (default True)
    :raise: `BlockException` if any of the `kwargs` is left unprocessed
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

    def set(self, exclude = (), **kwargs):
        """
        Set properties of *Block*.

        :param tuple exclude: list of attributes to exclude (default ())
        :param bool reset: if `True` calls `self.reset()`
        :param bool enabled: set enabled attribute
        :param kwargs: other keyword arguments
        :raise: `BlockException` if any of the `kwargs` is left unprocessed
        """

        if 'reset' in kwargs:
            if kwargs.pop('reset'):
                self.reset()

        if 'enabled' in kwargs:
            self.set_enabled(kwargs.pop('enabled'))

        for k in kwargs:
            if k in exclude or k not in self.__dict__:
                raise BlockException("Does not know how to set attribute '{}'".format(kwargs))
            else:
                # set attribute
                setattr(self, k, kwargs.get(k))

    def get(self, *keys, exclude = ()):
        """
        Get properties of blocks. For example:

        `block.get('enabled')`

        will retrieve the value of the property *enabled*. Returns a
        tuple with key values if argument *keys* is a list.

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        :raise: *KeyError* if `key` is not defined
        """

        #print('> keys = {}'.format(keys))

        if len(keys) == 0:
            
            # all keys
            retval = self.__dict__.copy()

            # exclude keys
            for k in exclude:
                # remove key
                retval.pop(k,None)

            return retval
            
        #else:
            
        # multiple keys
        retval = { k : self.__dict__[k] for k in keys }

        # exclude keys
        for k, v in retval.items():
            # if key in exclude
            if k in exclude:
                # remove key
                raise KeyError('Item with key {} does not exist'.format(k))

        # remove dict if single key
        if len(keys) == 1:
            return retval.popitem()[1]
        else:
            return retval

    def read(self):
        """
        Read from *Block*.

        :return: values
        :retype: tuple
        :raise: *BlockException* if block does not support read
        """
        raise BlockException('This block does not support read')

    def write(self, *values):
        """
        Write to *Block*.

        :param varag values: values
        :raise: *BlockException* if block does not support write
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
    
    :param bool mux: mux flag (default False)
    :param bool demux: demux flag (default False)
    """
    def __init__(self, **kwargs):
        
        self.buffer = ()

        self.mux = kwargs.pop('mux', False)
        self.demux = kwargs.pop('demux', False)

        super().__init__(**kwargs)

    def get(self, *keys, exclude = ()):
        """
        Get properties of a *BufferBlock*.

        This method excludes `buffer` from the list of properties. 

        :param keys: string or tuple of strings with property names
        :param exclude: tuple with list of keys never to be returned (Default ())
        """
        # call super
        return super().get(*keys, exclude = exclude + ('buffer',))
        
    def set(self, exclude = (), **kwargs):
        """
        Set properties of a *BufferBlock*.

        This method excludes `buffer` from the list of properties. 

        :param tuple exclude: list of attributes to exclude (default ())
        :param kwargs: other keyword arguments
        """
        
        # call super
        return super().set(exclude + ('buffer',), **kwargs)

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

    def read(self):
        """
        Calls `self.buffer_read` then returns the private `buffer` property.

        If `demux` is `False` then read returns a copy of the local `buffer`. 

        If `demux` is `True` then `buffer` is split into a tuple with
        scalar entries.

        :returns: `buffer`
        """
        if self.enabled:

            # return buffer
            if self.buffer and self.demux:
                self.buffer = tuple(numpy.hstack(self.buffer).tolist())
                
            return self.buffer

        # else return None

class ShortCircuit(BufferBlock):
    """
    *ShortCircuit* copies input to the output, that is

    :math:`y = u`
    """

class Printer(Block):
    """
    A *Printer* block prints the values of signals to the screen.

    :param endln: end-of-line character (default `'\\\\n'`)
    :param frmt: format string (default `{: 12.4f}`)
    :param sep: field separator (default `' '`)
    :param message: message to print (default `None`)
    :param file: file to print on (default `sys.stdout`)
    """
    
    def __init__(self, **kwargs):
        
        self.endln = kwargs.pop('endln', '\n')
        self.frmt = kwargs.pop('frmt', '{: 12.4f}')
        self.sep = kwargs.pop('sep', ' ')
        self.message = kwargs.pop('message', None)
        self.file = kwargs.pop('file', None)
        
        if self.file is sys.stdout:
            self.file = None
        
        super().__init__(**kwargs)

    def set(self, exclude = (), **kwargs):
        """
        Set properties of *Printer*.

        :param tuple exclude: list of attributes to exclude (default ())
        :param endl: end-of-line character
        :param frmt: format string
        :param sep: field separator
        :param message: message to print
        :param file: file to print on
        :param kwargs: other keyword arguments
        """
        
        if 'file' in kwargs:
            self.file = kwargs.pop('file')
            if self.file is sys.stdout:
                self.file = None

        # call super
        super().set(exclude, **kwargs)
    
    def write(self, *values):
        """
        Write formated entries of `values` to `file`.
        """
        
        if self.enabled:

            file = self.file
            if file is None:
                file = sys.stdout
            
            if self.message is not None:
                print(self.message.format(*values),
                      file=file,
                      end=self.endln)
                
            else:
                @contextlib.contextmanager
                def printoptions(*args, **kwargs):
                    original = numpy.get_printoptions()
                    numpy.set_printoptions(*args, **kwargs)
                    yield 
                    numpy.set_printoptions(**original)

                row = numpy.hstack(values)
                print(self.sep.join(self.frmt.format(val) for val in row),
                      file=file, end=self.endln)

class Constant(BufferBlock):
    """
    *Constant* outputs a constant.
    
    :param value: constant
    """

    def __init__(self, **kwargs):

        value = kwargs.pop('value', 1)
        
        super().__init__(**kwargs)

        if isinstance(value, (tuple, list)):
            self.buffer = value
        else:
            self.buffer = (value, )
            
    
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

    def set(self, exclude = (), **kwargs):
        """
        Set properties of *Signal*. 

        :param tuple exclude: list of attributes to exclude (default ())
        :param signal: `numpy` vector with values
        :param index: current index
        :param kwargs: other keyword arguments
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
            
        # call super
        super().set(exclude, **kwargs)

    def read(self):
        """
        Read from *Signal*.

        Reading increments current `index`.

        If `repeat` is True, `index` becomes `0` after end of `signal`.
        """

        # read signal sequentially
        
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

        # call super
        return super().read()

class Interp(BufferBlock):
    """
    A *Interp* block outputs values of a vector `signal` sequentially
    each time `read` is called.

    If `repeat` is True, signal repeats periodically.

    :param xp: `numpy` array with the x-coordinates of the data points, must be increasing
    :param fp: `numpy` array with the y-coordinates
    :param left: value to return for x < xp[0] (default is fp[0]).
    :param right: value to return for x > xp[-1] (default is fp[-1]).
    :param period: a period for the x-coordinates; parameters left and right are ignored if period is specified (default None)
    """

    def __init__(self, **kwargs):

        # xp
        self.xp = numpy.array(kwargs.pop('xp', []))

        # fp
        self.fp = numpy.array(kwargs.pop('fp', []))

        # make sure they have the same dimensions
        assert self.xp.shape[0] == self.fp.shape[0]

        # left
        self.left = kwargs.pop('left', 0)

        # right
        self.right = kwargs.pop('right', 0)

        # period?
        self.period = kwargs.pop('period', None)

        super().__init__(**kwargs)

        self.xp_origin = None
        self.xp_current = None
        
    def reset(self):
        """
        Reset *Interp*. Set xp index back to its origin.
        """

        self.xp_current = self.xp_origin = None

    def set(self, exclude = (), **kwargs):
        """
        Set properties of *Interp*. 

        :param tuple exclude: list of attributes to exclude (default ())
        :param xp: `numpy` array with the x-coordinates of the data points, must be increasing
        :param fp: `numpy` array with the y-coordinates
        :param left: value to return for x < xp[0]
        :param right: value to return for x > xp[-1]
        :param period: a period for the x-coordinates; parameters left and right are ignored if period is specified
        :param kwargs: other keyword arguments
        """

        if 'xp' in kwargs:
            self.xp = numpy.array(kwargs.pop('xp'))
            self.reset()

        if 'fp' in kwargs:
            self.fp = numpy.array(kwargs.pop('fp'))
            self.reset()
            
        # make sure they have the same dimensions
        assert self.xp.shape[0] == self.fp.shape[0]

        # call super
        super().set(exclude + ('xp_current', 'xp_origin'), **kwargs)

    def write(self, *values):
        """
        Writes input to the private `buffer`.
        """

        # call super
        super().write(*values)

        # get index from buffer
        assert len(self.buffer) == 1
        self.xp_current = self.buffer[0]

        # set xp_origin if needed
        if self.xp_origin is None:
            self.xp_origin = self.xp_current
        
    def read(self):
        """
        Read from *Xp*.

        Reading increments current `index`.

        If `repeat` is True, `index` becomes `0` after end of `xp`.
        """

        # interpolate signal
        xk = interp(self.xp_current - self.xp_origin,
                    self.fp, self.xp,
                    left = self.left, right = self.right,
                    period = self.period)
            
        self.buffer = (xk,)

        # call super
        return super().read()

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

    def write(self, *values):
        """
        Writes a tuple with the result of `function` applied to each
        input to the private `buffer`.
        """

        # call super
        super().write(*values)

        # map onto buffer
        self.buffer = tuple(map(self.function, self.buffer))

class Apply(BufferBlock):
    """
    The Block *Apply* applies `function` to all inputs and returns tuple
    with the result.

    :param function: the function to be applied (default identity)
    """

    def __init__(self, **kwargs):

        # function
        self.function = kwargs.pop('function', lambda x: x)
        
        super().__init__(**kwargs)

    def write(self, *values):
        """
        Writes a tuple with the result of `function` applied to all
        inputs to the private `buffer`.
        """

        # call super
        super().write(*values)

        # apply on buffer
        self.buffer = (self.function(*self.buffer), )

class Logger(Block):
    """
    *Logger* stores signals into an array.

    :param number_of_rows: number of stored rows (default 12000)
    :param number_of_columns: number of columns (default 0)
    """

    def __init__(self,
                 number_of_rows = 12000,
                 number_of_columns = 0, 
                 **kwargs):

        # reshape
        self.reshape(number_of_rows, number_of_columns)

        # auto reset
        self.auto_reset = kwargs.pop('auto_reset', False)

        super().__init__(**kwargs)

    def get(self, *keys, exclude = ()):

        # call super
        return super().get(*keys, exclude = exclude + ('data',))

    def set(self, exclude = (), **kwargs):
        """
        Set properties of *Logger*.

        Excludes data.

        :param tuple exclude: list of attributes to exclude
        :param int current: current index
        :param int page: current page index
        :param bool auto_reset: auto reset flag
        :param kwargs: other keyword arguments
        :raise: `BlockException` if any of the `kwargs` is left unprocessed
        """

        # call super
        return super().set(exclude + ('data',), **kwargs)
    
    def reshape(self, number_of_rows, number_of_columns):

        self.data = numpy.zeros((number_of_rows, number_of_columns), float)
        self.reset()

    def reset(self):

        self.page = 0
        self.current = 0

    def get_current_page(self):
        return self.page

    def get_current_index(self):
        return self.page * self.data.shape[0] + self.current

    def get_log(self):

        # set return value
        if self.page == 0:
            retval = self.data[:self.current,:]

        else:
            retval =  numpy.vstack((self.data[self.current:,:],
                                    self.data[:self.current,:]))

        # reset after read?
        if self.auto_reset:
            self.reset()

        # return values
        return retval
    
    read = get_log
        
    def write(self, *values):

        #print('values = {}'.format(values))

        # stack first
        values = numpy.hstack(values)

        # reshape?
        if self.data.shape[1] != len(values):
            # reshape log
            self.reshape(self.data.shape[0], len(values))
        
        # Log data
        self.data[self.current, :] = values

        if self.current < self.data.shape[0] - 1:
            # increment current pointer
            self.current += 1
        else:
            # reset current pointer and increment page counter
            self.current = 0
            self.page += 1
        
