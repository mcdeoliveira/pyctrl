import numpy

class SISOLTISystem:
    
    # 
    # Model is of the form:
    #
    #  den' (yk, ... yk-n) = num' (uk, ... uk-m)
    #
    # or 
    #                         -k
    #         \sum_{k = 0}^n z   num[k]
    # G(z) = --------------------------
    #                         -k
    #         \sum_{k = 0}^m z   den[k]
    #
    # Denominator is normalized so that den[0] = 1.
    #
    # Implementation is as follows:
    #
    # Let
    #
    #   zk = uk - den[1:] (zk-1, ..., zk-n)
    # 
    # By linearity:
    #
    #   yk = num[0] zk + num[1:] (zk-1, ..., zk-n)
    #

    def __init__(self,
                 period,
                 num = numpy.array((1,)),
                 den = numpy.array((1,)),
                 state = None):
        
        self.set_model(period, num, den, state)
        
    def set_period(self, value = 0.1):
        self.period = value

    def set_model(self, period, num, den, state = None):
        
        # set period
        self.period = period
        
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

    def update(self, uk):
        
        #   zk = uk - den[1:] (zk-1, ..., zk-n)
        #   yk = num[0] zk + num[1:] (zk-1, ..., zk-n)
        zk = uk - self.state.dot(self.den[1:])
        yk = self.num[0] * zk + self.state.dot(self.num[1:])
        if self.state.size > 0:
            if self.state.size > 1:
                self.state[1:] = self.state[:-1]
            self.state[0] = zk
            
        return yk
