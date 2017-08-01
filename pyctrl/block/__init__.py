"""
This module provides the basic building blocks for implementing controllers.
"""

import warnings
import contextlib
import numpy, math
import sys
import json
import itertools

from enum import Enum

np_major, np_minor, np_release = numpy.version.version.split('.')
if int(np_major) == 1 and int(np_minor) >= 10:

    # can handle period
    #print('CAN HANDLE PERIOD')
    interp = numpy.interp

else:

    # handle period
    def interp(x,xp,fp,left,right,period):
        if period:
            return numpy.interp(numpy.mod(x,period), xp, fp, left, right)
        else:
            return numpy.interp(x, xp, fp, left, right)

class BlockType(Enum):
    source = 0
    filter = 1
    sink = 2
    timer = 3
        
class BlockException(Exception):
    """
    Exception class for blocks
    """
    pass

class BlockWarning(Warning):
    """
    Warning class for blocks
    """
    pass

class Source:

    """
    Base class for all source blocks.
    """
    
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
    
    def get_type(self):
        """
        Get block :py:attr:`type`. :py:attr:`type` is a member of class :py:class:`pyctrl.block.BlockType`

        :return: :py:attr:`type`
        """
        return BlockType.source

    def write(self, *values):
        """
        Write to :py:class:`pyctrl.block.Block`.

        :param vararg values: values
        :raise: :py:class:`pyctrl.block.BlockException` if block does not support write
        """
        raise BlockException('This block does not support write')

class Sink:

    """
    Base class for all sink blocks.
    """
    
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
    
    def get_type(self):
        """
        Get block :py:attr:`type`. :py:attr:`type` is a member of class :py:class:`pyctrl.block.BlockType`

        :return: :py:attr:`type`
        """
        return BlockType.sink

    def read(self):
        """
        Read from :py:class:`pyctrl.block.Block`.

        :return: values
        :retype: tuple
        :raise: :py:class:`pyctrl.block.BlockException` if block does not support read
        """
        raise BlockException('This block does not support read')
    
class Filter:

    """
    Base class for all filter blocks.
    """
    
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
    
    def get_type(self):
        """
        Get block :py:attr:`type`. :py:attr:`type` is a member of class :py:class:`pyctrl.block.BlockType`

        :return: :py:attr:`type`
        """
        return BlockType.filter
    
