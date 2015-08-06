import numpy
import ctrl.lti as lti

class Algorithm:
    def update(self, measurement, reference, period):
        raise NameError('update method undefined')

class OpenLoop(Algorithm):
    # Open-loop control is:
    # u = reference
    def update(self, measurement, reference, period):
        return reference

class Proportional(Algorithm):
    # Proportional control is:
    # u = Kp * (gamma/100 * reference - measurement)
    def __init__(self, Kp, gamma = 100):
        self.Kp = Kp
        self.gamma = gamma/100
    
    def update(self, measurement, reference, period):
        return self.Kp * (self.gamma * reference - measurement)

class PID(Algorithm):
    # PID Controller is:
    # u = Kp * e + Ki int_0^t e dt + Kd de/dt
    # e = (gamma/100 * reference - measurement)

    def __init__(self, Kp, Ki, Kd = 0, gamma = 100):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.gamma = gamma/100
        self.error = 0
        self.ierror = 0
    
    def update(self, measurement, reference, period):

        # calculate error
        error = (self.gamma * reference - measurement)

        # Calculate derivative of the error
        de = (error - self.error) / period

        # Calculate integral of the error
        #                   Ts  
        # ei[k] = ei[k-1] + --- ( w[k] + w[k-1] )
        #                    2
        self.ierror += period * (error + self.error) / 2

        # Update error
        self.error = error
        
        return (self.Kp * error + self.Ki * self.ierror + self.Kd * de)

class LTI(Algorithm):

    def __init__(self, 
                 num = numpy.array((1,)),
                 den = numpy.array((1,)),
                 state = None,
                 gamma = 100):

        self.gamma = gamma/100
        self.model = lti.SISOLTISystem(num, den, state)
        
    def update(self, measurement, reference, period):

        # calculate error
        error = (self.gamma * reference - measurement)

        return self.model.update(error)
    
class VelocityController(Algorithm):

    # VelocityController is a wraper for controllers closed on velocity
    # instead of position

    def __init__(self, controller):
        self.measurement = 0
        self.controller = controller
        # velocit is for convinience only
        self.velocity = 0
    
    def update(self, measurement, reference, period):

        # Calculate velocity
        self.velocity = (measurement - self.measurement) / period
        
        # Update measurement
        self.measurement = measurement

        # Call controller
        return self.controller.update(self.velocity, reference, period)
