import pytest

import math
import time
import numpy as np
import numpy.linalg as la

from pyctrl.block.clock import Clock, TimerClock
from pyctrl.block import Map, Constant, Logger
from pyctrl.block.system import TimeVaryingSystem

test_ode = True
try:
    from pyctrl.system.ode import ODE, ODEINT
except:
    test_ode = False
    
def test1():

    if not test_ode:
        return
    
    from pyctrl import Controller
    controller = Controller()

    Ts = 0.01
    clock = TimerClock(period = Ts)
    controller.add_source('clock',clock,['clock'])

    a = -1
    b = 1
    def f(t, x, u, a, b):
        return a * x + b * u

    t0 = 0
    uk = 1
    x0 = np.array([0])
    sys = ODE((1,1,1), f, x0 = x0, t0 = t0, pars = (a,b))

    controller.add_signals('input','output')

    controller.add_filter('condition', 
                          Map(function = lambda x: x < 1), 
                          ['clock'], ['is_running'])

    controller.add_filter('ode',TimeVaryingSystem(model = sys),['clock','input'],['output'])

    controller.add_sink('logger',Logger(),['clock','output'])

    print(controller.info('all'))    

    controller.set_filter('ode', reset = True)
    controller.set_source('clock', reset = True)
    controller.set_sink('logger', reset = True)
    controller.set_signal('input',uk)
    controller.run()
    xk = sys.state

    log = controller.read_sink('logger')
    t0 = log[0,0]
    tk = log[-1,0]
    yk = log[-1,1]    
    yyk = uk * (1 - math.exp(a*(tk-t0))) + x0[0] * math.exp(a*(tk-t0))
    print(log)
    print(t0, x0, tk, xk, yk, yyk)
    assert np.abs(yk - yyk) < 1e-2

    uk = 0
    x0 = sys.state

    controller.add_filter('condition', 
                          Map(function = lambda x: x < 2), 
                          ['clock'], ['is_running'])

    
    #controller.set_source('clock', reset = True)
    controller.set_sink('logger', reset = True)
    controller.set_signal('input',uk)
    controller.run()
    xk = sys.state

    log = controller.read_sink('logger')
    t0 = log[0,0]
    tk = log[-1,0]
    yk = log[-1,1]    
    yyk = uk * (1 - math.exp(a*(tk-t0))) + x0 * math.exp(a*(tk-t0))
    print(log)
    print(t0, x0, tk, xk, yk, yyk)
    assert np.abs(yk - np.array([yyk])) < 1e-2

    uk = -1
    x0 = sys.state

    controller.add_filter('condition', 
                          Map(function = lambda x: x < 3), 
                          ['clock'], ['is_running'])

    #controller.set_source('clock', reset = True)
    controller.set_sink('logger', reset = True)
    controller.set_signal('input',uk)
    controller.run()
    xk = sys.state

    log = controller.read_sink('logger')
    t0 = log[0,0]
    tk = log[-1,0]
    yk = log[-1,1]    
    yyk = uk * (1 - math.exp(a*(tk-t0))) + x0 * math.exp(a*(tk-t0))
    print(t0, x0, tk, xk, yk, yyk)
    assert np.abs(yk - np.array([yyk])) < 1e-2

    clock.set_enabled(False)

