class BlockException(Exception):
    pass

class Block:
    
    def __init__(self, *vars, **kwargs):

        self.enabled = kwargs.pop('enabled', True)

        if len(vars) > 0:
            raise BlockException("Unknown parameter(s) '{}'".format(', '.join(str(v) for v in vars)))
        elif len(kwargs) > 0:
            raise BlockException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

    def is_enabled(self):
        return self.enabled
        
    def set_enabled(self, enabled  = True):
        self.enabled = enabled

    def reset(self):
        pass

    def set(self, **kwargs):

        if 'reset' in kwargs:
            if kwargs.pop('reset'):
                self.reset()

        if 'enabled' in kwargs:
            self.set_enabled(kwargs.pop('enabled'))
            
        if len(kwargs) > 0:
            raise BlockException("Does not know how to set '{}'".format(kwargs))

    def get(self, keys = None, exclude = None):

        if keys is None or isinstance(keys, (list, tuple)):
            if keys is None:
                retval = self.__dict__.copy()
            else:
                retval = { k : self.__dict__[k] for k in keys }
            if exclude is not None:
                for key in exclude:
                    del retval[key]
            return retval

        if exclude is None or (exclude is not None and keys not in exclude):
            return self.__dict__[keys]

        raise KeyError()

    def read(self):
        raise BlockException('This block does not support read')

    def write(self, values):
        raise BlockException('This block does not support write')

class Printer(Block):

    def __init__(self, *vars, **kwargs):

        self.endln = kwargs.pop('endln', '\n')
        self.frmt = kwargs.pop('frmt', '{:12.2f}')
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
    
    def write(self, values):

        if self.enabled:

            print(self.sep.join(self.frmt.format(val) for val in values), 
                  end=self.endln)

class BufferBlock(Block):

    def __init__(self, *vars, **kwargs):
        """Block with private buffer
        """

        self.buffer = ()

        super().__init__(*vars, **kwargs)

    def get(self, keys = None, exclude = None):

        if exclude is None:
            exclude = ('buffer',)
        else:
            exclude += ('buffer',)
            
        # call super
        return super().get(keys, exclude = exclude)
        
    def read(self):

        # get buffer
        return self.buffer

