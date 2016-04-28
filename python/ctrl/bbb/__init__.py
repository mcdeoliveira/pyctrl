import warnings
import time
import math
import importlib

from .. import block
from ..block import clock
import ctrl

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC

from .eqep import eQEP

from . import mpu6050

# alternative perf_counter
import sys
if sys.version_info < (3, 3):
    from .. import gettime
    perf_counter = gettime.gettime
    warnings.warn('Using gettime instead of perf_counter',
                  RuntimeWarning)
else:
    import time
    perf_counter = time.perf_counter


import glob

def load_device_tree(name):

    slots = glob.glob("/sys/devices/bone_capemgr.?/slots")[0]
    #print('name = {}'.format(name))
    #print('slots = {}'.format(slots))
    
    retval = -1
    with open(slots, 'r+') as file:
        for line in file:
            #print('line = {}'.format(line))
            if line.find(name) >= 0:
                # return true if device is already loaded
                return 0

        # reached end of file: device is not loaded
        file.write(name)
        retval = 1
        
    # take a break
    time.sleep(1)

    return retval

class Clock(clock.Clock):

    def __init__(self, eqeps = ['EQEP2'], *vars, **kwargs):

        # period
        self.period = kwargs.pop('period', 0.01) # deadzone

        # call super
        super().__init__(*vars, **kwargs)

        # initialize encoders
        self.encoder = [0, 0, 0]

        if 'EQEP0' in eqeps:

            print('> Initializing EQEP0')

            # Load device tree
            load_device_tree('bone_eqep0')

            # ENC0 PINS
            # eQEP0A_in(P9_42)
            # eQEP0B_in(P9_27)
            eQEP0 = "/sys/devices/ocp.3/48300000.epwmss/48300180.eqep"

            # initialize eqep0
            self.eqep0 = eQEP(eQEP0, eQEP.MODE_ABSOLUTE)
            self.eqep0.set_period(int(self.period * 1e9))
            self.set_encoder(0, 0)

        else:
            self.eqep0 = None

        if 'EQEP1' in eqeps:

            print('> Initializing EQEP1')

            # Load device tree
            load_device_tree('bone_eqep1')

            # ENC1 PINS
            # eQEP1A_in(P8_35)
            # eQEP1B_in(P8_33)
            eQEP1 = "/sys/devices/ocp.3/48302000.epwmss/48302180.eqep"

            # initialize eqep2
            self.eqep1 = eQEP(eQEP1, eQEP.MODE_ABSOLUTE)
            self.eqep1.set_period(int(self.period * 1e9))
            self.set_encoder(0, 1)

        else:
            self.eqep1 = None

        # Always use EQEP2 as clock    

        # Load device tree
        load_device_tree('bone_eqep2b')

        # ENC2b PINS
        # eQEP2bA_in(P8_12)
        # eQEP2bB_in(P8_11)
        eQEP2 = "/sys/devices/ocp.3/48304000.epwmss/48304180.eqep"

        # initialize eqep2
        self.eqep2 = eQEP(eQEP2, eQEP.MODE_ABSOLUTE)

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))
        self.set_encoder(0, 2)

    def set_period(self, period):
        
        # call supper
        super().set_period(period)

        # set period on BBB eQEP
        self.eqep2.set_period(int(self.period * 1e9))

    def get_encoder(self):

        return self.encoder
        
    def set_encoder(self, value, index = 2):

        if index == 0:
            self.eqep0.set_position(int(value))
            self.encoder[0] = value
        elif index == 1:
            self.eqep1.set_position(int(value))
            self.encoder[1] = value
        elif index == 2:
            self.eqep2.set_position(int(value))
            self.encoder[2] = value
        
    def read(self):

        #print('> read')
        if self.enabled:

            # Read encoder2 (blocking call)
            self.encoder[2] = self.eqep2.poll_position()
        
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
        
    def __init__(self, clock, ratio = 48 * 172, eqep = 2, *vars, **kwargs):

        # set period
        assert isinstance(clock, Clock)
        self.clock = clock

        # gear ratio
        self.ratio = ratio

        # eqep
        self.eqep = eqep

        # call super
        super().__init__(*vars, **kwargs)
        
        # output is in cycles/s
        self.buffer = (self.clock.encoder[self.eqep] / self.ratio, )

    def set(self, **kwargs):
        
        if 'ratio' in kwargs:
            self.ratio = kwargs.pop('ratio')

        super().set(**kwargs)

    def reset(self):

        self.clock.set_encoder(0, self.eqep)

    def write(self, *values):

        self.clock.set_encoder(int(values[0] * self.ratio), self.eqep)

    def read(self):

        #print('> read')
        if self.enabled:

            self.buffer = (self.clock.get_encoder()[self.eqep] / self.ratio, )
        
        return self.buffer
        