def test2():

    if not test_ode:
        return
    
    m1 = 30/1000
    l1 = 7.6/100
    r1 = (5-(10-7.6)/2)/100

    w1 = 10/100
    d1 = 2.4/100
    J1 = m1 * (w1**2 + d1**2) / 12

    m2 = 44/1000

    w2 = 25.4/100
    d2 = 2.4/100
    J2 = m2 * (w2**2 + d2**2) / 12

    r2 = (25.4/2-1.25)/100

    Jm = 0.004106
    km = 0.006039
    bm = 0.091503

    g = 9.8

    bPhi = 0
    bTheta = 0

    def MK(x,u):
        theta, phi, thetaDot, phiDot = x
        return (np.array([[J2+m2*r2**2, m2*r2*l1*math.cos(theta-phi)],
                         [m2*r2*l1*math.cos(theta-phi), J1+Jm+m1*r1**2+m2*l1**2]]),
                np.array([bTheta*thetaDot+m2*r2*(g*math.sin(theta)+l1*math.sin(theta-phi)*phiDot**2),
                          g*(m1*r1+m2*l1)*math.sin(phi)-m2*r2*l1*math.sin(theta-phi)*thetaDot**2+(bm+bPhi)*phiDot-km*u[0]]))

    def ff(t, x, u):
        M, K = MK(x,u)    
        return np.hstack((x[2:4], -la.solve(M,K)))

    theta0, phi0 = 0+math.pi/6, 0
    t0, x0, u0 = 0, np.array([theta0,phi0,0,0]), [0]
    M,K = MK(x0,u0)
    print(M)
    print(K)
    print(ff(t0,x0,u0))

    sys = ODE(shape = (1,4,4), t0 = t0, x0 = x0, f = ff)

    tk = 5
    uk = [0]
    yk = sys.update(tk, uk)

    print('1. [{:3.2f}, {:3.2f}] = {}'.format(t0, tk, yk))

    from pyctrl import Controller
    controller = Controller()

    Ts = 0.01
    controller.add_source('clock',Clock(),['clock'])

    condition = Map(function = lambda t : t < T)
    controller.add_filter('condition',condition,['clock'],['is_running'])

    controller.add_signals('tau','x')
    controller.add_filter('ode', 
                          TimeVaryingSystem(model = ODE(shape = (1,4,4), t0 = t0, x0 = x0, f = ff)),
                          ['clock','tau'], ['x'])
    controller.add_sink('logger',Logger(),['clock','x'])
    

    controller.set_source('clock',reset=True)
    T = 5 + Ts
    controller.run()

    log = controller.read_sink('logger')
    t0 = log[0,0]
    tk = log[-1,0]
    yk = log[-1,1:]

    print('2. [{:3.2f}, {:3.2f}] = {}'.format(t0, tk, yk))

    import control
    
    fc = 7
    wc = 2 * math.pi * fc
    lpf = control.tf(wc,[1,wc])

    ctr = -2*100

    def gg(t, x, u):
        return [x[0]]

    Ts = 0.01
    Ac, Bc, Cc, Dc = map(np.array, control.ssdata(control.ss(lpf * ctr)))
    nc = Ac.shape[0]

    def F(t, x, ref):
        x, xc = x[0:4], x[4:4+nc]
        y = ref - gg(t,x,[0])
        u = max(-100,min(100,Cc.dot(xc)+Dc.dot(y)))
        #print(ff(t,x,u))
        return np.hstack((ff(t,x,u), Ac.dot(xc)+Bc.dot(y)))

    eta = 0
    kappa = 0

    ref = np.array([eta * math.pi])

    theta0 = -20*math.pi/180
    xx0 = [kappa*math.pi-theta0,eta*math.pi,0,0]
    xc0 = np.zeros((nc,))
    x0 = np.hstack((xx0,xc0))

    t0 = 0
    print('F = {}'.format(F(t0, x0, ref)))

    sys = ODE(shape = (1,4,4), t0 = t0, x0 = x0, f = F)

    tk = 1
    uk = np.array([0])
    yk = sys.update(tk, uk)

    print('1. [{:3.2f}, {:3.2f}] = {}'.format(t0, tk, yk))

    controller.reset()
    Ts = 0.01
    controller.add_source('clock',Clock(),['clock'])

    condition = Map(function = lambda t : t < T)
    controller.add_filter('condition',condition,['clock'],['is_running'])

    controller.add_signals('ref','x')
    controller.add_filter('ode', 
                          TimeVaryingSystem(model = ODE(shape = (1,4,4), t0 = t0, x0 = x0, f = F)),
                          ['clock','ref'], ['x'])
    controller.add_sink('logger',Logger(),['clock','x'])


    #print(controller.info('all'))

    controller.set_source('clock',reset=True)
    controller.set_signal('ref',ref)
    T = 1 + Ts
    controller.run()

    log = controller.read_sink('logger')
    t0 = log[0,0]
    tk = log[-1,0]
    yk = log[-1,1:]

    print('2. [{:3.2f}, {:3.2f}] = {}'.format(t0, tk, yk))
