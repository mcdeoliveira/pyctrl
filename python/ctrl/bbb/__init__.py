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

from . import mpu6050
from . import util
from . import encoder

class Controller(ctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # period
        self.period = kwargs.pop('period', 0.01)

        # Initialize controller
        super().__init__(*vargs, **kwargs)

    def __reset(self):

        # call super
        super().__reset()

        # add source: clock
        self.clock = encoder.Clock(period = self.period,
                                   eqeps = ['EQEP2', 'EQEP1'])
        self.add_source('clock', self.clock, ['clock'])
        self.signals['clock'] = self.clock.time
        self.time_origin = self.clock.time_origin

        # add signals
        self.add_signals('motor1', 'encoder1', 'analog1')

        # add source: encoder1
        self.encoder1 = encoder.Encoder(clock = self.clock, 
                                        eqep = 2, ratio = 48 * 172)
        self.add_source('encoder1', self.encoder1, ['encoder1'])

        # add source: encoder2
        self.encoder2 = encoder.Encoder(clock = self.clock, 
                                        eqep = 1, ratio = 4 * 1024)
        self.add_signal('encoder2')
        self.add_source('encoder2', self.encoder2, ['encoder2'])

        # add source: analog1
        #self.analog1 = Potentiometer()
        #self.add_source('analog1', self.analog1, ['analog1'])
        self.add_device('analog1', 
                        'ctrl.bbb.analog', 'Analog',
                        type = 'source',
                        outputs = ['analog1'],
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
                        enable = True,
                        inputs = ['motor1'],
                        pwm_pin = 'P9_14',
                        dir_A = 'P9_15',
                        dir_B = 'P9_23') 

    # period
    def set_period(self, value):
        self.period = value

    def get_period(self):
        return self.period
