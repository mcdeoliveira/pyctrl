class ControlAlgorithm:
    def update(self, measurement, reference):
        raise NameError('update method undefined')

class OpenLoop(ControlAlgorithm):
    # Open-loop control is:
    # u = reference
    def update(self, measurement, reference, period):
        return reference

class ProportionalController(ControlAlgorithm):
    # Proportional control is:
    # u = Kp * (gamma * reference - measurement)
    def __init__(self, Kp, gamma = 1):
        self.Kp = Kp
        self.gamma = gamma
    
    def update(self, measurement, reference, period):
        return self.Kp * (self.gamma * reference - measurement)

class PIDController(ControlAlgorithm):
    # PID Controller is:
    # u = Kp * e + Ki int_0^t e dt + Kd de/dt
    # e = (gamma * reference - measurement)

    def __init__(self, Kp, Ki, Kd = 0, gamma = 1):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.gamma = gamma
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
        self.ierror = self.ierror + period * (error + self.error) / 2

        # Update error
        self.error = error
        
        return self.Kp * error + self.Ki * self.ierror + self.Kd * de
    
class VelocityController(ControlAlgorithm):

    # VelocityController is a wraper for controllers closed on velocity
    # instead of position

    def __init__(self, controller):
        self.measurement = 0
        self.controller = controller
        self.velocity = 0
    
    def update(self, measurement, reference, period):

        # Calculate velocity
        self.velocity = (measurement - self.measurement) / period
        
        # Update measurement
        self.measurement = measurement

        # Call controller
        return self.controller.update(self.velocity, reference, period)


