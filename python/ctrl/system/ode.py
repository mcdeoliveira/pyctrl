import numpy
import scipy.integrate

from . import tv

def identity(t, x, u, *pars):
    return x

class ODEBase(TVSystem):
    """ODE(f, state)

    Model is of the form:

      .
      x = f(t, x, u, *pars)
      y = g(t, x, u, *pars)

    """
    
    def __init__(self,
                 f, g = identity, x0 = 0, t0 = 0, pars = ()):

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
        
    def set_output(self, yk):

        raise Exception('Not implemented yet')
    
    def update(self, tk, uk):
        
        raise Exception('Not implemented yet')


class ODE(ODEBase):
    """ODE(f, state)

    Model is of the form:

      .
      x = f(t, x, u, *pars)
      y = g(t, x, u, *pars)

    """
    
    def __init__(self,
                 f, g = identity, x0 = 0, t0 = 0, pars = ()):

        # call super
        super().__init__(f, g, x0, t0, pars)

        # setup solver
        self.solver = scipy.integrate.ode(self.f).set_integrator('dopri5')

    def update(self, tk, uk):
        
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
    """ODE(f, state)

    Model is of the form:

      .
      x = f(t, x, u, *pars)
      y = g(t, x, u, *pars)

    """
    
    def __init__(self,
                 f, g = identity, x0 = 0, t0 = 0, pars = ()):

        # call super
        super().__init__(f, g, x0, t0, pars)

        # flip call to fit odeint
        self.f = lambda t, x, *pars: f(x, t, *pars)

    def update(self, tk, uk):
        
        # solve ode
        yk = scipy.integrate.odeint(self.f, 
                                    self.state, 
                                    [self.t0, tk], 
                                    args = (uk,) + self.pars)
        
        # update state
        self.state = yk[-1,:]

        # udpate time
        self.t0 = tk

        # evaluate output
        return self.g(tk, self.state, uk, *self.pars)
