import numpy
import scipy.integrate
import scipy.optimize

from .. import system

def identity(t, x, u, *pars):
    return x

class ODEBase(system.TVSystem):
    r"""
    :py:class:`pyctrl.system.ODEBase` implements a general nonlinear time-varying continuous-time state-space model of the form:

    .. math::

       \dot{x} &= f(t, x, u, *pars) \\
             y &= g(t, x, u, *pars)

    This base class does not implement any methods.

    :param tuple shape: (m,p) where m is the number of inputs and p is the number of outputs
    :param f: nonlinear state function :math:`f`
    :param g: nonlinear state function :math:`g`
    :param numpy.array x0: initial value of the state vector
    :param float t0: initial time
    :param vargs pars: variable positional arguments to be passed to f and g
    """
    
    def __init__(self,
                 shape,
                 f,
                 g = identity,
                 x0 = numpy.array([0]),
                 t0 = -1,
                 pars = ()):

        # set shape
        self.shp = shape
        
        # set initial condition
        self.state = x0
        
        # set parameters
        self.pars = pars

        # set ode function
        self.f = f

        # set output function
        self.g = g

        # set t0
        self.t0 = t0

    def get_state(self):
        return self.state
        
    def set_state(self, xk):
        assert len(xk) == len(self.state)
        self.state = xk

    def shape(self):
        return self.shp
            
    def set_output(self, tk, yk):
        r"""
        Sets the internal state of the :py:class:`pyctrl.system.ODE` so that a call to `update` with `uk = 0` yields `yk`.
        
        Solves the equation:

        .. math::

            g(x_{k}) = y_{k}

        which leads to 

        .. math::

            y_k &= g(x_k) = y_k
        
        when :math:`u_k = 0`

        :param numpy.array yk: desired `yk`
        """
        
        u0 = numpy.zeros(self.shp[0])
        x0 = self.state
        self.state = scipy.optimize.newton(lambda x: self.g(tk, x, u0) - yk, x0)
    
    def update(self, tk, uk):
        
        raise Exception('Must be implemented by subclass')


class ODE(ODEBase):
    r"""
    :py:class:`pyctrl.system.ODE` implements a general nonlinear time-varying continuous-time state-space model of the form:

    .. math::

       \dot{x} &= f(t, x, u, *pars) \\
             y &= g(t, x, u, *pars)

    Integration is performed using :py:class:`scipy.integrate.ode`.

    :param tuple shape: (m,p) where m is the number of inputs and p is the number of outputs
    :param f: nonlinear state function :math:`f`
    :param g: nonlinear state function :math:`g`
    :param numpy.array x0: initial value of the state vector
    :param float t0: initial time
    :param vargs pars: variable positional arguments to be passed to f and g
    """
    
    def __init__(self,
                 shape,
                 f, g = identity, x0 = 0, t0 = -1, pars = ()):

        # call super
        super().__init__(shape, f, g, x0, t0, pars)

        # setup solver
        self.solver = scipy.integrate.ode(self.f).set_integrator('dopri5')

    def update(self, tk, uk):
        
        #print('t0 = {}, tk = {}, xk = {}, uk = {}'.format(self.t0, tk, self.state, uk))

        if tk == self.t0:
        
            # same time, evaluate output
            return self.g(tk, self.state, uk, *self.pars)

        else:

            # set initial condition and parameters
            pars = (uk,) + self.pars
            self.solver.set_initial_value(self.state, self.t0).set_f_params(*pars)

            # solve ode
            yk = self.solver.integrate(tk)

            # update state
            self.state = yk

            # update time
            self.t0 = tk

        # evaluate output
        return self.g(tk, self.state, uk, *self.pars)

class ODEINT(ODEBase):
    r"""
    :py:class:`pyctrl.system.ODEINT` implements a general nonlinear time-varying continuous-time state-space model of the form:

    .. math::

       \dot{x} &= f(t, x, u, *pars) \\
             y &= g(t, x, u, *pars)

    Integration is performed using :py:class:`scipy.integrate.odeint`.

    :param tuple shape: (m,p) where m is the number of inputs and p is the number of outputs
    :param f: nonlinear state function :math:`f`
    :param g: nonlinear state function :math:`g`
    :param numpy.array x0: initial value of the state vector
    :param float t0: initial time
    :param vargs pars: variable positional arguments to be passed to f and g
    """
    
    def __init__(self,
                 shape,
                 f, g = identity, x0 = 0, t0 = -1, pars = ()):

        # call super
        super().__init__(shape, f, g, x0, t0, pars)

        # flip call to fit odeint
        self.f = lambda t, x, *pars: f(x, t, *pars)

    def update(self, tk, uk):

        #print('t0 = {}, tk = {}, uk = {}'.format(self.t0, tk, uk))
        
        if tk == self.t0:
        
            # same time, evaluate output
            return self.g(tk, self.state, uk, *self.pars)

        else:

            # solve ode
            yk = scipy.integrate.odeint(self.f, 
                                        self.state, 
                                        [self.t0, tk], 
                                        args = (uk,) + self.pars)

            # update state
            # odeint returns all state, latest is last
            self.state = yk[-1,:]

            # udpate time
            self.t0 = tk

        # evaluate output
        return self.g(tk, self.state, uk, *self.pars)
