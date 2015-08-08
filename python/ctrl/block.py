class BlockException(Exception):
    pass

class Block:
    
    def __init__(self, enabled  = True):
        self.enabled = enabled

    def is_enabled(self):
        return self.enabled
        
    def set_enabled(self, enabled  = True):
        self.enabled = enabled

    def read(self):
        raise BlockException('This block does not support read')

    def write(self, values):
        raise BlockException('This block does not support write')

class Printer(Block):

    def __init__(self, *vars, **kwargs):

        self.endln = kwargs.pop('endln', '\n')
        self.format_ = kwargs.pop('format', '{:12.2f}')
        self.join_ = kwargs.pop('join', ' ')

        super().__init__(*vars, **kwargs)
    
    def write(self, values):

        print(self.join_.join(self.format_.format(val) for val in values), 
              end=self.endln)

class Gain(Block):

    def __init__(self, *vars, **kwargs):

        self.gain = kwargs.pop('gain', 1)
        self.output = ()

        super().__init__(*vars, **kwargs)
    
    def read(self):
        return self.output

    def write(self, values):
        self.output = [value*self.gain for value in values]

class ShortCircuit(Block):

    def __init__(self, *vars, **kwargs):

        self.output = ()

        super().__init__(*vars, **kwargs)
    
    def read(self):
        return self.output

    def write(self, values):
        self.output = values

class Feedback(Block):

    def __init__(self, *vars, **kwargs):
        """
        Feedback connection:
            u = block (error), 
        error = gamma * ref - y
        
        inputs = (y, ref)
        output = (u, )
        """
        self.gamma = kwargs.pop('gamma', 100)/100
        self.block = kwargs.pop('block', ShortCircuit())
        self.output = ()

        super().__init__(*vars, **kwargs)
    
    def read(self):
        return self.output

    def write(self, values):
        error = self.gamma * values[1] - values[0]
        self.block.write((error, ))
        self.output = self.block.read()

class Differentiator(Block):

    def __init__(self, *vars, **kwargs):
        """
        Differentiator
        inputs: clock, signal
        output: derivative"""
        
        self.time = -1
        self.last = ()
        self.output = ()

        super().__init__(*vars, **kwargs)
    
    def read(self):
        return self.output

    def write(self, values):

        #print('values = {}'.format(values))

        if self.time > 0:
            dt = values[0] - self.time
        else:
            dt = 0
        #print('dt = {}'.format(dt))

        if dt > 0:
            self.time, self.last, self.output = values[0], values[1:], \
                [(n-o)/dt for n,o in zip(values[1:], self.last)]
        else:
            self.time, self.last, self.output = values[0], values[1:], \
                (len(values)-1)*[0.]

        #print('self.time = {}'.format(self.time))
        #print('self.last = {}'.format(self.last))
        #print('self.output = {}'.format(self.output))
