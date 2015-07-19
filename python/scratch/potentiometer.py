# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:52:23 2015

@author: Eduardo
"""

import Adafruit_BBIO.ADC as ADC
import time

ADC.setup()
print("Voltage:")

for i in range(0,10):
    value = ADC.read("AIN0")
    voltage = value * 1.5
    print(voltage)
    time.sleep(1)
