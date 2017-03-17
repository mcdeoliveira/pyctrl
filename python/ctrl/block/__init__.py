"""
This module provides the basic building blocks for implementing controllers.
"""

import contextlib
import numpy

class BlockException(Exception):
    pass

class Block:
    """
    *Block* provides the basic functionality for all types of blocks.
    """
    
    def __init__(self, *vars, **kwargs):
        """
        Constructs a new *Block* object.

        It does not take any parameters other than *enable* and will
        raise *BlockException* if any of the *vars* or *kwargs* is
        left unprocessed.
        
        :param enable: set block as enabled (default True)
        """
        
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
        Read from *Block*

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
        """
        Constructs a new *BufferBlock* object.
        """
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
    A *Printer* blocks prints the values of signals to the screen.
    """
    def __init__(self, *vars, **kwargs):
        """
        Constructs a new *Printer* object.

        :param endl: end-of-line character 
        :param frmt: 
        :param sep: 
        """
        self.endln = kwargs.pop('endln', '\n')
        self.frmt = kwargs.pop('frmt', '{: 12.4f}')
        self.sep = kwargs.pop('sep', ' ')

        super().__init__(*vars, **kwargs)

    def set(self, **kwargs):

        if 'endln' in kwargs:
            self.endln = kwargs.pop('endln')
        
        if 'frmt' in kwargs:
            self.frmt = kwargs.pop('frmt')

        if 'sep' in kwargs:
            self.sep = kwargs.pop('sep')

        super().set(**kwargs)
    
    def write(self, *values):

        if self.enabled:

            @contextlib.contextmanager
            def printoptions(*args, **kwargs):
                original = numpy.get_printoptions()
                numpy.set_printoptions(*args, **kwargs)
                yield 
                numpy.set_printoptions(**original)

            row = numpy.hstack(values)
            print(self.sep.join(self.frmt.format(val) for val in row), 
                  end=self.endln)


class Signal(Block):

    def __init__(self, x, repeat = False, *vars, **kwargs):
        """Block with signal
        """

        # signal
        assert isinstance(x, numpy.ndarray)
        self.x = x

        # repeat?
        self.repeat = repeat

        # index
        self.k = 0
       
        super().__init__(*vars, **kwargs)

    def reset(self):

        self.k = 0

    def set(self, **kwargs):

        if 'x' in kwargs:
            self.x = kwargs.pop('x')
            self.reset()
        
        super().set(**kwargs)

    def read(self, *values):

        # return 0 if over the edge
        if self.k >= len(self.x):

            xk = 0 * self.x[0]

        else:

            # get entry
            xk = self.x[self.k]
            
            # increment
            self.k += 1
            
            if self.repeat and self.k == len(self.x):

                # reset
                self.k = 0
        
        return (xk, )


class Map(BufferBlock):
    """
    The Block Map applies 'function' to each input and returns tuple
    with results.
    """

    def __init__(self, function = (lambda x: x), *vars, **kwargs):
        """
        Constructs a new *Map* object.

        :param function: the function to be applied
        """

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
    """

    def __init__(self, function = (lambda x: x), *vars, **kwargs):
        """
        Constructs a new *Apply* object.

        :param function: the function to be applied
        """

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
            self.buffer = tuple(self.function(*values))

