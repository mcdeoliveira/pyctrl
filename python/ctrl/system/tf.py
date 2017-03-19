import numpy

from .. import system
from . import ss

class DTTF(system.System):
    r"""
    *DTTF* implements a single-input-single-output (SISO) transfer-function.

    The underlying model is of the form:

    .. math::

        den[0] y_k + den[1] y_{k-1} + \cdots + den[n] y_{k-n} = num[0] uk + num[1] u_{k-1} + \cdots + num[m] u_{k-m}

    which corresponds to the transfer-function:

    .. math::

      G(z) = \frac{\sum_{i = 0}^m z^{-i} num[i]}{\sum_{i = 0}^n z^{-i} den[i]}

    Denominator is always normalized so that :math:`den[0] = 1`.

    Model is implementated in terms of the auxiliary variable $z$ as follows. Let

    .. math::

        z_k + den[1] z_{k-1} + \cdots + den[n] z_{k-n} = u_k 

    By linearity:

    .. math::

        y_k = num[0] z_k + num[1] z_{k-1} + \cdots + den[n] z_{k-n}

    :param num: numpy m-dimensional 1D-vector numerator (default [1])
    :param den: numpy n-dimensional 1D-vector denominator (default [1])
    :param state: numpy n-dimensional 1D-vector representing vector z (default `None`)
    """
    
    def __init__(self,
                 num = numpy.array((1,)),
                 den = numpy.array((1,)),
                 state = None):

        # make sure it is numpy array
        num = numpy.array(num)
        den = numpy.array(den)

        # must be proper
        n = num.size - 1
        m = den.size - 1
        
        #print('n = {}\nm = {}'.format(n, m))
        
        # Make vectors same size
        self.den = den.astype(float)
        self.num = num.astype(float)
        if m < n:
            self.den.resize(num.shape)
            m = n
        elif m > n:
            self.num.resize(den.shape)
            n = m

        # inproper?
        if not self.den[0]:
            raise system.SystemException('Order of numerator cannot be greater than order of the denominator')

        # normalize denominator
        self.num = self.num / self.den[0]
        self.den = self.den / self.den[0]
        
        if state is None:
            self.state = numpy.zeros((n,), dtype=float)
        elif state.size == n:
            self.state = state.astype(float)
        else:
            raise system.SystemException('Order of state must match order of denominator')

        #print('num = {}'.format(self.num))
        #print('den = {}'.format(self.den))
        #print('state = {}'.format(self.state))

    def set_output(self, yk):
        r"""
        Sets the internal state of the *DTTF* so that a call to `update` with `uk = 0` yields `yk`.
        
        It is calculated as follows. With :math:`u_k = 0`

        .. math::

            z_k + den[1] z_{k-1} + \cdots + den[n] z_{k-n} &= 0

        and

        .. math::

            y_k &= num[0] z_k + num[1] z_{k-1} + \cdots + num[n] z_{k-n} \\
            &= num[1] z_{k-1} + \cdots + num[n] z_{k-n} - num[0] (den[1] z_{k-1} + \cdots + den[n] z_{k-n}) \\
        
        and :math:`y_k =` `yk` if :math:`num[1] \neq num[0] den[1]` and

        .. math::

            z_{k-1} = \frac{y_k - \sum_{i = 2}^{n} (num[i] - num[0] den[i]) z_{k-i}}{num[1] - num[0] den[1]}

        TODO: if :math:`num[1] \neq num[0] den[1]` then choose next nonzero coefficient.

        :param yk: scalar desired `yk`
        """
        self.state[1:] = 0
        if yk != 0:
            self.state[0] = (yk - self.state[1:].dot(self.num[2:]) + self.num[0] * self.state[1:].dot(self.den[2:]) ) / (self.num[1] - self.num[0] * self.den[1])
        elif self.state.size > 0:
            self.state[0] = 0
        #print('state = {}'.format(self.state))
    
    def shape(self):
        """
        Shape of a *DTTF*

        :return: tuple with number of inputs, number of outputs and order
        """
        return (1,1,len(self.state))
    
    def update(self, uk):
        r"""
        Update *DTTF* model. Implements the recursion:

        .. math::
        
            z_k + den[1] z_{k-1} + \cdots + den[n] z_{k-n} &= u_k \\
            y_k &= num[0] z_k + num[1] z_{k-1} + \cdots + den[n] z_{k-n}
        """
        #print('uk = {}, state = {}'.format(uk, self.state))
        zk = uk - self.state.dot(self.den[1:])
        yk = self.num[0] * zk + self.state.dot(self.num[1:])
        if self.state.size > 0:
            if self.state.size > 1:
                # shift state
                self.state[1:] = self.state[:-1]
            self.state[0] = zk
            
        return yk

    def as_DTSS(self):
        """
        :returns: a state-space representation (*DTSS*) of the *DTTF*.
        """
        
        n = self.num.size - 1
        m = 1
        p = 1

        A = numpy.zeros((n,n))
        B = numpy.zeros((n,m))
        C = numpy.zeros((p,n))
        D = numpy.zeros((p,m))

        A[:-1,1:] = numpy.eye(n-1)
        A[-1,:] = -numpy.flipud(self.den[1:])
        B[-1,0] = 1
        C[0,:] = numpy.flipud(self.num[1:]) - self.num[0] * numpy.flipud(self.den[1:])
        D[0,0] = self.num[0]

        return ss.DTSS(A, B, C, D)

