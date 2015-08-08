import numpy

from . import block

class SISOLTISystem:
    """ 
    SISOLTISystem(num, den, state)

    Model is of the form:

      den' (yk, ... yk-n) = num' (uk, ... uk-m)

    or 
                              -k
              \sum_{k = 0}^n z   num[k]
      G(z) = ---------------------------
                              -k
              \sum_{k = 0}^m z   den[k]

    Denominator is normalized so that den[0] = 1.

    Implementation is as follows:

    Let

      zk = uk - den[1:] (zk-1, ..., zk-n)

    By linearity:

      yk = num[0] zk + num[1:] (zk-1, ..., zk-n)
    """
    
    def __init__(self,
                 num = numpy.array((1,)),
                 den = numpy.array((1,)),
                 state = None):
        self.set_model(num, den, state)
        
    def set_model(self, num, den, state = None):
        
        # must be proper
        n = num.size - 1
        m = den.size - 1
        
        #print('n = {}\nm = {}'.format(n, m))
        
        # Make vectors same size
        self.den = den.astype(float)
        self.num = num.astype(float)
        if m < n:
            self.den.resize(num.shape)
        elif m > n:
            self.num.resize(den.shape)
        
        # normalize denominator
        self.num = self.num / self.den[0]
        self.den = self.den / self.den[0]
        
        if state is None:
            self.state = numpy.zeros((n,), dtype=float)
        elif state.size != n:
            raise NameError('Order of state must match order of denominator')
        else:
            self.state = state.astype(float)

        #print('num = {}'.format(self.num))
        #print('den = {}'.format(self.den))
        #print('state = {}'.format(self.state))

    def set_output(self, yk):
        # From the realization:
        #   zk = uk - den[1:] (zk-1, ..., zk-n)
        #   yk = num[0] zk + num[1:] (zk-1, ..., zk-n)
        # with uk = 0
        #  => zk-1 = (yk - num[2:] + num[0] den[2:]) (zk-2, ..., zk-n) / (num[1] - num[0] den[1])
        self.state[1:] = 0
        if yk != 0:
            self.state[0] = (yk - self.state[1:].dot(self.num[2:]) + self.num[0] * self.state[1:].dot(self.den[2:]) ) / (self.num[1] - self.num[0] * self.den[1])
        elif self.state.size > 0:
            self.state[0] = 0
        #print('state = {}'.format(self.state))
    
    def update(self, uk):
        # zk = uk - den[1:] (zk-1, ..., zk-n)
        # yk = num[0] zk + num[1:] (zk-1, ..., zk-n)
        #print('uk = {}, state = {}'.format(uk, self.state))
        zk = uk - self.state.dot(self.den[1:])
        yk = self.num[0] * zk + self.state.dot(self.num[1:])
        if self.state.size > 0:
            if self.state.size > 1:
                # shift state
                self.state[1:] = self.state[:-1]
            self.state[0] = zk
            
        return yk

class PID(SISOLTISystem):
    """PID(Kp, Ki = 0, Kd = 0, period = 0, state = None) implements a PID
    controller base on SISOLTISystem.

    Continuous:

      u(t) = Kp e(t) + Ki int_0^t e(t) dt + Kd d/dt e(t)

    Discrete:

                       T  
      x[k] = x[k-1] + --- (e[k] + e[k-1])
                       2
                                  Kd
      u[k] = Kp e[k] + Ki x[k] + --- (e[k] - e[k-1])
                                  T

    Transfer-function (q = z^{-1}):

           T  (1 + q)
      X = --- ------- E
           2  (1 - q)
                         Kd
      U = Kp E + Ki X + --- (1 - q) E
                         T
                  Ki T  (1 + q)    Kd
        = { Kp + ------ ------- + --- (1 - q) } E
                   2    (1 - q)    T

           Kp (1 - q) + Ki (T/2) (1 + q) + (Kd/T) (1 - q)^2
        = -------------------------------------------------- E
                             (1 - q)

           num(q)
        = ------- E
           den(q)

           num = Kp + Ki (T/2) + (Kd/T), 
                 Ki (T/2) - Kp - 2 (Kd/T),
                 (Kd/T)
           den = 1, -1, 0

    PD is special case Ki = 0:

                  Kd
      U = Kp E + --- (1 - q) E
                  T
           num(q)
        = ------- E
           den(q)

           num = Kp + (Kd/T), -(Kd/T)
           den = 1,  0

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

class SISOLTIBlock(block.Block):

    def __init__(self, *vars, **kwargs):
        """
        Wrapper for SISOLTISystem as a Block
        """

        self.model = kwargs.pop('model', SISOLTISystem())
        self.output = ()

        super().__init__(*vars, **kwargs)
        
    def read(self):
        return self.output

    def write(self, values):
        self.output = (self.model.update(values[0]), )
