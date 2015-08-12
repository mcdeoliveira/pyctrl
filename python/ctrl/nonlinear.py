import numpy

from . import block

# Blocks

class DeadZoneInverse(block.Block):

    def __init__(self, *vars, **kwargs):
        # Wrapper for the piecewise function
        # f(x) = { x (100-y)/(100-d) + 100(y-d)/(100-d), x > d,
        #        { x (100-y)/(100-d) - 100(y-d)/(100-d), x < -d,
        #        { x (y/d),                              -d <= x <= d

        y = kwargs.pop('y', 1)
        d = kwargs.pop('d', 1)

        assert y >= 0
        assert d >= 0

        self.a = (100 - y) / (100 - d)
        self.b = 100 * (y - d) / (100 - d)
        self.c = y / d
        self.d = d

        self.output = ()

        super().__init__(*vars, **kwargs)
    
    def read(self):
        return self.output

    def write(self, values):

        # Dead-zone compensation
        x = next(values)
        if x > self.d:
            self.output = (x * self.a + self.b, )
        elif x < -self.d:
            self.output = (x * self.a - self.b, )
        else: # -d <= x <= d
            self.output = (x * self.c, )

        return self.output