class Block:
    """
    :py:class:`pyctrl.block.Block` provides the basic functionality for all types of blocks.
        
    :py:class:`pyctrl.block.Block` does not take any parameters other than :py:attr:`enable`
        
    :param bool enable: set block as enabled (default True)
    :param kwargs kwargs: additional keyword arguments
    :raise: :py:class:`pyctrl.block.BlockException` if any of the :py:data:`kwargs` is left unprocessed
    """
    
    def __init__(self, **kwargs):
        
        self.enabled = kwargs.pop('enabled', True)
        self.parent = kwargs.pop('parent', None)

        if len(kwargs) > 0:
            raise BlockException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

    def is_enabled(self):
        """
        Return :py:attr:`enabled` state.

        :return: :py:attr:`enabled`
        """
        return self.enabled
    
    def set_enabled(self, enabled  = True):
        """
        Set :py:attr:`enabled` state.

        :param bool enabled: True or False (default True)
        """
        self.enabled = enabled

    def set_parent(self, parent):
        """
        Set :py:attr:`controlller` reference.

        :param :py:class:`pyctrl.block.containter.Container` parent: parent container
        """
        self.parent = parent

    def get_parent(self):
        """
        Get :py:attr:`controlller` reference.

        :return: :py:attr:`parent`
        """
        return self.parent

    def reset(self):
        """
        Reset :py:class:`pyctrl.block.Block`.

        Does nothing here but allows another :py:class:`pyctrl.block.Block` to reset itself.
        """
        pass

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.Block`.

        :param tuple exclude: attributes to exclude (default ())
        :param bool reset: if True calls :py:meth:`reset`
        :param bool enabled: set enabled attribute
        :param pyctrl.block.container.Container parent: set parent attribute
        :param kwargs kwargs: other keyword arguments
        :raise: :py:class:`pyctrl.block.BlockException` if any of the kwargs is left unprocessed
        """

        if 'reset' in kwargs:
            if kwargs.pop('reset'):
                self.reset()

        if 'enabled' in kwargs:
            self.set_enabled(kwargs.pop('enabled'))

        # add parent to list of excluded properties
        exclude += ('parent',)
        
        for k in kwargs:
            if k in exclude or k not in self.__dict__:
                raise BlockException("Does not know how to set attribute '{}'".format(kwargs))
            else:
                # set attribute
                setattr(self, k, kwargs.get(k))

    def get(self, *keys, exclude = ()):
        """
        Get properties of blocks. For example:

        :samp:`block.get('enabled')`

        will retrieve the value of the property :py:attr:`enabled`. Returns a
        tuple with key values if argument :py:attr:`keys` is a list.

        :param keys: string or tuple of strings with property names
        :param tuple exclude: tuple with keys never to be returned (Default ())
        :raise: :py:class:`KeyError` if :py:attr:`key` is not defined
        """

        #print('> keys = {}'.format(keys))

        # add parent to list of excluded properties
        exclude += ('parent',)
        
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

    def html(self, *keys):
        """
        Format :py:class:`pyctrl.block.Block` in HTML.

        By default uses the result of :py:meth:`pyctrl.block.Block.get`.

        :param keys: string or tuple of strings with property names
        :raise: :py:class:`KeyError` if :py:attr:`key` is not defined
        """

        result = '<dl>'
        for (k,v) in self.get().items():
            result += '<dt>' + str(k) + '</dt>'
            result +=  '<dd>' + str(v) + '</dd>'
        result += '</dl>'

        return result
        
    def read(self):
        """
        Read from :py:class:`pyctrl.block.Block`.

        :return: values
        :retype: tuple
        :raise: :py:class:`pyctrl.block.BlockException` if block does not support read
        """
        raise BlockException('This block does not support read')

    def write(self, *values):
        """
        Write to :py:class:`pyctrl.block.Block`.

        :param vararg values: values
        :raise: :py:class:`pyctrl.block.BlockException` if block does not support write
        """
        raise BlockException('This block does not support write')

class BufferBlock(Block):
    """
    :py:class:`pyctrl.block.BufferBlock` provides the basic functionality for blocks that
    implement :py:class:`pyctrl.block.Block.read` and :py:class:`pyctrl.block.Block.write` through a local buffer :py:attr:`buffer`. 

    A :py:class:`pyctrl.block.BufferBlock` has the property :py:attr:`buffer`.
    
    Writing to a :py:class:`pyctrl.block.BufferBlock` writes to the :py:attr:`buffer`.

    Reading from a :py:class:`pyctrl.block.BufferBlock` reads from the :py:attr:`buffer`.

    Multiplexing and demultiplexing options are available.

    If :py:attr:`mux` is False (:py:attr:`demux` is False) then :py:meth:`pyctrl.block.BufferBlock.read` (:py:meth:`pyctrl.block.BufferBlock.write`) are
    simply copied to (from) the :py:attr:`buffer`.

    If :py:attr:`mux` is True then :py:meth:`pyctrl.block.BufferBlock.read` writes a numpy array with the
    contents of :py:data`*values` to :py:attr:`buffer`.

    If :py:attr:`demux` is True then :py:meth:`pyctrl.block.BufferBlock.write` splits :py:attr:`buffer` into a tuple
    with scalar entries.

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
        Get properties of a :py:class:`pyctrl.block.BufferBlock`.

        This method excludes :py:attr:`buffer` from the list of properties. 

        :param keys: string or tuple of strings with property names
        :param tuple exclude: tuple with keys never to be returned (Default ())
        """
        # call super
        return super().get(*keys, exclude = exclude + ('buffer',))
        
    def set(self, exclude = (), **kwargs):
        """
        Set properties of a :py:class:`pyctrl.block.BufferBlock`.

        This method excludes :py:attr:`buffer` from the list of properties. 

        :param tuple exclude: attributes to exclude (default ())
        :param kwargs kwargs: other keyword arguments
        """
        
        # call super
        return super().set(exclude + ('buffer',), **kwargs)

    def write(self, *values):
        """
        Writes to the private :py:attr:`buffer` property.

        If :py:attr:`mux` is False then `*values` are simply copied to the
        :py:attr:`buffer`.

        If :py:attr:`mux` is True then `*values` writes a numpy array with the
        contents of `*values` to the first entry of :py:attr:`buffer`.

        :param vararg values: list of values
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
        Returns the private :py:attr:`buffer` property.

        If :py:attr:`demux` is False then read returns a copy of the local :py:attr:`buffer`. 

        If :py:attr:`demux` is True then :py:attr:`buffer` is split into a tuple with
        scalar entries.

        :returns: :py:attr:`buffer`
        """
        if self.enabled:

            # return buffer
            if self.buffer and self.demux:
                self.buffer = tuple(numpy.hstack(self.buffer).tolist())
                
            return self.buffer

        # else

        return (None, )

class ShortCircuit(Filter, BufferBlock):
    """
    :py:class:`pyctrl.block.ShortCircuit` copies input to the output, that is

    :math:`y = u`
    """

class Printer(Sink, Block):
    """
    :py:class:`pyctrl.block.Printer` prints the values of its input signals.

    :param str endln: end-of-line character (default `'\\\\n'`)
    :param str frmt: format string (default `{: 12.4f}`)
    :param str sep: field separator (default `' '`)
    :param str message: message to print (default `None`)
    :param file file: file to print on (default `sys.stdout`)
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
        Set properties of :py:class:`pyctrl.block.Printer`.

        :param tuple exclude: attributes to exclude (default ())
        :param str endl: end-of-line character
        :param str frmt: format string
        :param str sep: field separator
        :param str message: message to print
        :param file file: file to print on
        :param kwargs kwargs: other keyword arguments
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

class Constant(Source, BufferBlock):
    """
    :py:class:`pyctrl.block.Constant` outputs a constant.
    
    :param value: constant
    """

    def __init__(self, **kwargs):

        self.value = kwargs.pop('value', 1)
        
        super().__init__(**kwargs)

        if isinstance(self.value, (tuple, list)):
            self.buffer = self.value
        else:
            self.buffer = (self.value, )

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.Constant`. 

        :param tuple exclude: attributes to exclude (default ())
        :param value: value or list with values
        :param kwargs kwargs: other keyword arguments
        """

        if 'value' in kwargs:
            self.value = numpy.array(kwargs.pop('value'))
            if isinstance(self.value, (tuple, list)):
                self.buffer = self.value
            else:
                self.buffer = (self.value, )
            
        # call super
        super().set(exclude, **kwargs)
    
class Signal(Source, BufferBlock):
    """
    :py:class:`pyctrl.block.Signal` outputs values corresponding to its attribute :py:attr:`signal` sequentially each time :py:meth:`pyctrl.block.BufferBlock.read` is called.
    
    If :py:attr:`repeat` is True, signal repeats periodically.

    :param signal: :py:class:`numpy.ndarray` or list with values
    :param bool repeat: if True then signal repeats periodically
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
        Reset :py:class:`pyctrl.block.Signal` index back to :py:data:`0`.
        """

        self.index = 0

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.Signal`. 

        :param tuple exclude: attributes to exclude (default ())
        :param signal: :py:class:`numpy.ndarray` or list with values
        :param bool repeat: if True then signal repeats periodically
        :param kwargs kwargs: other keyword arguments
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
        """Read from :py:class:`pyctrl.block.Signal`.

        If :py:attr:`repeat` is True, :py:attr:`index` becomes
        :py:data:`0` after end of :py:attr:`signal`.

        :return: current value of :py:attr:`signal` and increments current :py:attr:`index`.
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

