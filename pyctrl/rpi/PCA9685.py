import Adafruit_PCA9685

class PCA9685:
    ''' 
    PWM motor controler using PCA9685 boards. 
    This is used for most RC Cars
    '''
    def __init__(self, frequency=60):
        # Initialise the PCA9685 using the default address (0x40).
        self.frequency = frequency
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(frequency)
        
    def set_pulse(self, channel, pulse):
        pulse_length = 1000000    # 1,000,000 us per second
        pulse_length //= self.frequency # 60 Hz
        # print('{0}us per period'.format(pulse_length))
        pulse_length //= 4096     # 12 bits of resolution
        # print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        pulse //= pulse_length
        self.pwm.set_pwm(channel, 0, pulse)
