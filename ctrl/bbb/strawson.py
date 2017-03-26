class SimplePWMException(Exception):
    pass

SYSFS_PWM_DIR = "/sys/class/pwm"

def init_pwm(subsystem, period_ns):

    with open(SYSFS_PWM_DIR +
              "/pwm{}/run".format(subsystem), 'w') as runA, \
        open(SYSFS_PWM_DIR +
             "/pwm{}/period_ns".format(subsystem), 'w') as periodA, \
        open(SYSFS_PWM_DIR +
             "/pwm{}/duty_ns".format(subsystem), 'w') as dutyA, \
        open(SYSFS_PWM_DIR +
             "/pwm{}/polarity".format(subsystem), 'w') as polarityA:

        # disable A channel and set polarity before setting frequency
        #write(runA_fd, "0", 1);
	# write(duty_fd[(subsystem)], "0", 1); // set duty cycle to 0
	# write(polarityA_fd, "0", 1); // set the polarity
        
        runA.write("0")
        dutyA.write("0")
        polarityA.write("0")

	# set the period in nanoseconds
        periodA.write("{}".format(period_ns))

def uninit_pwm(subsystem):

    with open(SYSFS_PWM_DIR + "/unexport", 'w') as fd:
        fd.write("{}".format((2*subsystem)))
        fd.write("{}".format((2*subsystem)+1))

class SimplePWM:

    def __init__(self, subsystem, frequency):

        assert (subsystem >= 0 and subsystem <= 2)
                 
        self.period = 1000000000/frequency # in ns

        # unexport the channels first
        uninit_pwm(subsystem)
	
        with open(SYSFS_PWM_DIR + "/export", 'w') as export:

            # export just the A channel for that subsystem
            export.write("{}".format(2*subsystem))

            # len = snprintf(buf, sizeof(buf), "%d", period_ns[subsystem]);
            # write(periodA_fd, buf, len);

            init_pwm(2*subsystem, self.period)

            # now we can set up the 'B' channel since the period has been set
            # the driver will not let you change the period when both are exported
	
            # export the B channel
            export.write("{}".format((2*subsystem) + 1))

            # set duty
            init_pwm((2*subsystem) + 1, self.period)

        # enable channels A & B
        with open(SYSFS_PWM_DIR +
                  "/pwm{}/run".format(2*subsystem), 'w') as runA, \
            open(SYSFS_PWM_DIR +
                 "/pwm{}/run".format((2*subsystem)+1), 'w') as runB:
            runA.write("1");
            runB.write("1");

        # open duty_fds
        self.duty_fd = (open(SYSFS_PWM_DIR +
                             "/pwm{}/duty_ns".format(2*subsystem), 'w'),
                        open(SYSFS_PWM_DIR +
                             "/pwm{}/duty_ns".format((2*subsystem)+1), 'w'))

    def set_pwm_duty(channel, duty):

        # start with sanity checks
        assert (duty >= 0 and duty <= 100)
	
        # set the duty
        duty_ns = duty * self.period / 100

        if ch == 'A':
            self.duty_fd[0].write("{}".format(duty_ns))
        elif ch == 'B':
            self.duty_fd[1].write("{}".format(duty_ns))
        else:
            raise SimplePWMException("channel must be 'A' or 'B'")

if __name__ == "__main__":

    import Adafruit_BBIO.GPIO as GPIO
    import Adafruit_BBIO.PWM as PWM
    import time, math

    print("> Testing Motor1")
    
    pwm_pin = 'P9_14'
    dir_A = 'P9_15'
    dir_B = 'P9_23'
    PWM.start(pwm_pin)
    GPIO.setup(dir_A, GPIO.OUT)
    GPIO.setup(dir_B, GPIO.OUT)

    freq = 25000
    motor1 = SimplePWM(1, freq)

    # # run motor forward
    # motor1.write(100)
    # time.sleep(1)

    # # stop motor
    # motor1.write(0)
    # time.sleep(1)

    # # run back
    # motor1.write(-100)
    # time.sleep(1)

    # # stop motor
    # motor1.write(0)

    # print("> Testing Motor2")

    # motor2 = Motor(dir_A='P9_12',
    #                dir_B='P9_27',
    #                pwm_pin='P9_16')

    # # run motor forward
    # motor2.write(100)
    # time.sleep(1)

    # # stop motor
    # motor2.write(0)
    # time.sleep(1)

    # # run back
    # motor2.write(-100)
    # time.sleep(1)

    # # stop motor
    # motor2.write(0)
