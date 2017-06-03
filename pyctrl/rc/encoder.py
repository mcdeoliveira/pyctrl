import pyctrl.block as block

import rcpy
import rcpy.encoder as encdr

class Encoder(block.BufferBlock):
        
    def __init__(self, **kwargs):
        
        # gear ratio
        self.ratio = float(kwargs.pop('ratio', 48 * 172))

        # encoder
        self.encoder = kwargs.pop('encoder', 2)

        # call super
        super().__init__(**kwargs)
        
    def set(self, **kwargs):

        if 'ratio' in kwargs:
            # make sure ratio is a float
            self.ratio = float(kwargs.pop('ratio'))

        # call super
        super().set(**kwargs)
        
    def reset(self):

        encdr.set(self.encoder, 0)

    def write(self, *values):

        assert len(values) == 1
        encdr.set(self.encoder, int(values[0] * self.ratio))

    def read(self):

        #print('> read')
        if self.enabled:

            self.buffer = (encdr.get(self.encoder) / self.ratio, )
        
        return self.buffer

if __name__ == "__main__":

    import pyctrl
    
    import time, math
    from time import perf_counter
    import itertools

    T = 0.04
    K = 1000

    print("\n> Testing Encoder")

    e1 = Encoder(encoder = 1)
    e2 = Encoder(encoder = 2)
    e3 = Encoder(encoder = 3)
    e4 = Encoder(encoder = 4)
    
    print('\n ENC #1 |  ENC #2 |  ENC #3 |  ENC #4')
    
    N = 10
    for k in range(N):

        print('\r{:7.3f} | {:7.3f} | {:7.3f} | {:7.3f}'.format(*itertools.chain(e1.read(),
                                                                                e2.read(),
                                                                                e3.read(),
                                                                                e4.read())),
              end='')

        time.sleep(1)
