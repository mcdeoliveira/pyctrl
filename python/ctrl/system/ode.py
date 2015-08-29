import numpy
import scipy.integrate

from .. import system

def identity(x, u, *pars):
    return x

class ODE:
    """ODE(f, state)

    Model is of the form:

      .
      x = f(x, u, *pars)
      y = g(x, u, *pars)

    """
    
    def __init__(self,
                 f, g = identity, x0 = 0, period = 0, pars = ()):

        # set period
        assert period > 0
        self.period = period
        
        # set initial condition
        self.state = x0
        
        # ode function
        self.f = lambda y, t, *pars: f(y, *pars)

        # set parameters
        self.pars = pars

        # set output
        self.g = g
        
    def set_output(self, yk):
        raise Exception('Not implemented yet')
    
    def update(self, uk):
        
        # solve ode
        yk = scipy.integrate.odeint(self.f, self.state, [0, self.period], 
                                    args = (uk,) + self.pars)
        
        # update state
        self.state = yk[-1,:]
        
        # evaluate output
        return self.g(self.state, uk, *self.pars)


class ODE2(ODE):
    """ODE(f, state)

    Model is of the form:

      .
      x = f(x, u, *pars)
      y = g(x, u, *pars)

    """
    
    def __init__(self,
                 f, g = identity, x0 = 0, period = 0, pars = ()):

        # call super
        super().__init__(f, g, x0, period, pars)

        # setup solver
        self.solver = scipy.integrate.ode(f).set_integrator('dopri5')

        # set t
        self.t = 0
                
    def update(self, uk):
        
        # set initial condition and parameters
        pars = (uk,) + self.pars
        self.solver.set_initial_value(self.state, self.t).set_f_params(*pars)
        
        # solve ode
        yk = self.solver.integrate(self.t + self.period)
        
        # update state
        self.state = yk

        # update time
        self.t += self.period

        # evaluate output
        return self.g(self.state, uk, *self.pars)
