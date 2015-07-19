import time
import math
import numpy

import ctrl.algo as algo
import ctrl.sim as sim

controller = sim.Controller()

# Model is
#
# .                    .
# w + a w = b u,   w = x
#
# Units are:
#   x = cycles
#   w = cycles/s (Hz)
#
#   a = 1/tau = 17 (1/s)
# b/a =  w/u  = 11 Hz / 100 duty = 0.11 cycles/s/duty
#             a
# G(s) = k -------, k = b/a
#           s + a
#
# Zero-order hold equivalent (Ts < pi/a = 0.3):
#
#                            -1      
#           1 - c           z  (1 - c)        -a Ts
# G(z) = k ----------- = k ------------, c = e
#           z - c                -1
#                           1 - z  c
#
#                                     Ts  
# x[k] = int_{t-Ts}^t w dt = x[k-1] + --- ( w[k] + w[k-1] )
#                                      2
#                  -1
#        Ts   1 + z  
# H(z) = --- ---------
#         2        -1
#             1 - z
#                            -1           -2
#                     k Ts   z  (1 - c) + z  (1 - c)
# T(z) = H(z) G(z) = ----- -------------------------
#                      2         -1            -2
#                           1 - z   (1 + c) + z  c

Ts = 0.01              # s
a = 17                 # 1/s
k = 0.11               # cycles/s duty
c = math.exp(-a * Ts)  # adimensional

controller.set_period(Ts)
controller.set_model1( numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                       numpy.array((1, -(1 + c), c)),
                       numpy.array((0,0)) )

controller.set_echo(.1/Ts)
controller.calibrate()
controller.set_delta_mode(0)

print('> OPEN LOOP')
controller.start()
time.sleep(1)
controller.set_reference1(100)
time.sleep(1)
controller.set_reference1(-100)
time.sleep(1)
controller.set_reference1(0)
time.sleep(1)
controller.stop()

reference = 2
controller.set_controller1(
    algo.Proportional(0.09 / (k*Ts), reference / 100)
)

print('> CLOSED LOOP ON POSITION')
controller.start()
time.sleep(1)
controller.set_reference1(100)
print('\n> REFERENCE = {}'.format(reference))
time.sleep(3)
controller.set_reference1(50)
print('\n> REFERENCE = {}'.format(reference/2))
time.sleep(3)
controller.set_reference1(-50)
print('\n> REFERENCE = {}'.format(-reference/2))
time.sleep(3)
controller.stop()

reference = 11

controller.set_controller1(
    algo.VelocityController(algo.Proportional(1 / k, reference / 100))
)

print('> CLOSED LOOP ON VELOCITY')
#controller.set_reference1(0)
controller.start()
time.sleep(1)
controller.set_reference1(100)
print('\n> REFERENCE = {}'.format(reference))
time.sleep(3)
controller.set_reference1(50)
print('\n> REFERENCE = {}'.format(reference/2))
time.sleep(3)
controller.set_reference1(-50)
print('\n> REFERENCE = {}'.format(-reference/2))
time.sleep(3)
controller.stop()

controller.set_controller1(
    algo.VelocityController(algo.PID(1 / k, a / k, 0, reference / 100))
)

print('> CLOSED LOOP ON VELOCITY INTEGRAL')
controller.set_logger(20*controller.period)
controller.start()
time.sleep(1)
controller.set_reference1(100)
print('\n> REFERENCE = {}'.format(reference))
time.sleep(3)
controller.set_reference1(50)
print('\n> REFERENCE = {}'.format(reference/2))
time.sleep(3)
controller.set_reference1(-50)
print('\n> REFERENCE = {}'.format(-reference/2))
time.sleep(3)
controller.stop()

# print('page = {}\tcurrent = {}'.format(controller.page, controller.current))
# print('data = {}'.format(controller.data))
# print('log = {}'.format(controller.get_log()))
