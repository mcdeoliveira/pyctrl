# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 21:12:09 2015

@author: Eduardo
"""
from eqep import eQEP
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time
import sys

dir_A="P9_15"
dir_B="P9_23"
pwm_A="P9_14"
pwm_B="P9_16"

nperiod = 5000000
period = nperiod / 1e9

eQEP2="/sys/devices/ocp.3/48304000.epwmss/48304180.eqep"    #eQEP2A_in(P8_12)
eqep2=eQEP(eQEP2,eQEP.MODE_ABSOLUTE)                   #eQEP2B_in(P8_11)
eqep2.set_period(nperiod)

PWM.start(pwm_A)
GPIO.setup(dir_A,GPIO.OUT)
GPIO.setup(dir_B,GPIO.OUT)
encoder=eqep2.poll_position

print ("RIGHT")

with open('data.csv', 'w') as file:


    GPIO.output(dir_A,1)
    GPIO.output(dir_B,0)
    PWM.set_duty_cycle(pwm_A,100)
        
    x0 = (encoder()/(48*9.68))
    t = 0

    for i in range(int(10/period)):
        x = (encoder()/(48*9.68))
        t = t + period
        speed = (x-x0) / period

        file.write('{0:5.4f}\t {1:5.4f} \n'.format(t,speed))            
        x0 = x

    PWM.set_duty_cycle(pwm_A,0)
    time.sleep(1)