import warnings
import time

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from ..gettime import gettime as perf_counter
    #perf_counter = gettime.gettime
else:
    from time import perf_counter

from .. import block
from ..block import clock as clk

from . import util
from .eqep import eQEP

# Uses Alex Martelli's Borg for making Clock a singleton

class Clock(clk.Clock):

    _shared_state = {}

    def __init__(self, eqeps = ['EQEP2B'], *vars, **kwargs):

        # Makes sure clock is a singleton
        self.__dict__ = self._shared_state

        #print("encoder.Clock.__init__: vars {}".format(vars))
        #print("encoder.Clock.__init__: kwargs {}".format(kwargs))
        
        # Do not initialize if already initialized
        if not self.__dict__ == {}:
            warnings.warn('> Clock is already initialized. Skipping call to __init')
            return

        # call super
        super().__init__(*vars, **kwargs)

        # initialize encoders
        self.encoder = [0, 0, 0]

        # Always use EQEP2B as clock    
        if 'EQEP2B' not in eqeps:
            eqeps.append('EQEP2B')

        # initialize eqeps
        self.eqep0 = None
        self.eqep1 = None
        self.eqep2b = None
        self.initialize_eqep(eqeps)

    def initialize_eqep(self, eqeps = ['EQEP2']):

        # print("initialize_eqep: PERIOD = {}".format(self.period))
        
        if not self.eqep0 and 'EQEP0' in eqeps:

            warnings.warn('> Initializing EQEP0')

            # Load device tree
            util.load_device_tree('bone_eqep0')

            # ENC0 PINS
            # eQEP0A_in(P9_42)
            # eQEP0B_in(P9_27)
            eQEP0 = "/sys/devices/ocp.3/48300000.epwmss/48300180.eqep"

            # initialize eqep0
            self.eqep0 = eQEP(eQEP0, eQEP.MODE_ABSOLUTE)
            self.eqep0.set_period(int(self.period * 1e9))
            self.set_encoder(0, 0)

        if not self.eqep1 and 'EQEP1' in eqeps:

            warnings.warn('> Initializing EQEP1')

            # Load device tree
            util.load_device_tree('bone_eqep1')

            # ENC1 PINS
            # eQEP1A_in(P8_35)
            # eQEP1B_in(P8_33)
            eQEP1 = "/sys/devices/ocp.3/48302000.epwmss/48302180.eqep"

            # initialize eqep1
            self.eqep1 = eQEP(eQEP1, eQEP.MODE_ABSOLUTE)
            self.eqep1.set_period(int(self.period * 1e9))
            self.set_encoder(0, 1)

        if not self.eqep2b and 'EQEP2B' in eqeps:

            warnings.warn('> Initializing EQEP2B')

            # Load device tree
            util.load_device_tree('bone_eqep2b')

            # ENC2b PINS
            # eQEP2bA_in(P8_12)
            # eQEP2bB_in(P8_11)
            eQEP2b = "/sys/devices/ocp.3/48304000.epwmss/48304180.eqep"

            # initialize eqep2b
            self.eqep2b = eQEP(eQEP2b, eQEP.MODE_ABSOLUTE)
            self.eqep2b.set_period(int(self.period * 1e9))
            self.set_encoder(0, 2)

    def set_period(self, period):
        
        warnings.warn('> Setting clock period to {}s'.format(period))
            
        # call supper
        super().set_period(period)

        # set period on BBB eQEP
        self.eqep2b.set_period(int(self.period * 1e9))

    def get_encoder(self):

        return self.encoder
        
    def get_encoder(self, index):

        return self.encoder[index]

    def set_encoder(self, value, index = 2):

        if index == 0:
            self.eqep0.set_position(int(value))
            self.encoder[0] = value
        elif index == 1:
            self.eqep1.set_position(int(value))
            self.encoder[1] = value
        elif index == 2:
            self.eqep2b.set_position(int(value))
            self.encoder[2] = value
        
    def read(self):

        #print('> read')
        if self.enabled:

            # Read encoder2 (blocking call)
            self.encoder[2] = self.eqep2b.poll_position()
        
            # Read clock
            self.time = perf_counter()
            self.counter += 1

            # Read encoder0 (non-blocking)
            if self.eqep0 is not None:
                self.encoder[0] = self.eqep0.get_position()

            # Read encoder1 (non-blocking)
            if self.eqep1 is not None:
                self.encoder[1] = self.eqep1.get_position()

        return (self.time - self.time_origin, )


class Encoder(block.BufferBlock):
        
    def __init__(self, 
                 clock = Clock(), # is a singleton
                 ratio = 48 * 172, 
                 encoder = 2, *vars, **kwargs):

        # set period
        assert isinstance(clock, Clock)
        self.clock = clock

        # gear ratio
        self.ratio = ratio

        # encoder
        self.encoder = encoder

        # initialize eqep
        if encoder == 0:
            self.eqep = 'EQEP0'
        elif encoder == 1:
            self.eqep = 'EQEP1'
        elif encoder == 2:
            self.eqep = 'EQEP2B'
        else:
            raise NameException("Encoder '{}' is not defined".format(self.eqep))
        self.clock.initialize_eqep([self.eqep])

        # call super
        super().__init__(*vars, **kwargs)
        
        # output is in cycles/s
        self.buffer = (self.clock.encoder[self.encoder] / self.ratio, )

    def set(self, **kwargs):
        
        if 'ratio' in kwargs:
            self.ratio = kwargs.pop('ratio')

        super().set(**kwargs)

    def reset(self):

        self.clock.set_encoder(0, self.encoder)

    def write(self, *values):

        self.clock.set_encoder(int(values[0] * self.ratio), self.encoder)

    def read(self):

        #print('> read')
        if self.enabled:

            self.buffer = (self.clock.get_encoder(self.encoder) / self.ratio, )
        
        return self.buffer