class Interp(Filter, BufferBlock):
    """
    :py:class:`pyctrl.block.Interp` outputs values of a vector :py:attr:`fp` interpolated according to the vector :py:attr:`xp` each time :py:meth:`pyctrl.block.BufferBlock.read` is called.

    If :py:attr:`repeat` is True, signal repeats periodically.

    :param xp: :py:class:`numpy.ndarray` or list with the x-coordinates of the data points, must be increasing
    :param fp: :py:class:`numpy.ndarray` or list with the y-coordinates
    :param float left: value to return for x < xp[0] (default is fp[0]).
    :param float right: value to return for x > xp[-1] (default is fp[-1]).
    :param float period: a period for the x-coordinates; parameters left and right are ignored if period is specified (default None)
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
        """Reset :py:class:`pyctrl.block.Interp` so that the input of the next
        call to :py:meth:`pyctrl.block.Signal.read` become the origin.
        """

        self.xp_current = self.xp_origin = None

    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.Interp`. 

        :param tuple exclude: attributes to exclude (default ())
        :param xp: :py:class:`numpy.ndarray` or list with the x-coordinates of the data points, must be increasing
        :param fp: :py:class:`numpy.ndarray` or list with the y-coordinates
        :param float left: value to return for x < xp[0]
        :param float right: value to return for x > xp[-1]
        :param float period: a period for the x-coordinates; parameters left and right are ignored if period is specified
        :param kwargs kwargs: other keyword arguments
        """

        changes = False
        
        if 'xp' in kwargs:
            self.xp = numpy.array(kwargs.pop('xp'))
            changes = True

        if 'fp' in kwargs:
            self.fp = numpy.array(kwargs.pop('fp'))
            changes = True

        if changes:
            self.reset()
            
        # make sure they have the same dimensions
        assert self.xp.shape[0] == self.fp.shape[0]

        # call super
        super().set(exclude + ('xp_current', 'xp_origin'), **kwargs)

    def write(self, *values):
        """
        Writes input to the private :py:attr:`buffer`. Input is the interpolating variable.
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
        Read from :py:class:`pyctrl.block.Interp`.

        :return: current interpolated value using :py:meth:`numpy.iterp`.
        """

        # interpolate signal
        xk = interp(self.xp_current - self.xp_origin,
                    self.fp, self.xp,
                    left = self.left, right = self.right,
                    period = self.period)
            
        self.buffer = (xk,)

        # call super
        return super().read()

