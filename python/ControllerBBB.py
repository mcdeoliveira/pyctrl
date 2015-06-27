import warnings
from Controller import Controller

class PID:
    
    def __init__(self, Kp = 1, Ki = 0, Kd = 0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.state = (0,0)

    def update(self, e):
        # PID controller
        #
        # u = Kp e + Ki z/(z-1) e + Kd (z-1)/z e
        #
        # x1(k+1) = x2(k)
        # x2(k+1) = x2(k) + e(k) 
        #
        # u_{k} = Kp e(k) + Ki (x2(k) + e(k)) + Kd (x1(k) - x2(k) + e(k))
        #
        u = self.Kp*e + \
            self.Ki*(self.state[1] + e) + \
            self.Kd*(self.state[0] - self.state[1] + e)
        self.state = self.state[1], self.state[1] + e
    
class ControllerBBB(Controller):

    def __init__(self):

        # parameters
        self.period = 100000000  # 100,000,000 ns = 0.1s
        self.target_mode = 0     # 1: read pot 
        self.controller_mode = 0 # 0: off,      1: open-loop, 
                                 # 2: velocity, 3: position, 4: custom

        # references
        self.target_1 = 0
        self.target_2 = 0

        # sensors
        self.potentiometer_1 = 0 #
        self.potentiometer_2 = 0 #
        self.encoder_1 = 0       #
        self.encoder_2 = 0       #

        # controls PWM
        self.motor_1_PWM = 0       #
        self.motor_1_direction = 0 #
        self.motor_2_PWM = 0       #
        self.motor_2_direction = 0 #

    def __enter__(self):
        print('> Starting Controller...')
        return self

    def __exit__(self, type, value, traceback):
        print('> Quiting Controller...')

    def set_period(self, value):
        self.period = value
        # Do it

    def set_encoder(self, value = 0):
        self.encoder1 = value

    def get_encoder(self):
        return self.encoder1

    def loop(self, value = True):

        # Read potentiometers

        # Update target
        if self.target_mode:
            self.target = analogRead(potentiometerPin) * 10;
        
        # Update encoders
        
        # Calculate velocity
        

  if ( runControl && controllerMode != OFF_CONTROL ) {
    

    /* compute velocity */
    long velocity = position - oldPosition;
    
    /* compute error */
    long dError, error = controllerTarget - targetZero;
    switch ( controllerMode ) {
      
      default:
      case POSITION_CONTROL:

        /* control position */
        /* dError = velocity */
        dError = velocity;
        /* erro = target - position */
        error -= position;
        break;
        
      case VELOCITY_CONTROL:
      
        /* control velocity */
        error /= VELOCITY_TARGET_SCALING;
        /* dError = acceleration */
        dError = position - 2 * oldPosition + oldOldPosition;
        /* error = target - velocity */
        error -= velocity;
        break;
        
      case OPEN_LOOP_CONTROL:
        
        /* set input */
        dError = 0;
        /* error will be between -512 and 512 */
        error /= 10;
        /* always zero controller state */
        controllerState = - error;
        break;
        
    }
    
    /* update state */
    controllerState += error;

    /* compute control */
    control = (controllerProportionalGain * error 
         + controllerIntegralGain * controllerState
         + controllerDerivativeGain * dError ) / motorGain * (256 * 16);
    controlDirection = (control > 0 ? 1 : -1);
    
    /* compute control intensity */
    if (controlDirection < 0)
      control = -control;

    /* normalize control */
    control = min(256 * 16, control);

    /* flip controlDirection */
    if (motorDirection < 0)
      controlDirection = -controlDirection;    
            
    if (runMotor) {      

      float tmp;
      switch ( motorCurve ) {

        case QUADRATIC_MOTOR:
          tmp = sqrt(float(control) / (256 * 16));
          control = 255 * (tmp * (2 - tmp));
          break;
        
        case CUBIC_MOTOR:
          tmp = pow(float(control) / (256 * 16), 1./3);
          control = 255 * (tmp * (1.5 - .5 * tmp * tmp));
          break;

        case LINEAR_MOTOR:
        default:
          control = control / 16;
          break;
        
      }
      
      control = min(255, control);
           
      /* set motor direction */
      if (controlDirection > 0)
        digitalWrite(motorDirectionPin, HIGH);
      else
        digitalWrite(motorDirectionPin, LOW);
      
      /* set motor intensity */
      analogWrite(motorPWMPin, control);
  
    }

  }
  
  if (echoPeriod && (loopCounter % echoPeriod == 0)) {
    
    Serial.print("T");
    Serial.println(millis());

    Serial.print("E");
    Serial.println(position, DEC);

/*
    Serial.print("V");
    Serial.println( position - oldPosition);

    Serial.print("V");
    Serial.println( period * encoderUno4589.getVelocityCountsA() / 1000000 );
*/

    if (runControl) {

      Serial.print("U");
      Serial.print(controlDirection < 0 ? "-" : "+");
      Serial.println(control, DEC);
    
    } else {
      
      Serial.println("U0");
      
    }
    
    Serial.print("R");
    Serial.println(controllerTarget, DEC);
      
  }
  
  /* updates */
  loopCounter++;
  oldOldPosition = oldPosition;
  oldPosition = position;

}


        sleep(self.period)