class Controller(ctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # period
        self.period = kwargs.pop('period', 0.01) # deadzone

        # Initialize controller
        super().__init__(*vargs, **kwargs)

    def __reset(self):

        # call super
        super().__reset()

        # create device dictionary
        self.devices = {}

        # add source: clock
        self.clock = Clock(period = self.period,
                           eqeps = ['EQEP2', 'EQEP1'])
        self.add_source('clock', self.clock, ['clock'])
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

        # add signals
        self.add_signals('motor1', 'encoder1', 'analog1')

        # add source: encoder1
        self.encoder1 = Encoder(clock = self.clock, 
                                eqep = 2, ratio = 48 * 172)
        self.add_source('encoder1', self.encoder1, ['encoder1'])

        # add source: encoder2
        self.encoder2 = Encoder(clock = self.clock, 
                                eqep = 1, ratio = 4 * 1024)
        self.add_signal('encoder2')
        self.add_source('encoder2', self.encoder2, ['encoder2'])

        # add source: analog1
        #self.analog1 = Potentiometer()
        #self.add_source('analog1', self.analog1, ['analog1'])
        self.add_device('analog1', 
                        'ctrl.bbb.analog', 'Analog',
                        type = 'source',
                        signals = ['analog1'],
                        pin = 'AIN0',
                        full_scale = 0.85,
                        invert = True) 

        # add source: incl1
        try:
            self.incl = mpu6050.Inclinometer()

            # add source if no exceptions
            self.add_source('inclinometer1', self.incl, ['theta']) 
            self.add_signal('theta')
        except:
            self.incl = None

        # add sink: motor1
        #self.motor1 = Motor()
        #self.add_sink('motor1', self.motor1, ['motor1'])
        self.add_device('motor1', 
                        'ctrl.bbb.motor', 'Motor',
                        type = 'sink',
                        strtstp = True,
                        signals = ['motor1'],
                        pwm_pin = 'P9_14',
                        dir_A = 'P9_15',
                        dir_B = 'P9_23') 


    def add_device(self, 
                   label, device_module, device_class, 
                   **kwargs):

        # period
        device_type = kwargs.pop('type', 'source')
        device_signals = kwargs.pop('signals', [])
        device_strtstp = kwargs.pop('strtstp', False)

        try:

            # create device
            obj_class = getattr(importlib.import_module(device_module), 
                                device_class)
            instance = obj_class(**kwargs)

        except:

            # rethrow
            raise 

        # store device
        self.devices[label] = {
            'instance': instance,
            'devtype': device_type,
            'signals': device_signals,
            'strtstp': device_strtstp
        }

        # create device
        if device_type == 'source':

            # add device as source
            self.add_source(label, instance, device_signals)

        elif device_type == 'sink':

            # add device as source
            self.add_sink(label, instance, device_signals)

        else:
            
            raise NameError("Unknown device type '{}'. Must be sink, source or filter.".format(device_type))

    def stop(self):

        # stop
        super().stop()

        # then disable devices
        for label, device in self.devices.items():
            if device['strtstp']:
                device['instance'].set_enabled(False)

        # then disable motor
        #self.motor1.set_enabled(False)

    def start(self):

        # enable devices
        for label, device in self.devices.items():
            if device['strtstp']:
                device['instance'].set_enabled(True)

        # enable motor
        #self.motor1.set_enabled(True)

        # then start
        super().start()

    # period
    def set_period(self, value):
        self.period = value

    def get_period(self):
        return self.period