class Fade(Filter, BufferBlock):
    """
    :py:class:`pyctrl.block.FadeIn` outputs values of a vector :py:attr:`fp` interpolated according to the vector :py:attr:`xp` each time :py:meth:`pyctrl.block.BufferBlock.read` is called.

    If :py:attr:`repeat` is True, signal repeats periodically.

    :param float period: a period for the x-coordinates; parameters left and right are ignored if period is specified (default None)
    """

    def __init__(self, **kwargs):

        # target
        target = kwargs.pop('target', [])
        if numpy.isscalar(target):
            target = [target]
        self.target = numpy.array(target)

        # period
        self.period = kwargs.pop('period')

        # direction
        self.direction = kwargs.pop('direction', 'in').lower()
        
        super().__init__(**kwargs)

        # xp and fp
        self.xp = numpy.array([0, self.period])
        if self.direction == 'in':
            self.fp = numpy.array([0, 1])
        elif self.direction == 'out':
            self.fp = numpy.array([1, 0])
        else:
            raise BlockException("Unknown direction; must be 'in' or 'out'")
            
        self.xp_origin = None
        self.xp_current = None
        
    def reset(self):
        """Reset :py:class:`pyctrl.block.Interp` so that the input of the next
        call to :py:meth:`pyctrl.block.Signal.read` become the origin.
        """

        self.xp_current = self.xp_origin = None

        if self.direction == 'in':
            self.fp = numpy.array([0, 1])
        elif self.direction == 'out':
            self.fp = numpy.array([1, 0])
        else:
            raise BlockException("Unknown direction; must be 'in' or 'out'")
        
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.Interp`. 

        :param tuple exclude: attributes to exclude (default ())
        :param float period: a period for the x-coordinates; parameters left and right are ignored if period is specified
        :param kwargs kwargs: other keyword arguments
        """

        changes = False
        
        if 'target' in kwargs:
            self.target = numpy.array(kwargs.pop('target'))
            changes = True

        if 'period' in kwargs:
            self.period = numpy.array(kwargs.pop('fp'))
            changes = True

        if 'direction' in kwargs:
            self.direction = kwargs.pop('direction')
            changes = True
            
        if changes:
            self.reset()
            
        # call super
        super().set(exclude + ('xp', 'fp', 'xp_current', 'xp_origin'), **kwargs)

    def get(self, *keys, exclude = ()):

        # call super
        return super().get(*keys,
                           exclude = exclude + ('xp', 'fp', 'xp_current', 'xp_origin'))
        
    def write(self, *values):
        """
        Writes input to the private :py:attr:`buffer`. First input is the interpolating variable.
        """

        # call super
        super().write(*values)

        # get index from buffer
        self.xp_current = self.buffer[0]

        # set xp_origin
        if self.xp_origin is None:
            
            self.xp_origin = self.xp_current
            
            if not len(self.target):
                self.target = (len(self.buffer) - 1) * [0]
                
    def read(self):
        """
        Read from :py:class:`pyctrl.block.Signal`.

        :return: current interpolated value using :py:meth:`numpy.iterp`.
        """

        if self.xp_current - self.xp_origin <= self.period:
            # interpolate signal
            x = self.xp_current - self.xp_origin
            f = numpy.interp(x, self.xp, self.fp)
            self.buffer = tuple(f*y+(1-f)*o for (o,y) in zip(self.target,self.buffer[1:]))
        elif self.direction == 'in':
            self.buffer = self.buffer[1:]
        elif self.direction == 'out':
            self.buffer = self.target
        
        # call super
        return super().read()
    
class Map(Filter, BufferBlock):
    """
    A :py:class:`pyctrl.block.Map` block applies 'function' to each input and returns tuple
    with results.

    :param function: the function to be applied (default identity)
    """

    def __init__(self,  **kwargs):

        # function
        self.function = kwargs.pop('function', lambda x: x)
        
        super().__init__(**kwargs)

    def write(self, *values):
        """
        :py:class:`pyctrl.block.Map` write.

        :return: tuple with the result of :py:attr:`function` applied to each input.
        """

        # call super
        super().write(*values)

        # map onto buffer
        self.buffer = tuple(map(self.function, self.buffer))

class Apply(Filter, BufferBlock):
    """
    The Block :py:class:`pyctrl.block.Apply` applies :py:attr:`function`
    to all inputs and returns a tuple with the result.

    :param function: the function to be applied (default identity)
    """

    def __init__(self, **kwargs):

        # function
        self.function = kwargs.pop('function', lambda x: x)
        
        super().__init__(**kwargs)

    def write(self, *values):
        """
        :py:class:`pyctrl.block.Apply` write.

        :return: tuple with the result of :py:attr:`function` applied to all inputs.
        """

        # call super
        super().write(*values)

        # apply on buffer
        self.buffer = (self.function(*self.buffer), )

class Logger(Sink, Block):
    """
    :py:class:`pyctrl.block.Logger` stores signals into an array.

    :param int number_of_rows: number of stored rows (default 12000)
    :param int number_of_columns: number of columns (default 0)
    :param list labels: list with labels
    :param bool auto_reset: auto reset flag
    """

    def __init__(self,
                 number_of_rows = 12000,
                 number_of_columns = 0, 
                 **kwargs):

        # reshape
        self.reshape(number_of_rows, number_of_columns)

        # auto reset
        self.auto_reset = kwargs.pop('auto_reset', False)

        # labels
        self.labels = kwargs.pop('labels', None)
        self.index = None
        
        super().__init__(**kwargs)

    def set_parent(self, parent):

        # call super
        super().set_parent(parent)

        # look for labels
        if self.parent and isinstance(self.parent, container.Container):
            label = self.parent.find_sink(self)
            if not label:
                raise BlockException("Could not locate Logger in parent")
            self.labels = self.parent.sinks[label]['inputs']
        
    def get(self, *keys, exclude = ()):
        """
        Get properties of :py:class:`pyctrl.block.Logger`.

        The special key `log` can be used to retrieve the current
        stored entries. It calls the method
        :py:meth:`pyctrl.block.Logger.get_log`.

        :param keys: string or tuple of strings with property names
        :param tuple exclude: tuple with keys never to be returned (Default ())
        :raise: :py:class:`KeyError` if :py:attr:`key` is not defined

        """

        has_log = False
        if 'log' in keys:
            # temporarily add 'log' to attributes
            self.log = self.get_log()
            has_log = True

        # call super
        retval = super().get(*keys, exclude = exclude + ('data',))
            
        if has_log:
            # exclude log from attributes
            del self.log

        return retval
            
    def set(self, exclude = (), **kwargs):
        """
        Set properties of :py:class:`pyctrl.block.Logger`.

        :param list labels: list with labels
        :param bool auto_reset: auto reset flag
        :param tuple exclude: attributes to exclude
        :param kwargs kwargs: other keyword arguments
        :raise: `BlockException` if any of the :py:data:`kwargs` is left unprocessed
        """

        if 'labels' in kwargs:
            self.labels = kwargs.pop('labels')
        
        # call super
        return super().set(exclude + ('data',), **kwargs)
    
    def reshape(self, number_of_rows, number_of_columns):

        self.data = numpy.zeros((number_of_rows, number_of_columns), float)
        self.reset()

    def reset(self):

        self.page = 0
        self.current = 0
        self.index = None

    def get_current_page(self):
        return self.page

    def get_current_index(self):
        return self.page * self.data.shape[0] + self.current

    def get_log(self):
        """
        Retrieve current entries of :py:class:`pyctrl.block.Logger`.

        If property `labels` is set return entries as a dictionary
        with keys from `labels`.

        If property `labels` is `None` return entries in an array
        where each column correspond to an input. Inputs which are
        vectors are flattened.

        :return: dictionary or numpy array with current entries.
        """
        
        # set return value
        if self.page == 0:
            retval = self.data[:self.current,:]

        else:
            retval =  numpy.vstack((self.data[self.current:,:],
                                    self.data[:self.current,:]))

        # reset after read?
        index = self.index
        if self.auto_reset:
            self.reset()

        # labels?
        if self.labels:
            if index:
                retval = {l: retval[:,index[i]:index[i+1]]
                          for (i,l) in enumerate(self.labels)}
            else:
                retval = {l: numpy.empty((0,1))
                          for (i,l) in enumerate(self.labels)}
            
        # return values
        return retval
    
    # read = get_log

    def len(value):
        try:
            return len(value)
        except:
            return 1
    
    def write(self, *values):

        # stack first
        stack_values = numpy.hstack(values)

        # reshape?
        if self.data.shape[1] != len(stack_values):
            # reshape log
            self.reshape(self.data.shape[0], len(stack_values))

        # recalculate index?
        if self.index is None and self.labels is not None :
            assert len(self.labels) == len(values)
            dims = tuple(Logger.len(x) for x in values)
            self.index = (0,) + tuple(itertools.accumulate(dims))
        
        # Log data
        self.data[self.current, :] = stack_values

        if self.current < self.data.shape[0] - 1:
            # increment current pointer
            self.current += 1
        else:
            # reset current pointer and increment page counter
            self.current = 0
            self.page += 1
        
class Wrap(Filter, BufferBlock):
    """
    :py:class:`pyctrl.block.Wrap` attempt to make a possible
    discontinuous angular signal into a continuous one.

    Use the attribute `scaling` to change units. Default is radians.

    :param int turns: the current number of turns
    :param float theta: current unwraped value of the signal
    :param int threshold: the threshold to use when deciding whether a discontinuity has been reached (Default 0.25 * scaling) 
    :param float scaling: scaling factor (default 2*pi)
    """

    def __init__(self, **kwargs):

        # turns initialization
        self.turns = kwargs.pop('turns', 0)
        self.scaling = kwargs.pop('scaling', 2*math.pi)
        self.threshold = kwargs.pop('threshold', 0.25*self.scaling)
        self.theta = kwargs.pop('theta', 0)

        # call super
        super().__init__(**kwargs)

        self.first = True

    def reset(self):

        self.turns = 0
        self.first = True
        
    def read(self):

        #print('> read')
        if self.enabled:

            # get theta
            theta = self.buffer[0]

            if self.first:
                self.first = False
                
            else:

                # jump?
                if (numpy.fabs(theta - self.theta) > self.threshold):
                    if theta > self.theta:
                        self.turns -= 1
                    else: 
                        self.turns += 1
                        
            self.theta = theta

            # units (turns) and (1/s)
            self.buffer = (self.scaling * self.turns + theta, )
        
        # call super
        return super().read()