def zDTTF(num, den, state = None):
    r"""
    *zDTTF* implements a single-input-single-output (SISO) transfer-function.

    The underlying model is of the form corresponds to the transfer-function:

    .. math::

      G(z) = \frac{\sum_{i = 0}^m z^{i} num[i]}{\sum_{i = 0}^n z^{i} den[i]}

    This is a convinience constructor that transforms a model in the form *zDTTF* into a `ctrl.system.DTTF`
    """

    if len(num) > len(den):
        raise system.SystemException('Order of numerator cannot be greater than order of the denominator')

    # make sure it is numpy array
    num = numpy.array(num)
    den = numpy.array(den)

    # must be proper
    n = num.size - 1
    m = den.size - 1

    # Make vectors same size
    den = den.astype(float)
    num = num.astype(float)
    if m < n:
        den.resize(num.shape)
        m = n
    elif m > n:
        num.resize(den.shape)
        n = m
        
    num = numpy.flipud(num)
    den = numpy.flipud(den)

    return DTTF(num, den, state) 


class PID(DTTF):
    r"""
    *PID* implements a PID controller.

    A continuous-time PID implements the following function:

    .. math::

        u(t) = K_p e(t) + K_i \int_0^t{e(t) \, dt} + K_d \frac{d}{dt} e(t)

    We provice the following discrete-time version:


    .. math::

                         
        x_k &= x_{k-1} +\frac{T}{2} (e_k + e_{k-1}) \\
        u_k &= K_p e_k + K_i x_k + \frac{K_d}{T} (e_k - e_{k-1})


    In terms of a transfer-function

    .. math::

       X(z) &= \frac{T}{2} \frac{1 + z^{-1}}{1 - z^{-1}} E(z)

    so that

    .. math::

       U(z) &= Kp E(z) + K_i X(z) + \frac{K_d}{T} (1 - z^{-1}) E(z) \\
       &= \left ( K_p + \frac{K_i T}{2} \frac{1 + z^{-1}}{1 - z^{-1}} + \frac{K_d}{T} (1 - z^{-1}) \right) E(z) \\
       &= \frac{K_p (1 - z^{-1}) + \frac{K_i T}{2} (1 + z^{-1}) + \frac{K_d}{T} (1 - z^{-1})^2}{1 - z^{-1}} E(z) \\
       &= G(z) E(z)

    where

    .. math::

       G(z) &= \frac{K_p + \frac{K_i T}{2} + \frac{Kd}{T} + z^{-1} \left ( \frac{K_i T}{2} - K_p - 2 \frac{K_d}{T} \right ) + z^{-2} \left ( \frac{K_d}{T} \right ) }{1 - z^{-1}}

    A PD controller is the special case when Ki = 0:

    .. math::

       U(z) &= \left ( K_p + \frac{Kd}{T} (1 - z^{-1}) \right ) E(z) \\
            &= \frac{K_p + + \frac{Kd}{T} - z^{-1} \frac{Kd}{T}}{1} E(z)

    This is a convinience constructor that returs a *PID* as a `ctrl.systems.DTTF`.

    :param Kp: proportional gain 
    :param Ki: integral gain (default = `0`)
    :param Kd: derivative gain (default = `0`)
    :param period: sampling period (default = `0`)
    :param state: internal state representation (default = `None`)
    """

    def __init__(self, Kp, Ki = 0, Kd = 0, period = 0, state = None):

        if Kd == 0:

            # P
            if Ki == 0:
                num = numpy.array([Kp])
                den = numpy.array([1])

            # PI
            else:

                assert period > 0
                num = numpy.array([Kp + Ki*period/2, 
                                   Ki*period/2 - Kp])
                den = numpy.array([1, -1])

        else:

            assert period > 0

            # PD
            if Ki == 0:
                num = numpy.array([Kp + Kd/period, 
                                   -Kd/period])
                den = numpy.array([1, 0])
                
            # PID
            else:
                num = numpy.array([Kp + Ki*period/2 + Kd/period, 
                                   Ki*period/2 - Kp - 2*Kd/period,
                                   Kd/period])
                den = numpy.array([1, -1, 0])
            
        super().__init__(num, den, state)

import math

class LPF(DTTF):
    """
    *LPF* implements a low pass-filter base on DTTF.
    
    TODO: filters of order higher than `1`
    
    :param fc: cuttof frequency in Hz
    :param order: order (default = `1`)
    """

    def __init__(self, fc, period = 0, order = 1):

        if order != 1:
            raise Exception('Not implemented yet')

        assert period > 0

        # LPF order 1
        # wc = 2 pi fc
        # T(s) = wc / (s + wc)
        # T(z) = wc Ts z / (z - e^{-wc Ts}) = wc Ts / (1 - q e^{-wc * Ts})
        
        wc = 2 * math.pi * fc
        num = numpy.array([wc * period ])
        den = numpy.array([1, -math.exp(-wc * period)])
            
        super().__init__(num, den)
