import pyctrl.bbb as pyctrl

class Controller(pyctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # Initialize controller
        super().__init__(*vargs, **kwargs)

    def __reset(self):

        # call super
        super().__reset()

        # add source: encoder1
        self.add_device('encoder1',
                        'pyctrl.bbb.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder1'],
                        encoder = 1, 
                        ratio = - 60 * 35.557)

        # add source: encoder2
        self.add_device('encoder2',
                        'pyctrl.bbb.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder2'],
                        encoder = 2, 
                        ratio = 60 * 35.557)

        # add source: imu
        # self.add_device('mpu6050',
        #                 'pyctrl.bbb.mpu6050', 'Inclinometer',
        #                 type = 'source',
        #                 enable = True,
        #                 outputs = ['imu'])

        # add source: mic1
        self.add_device('mic1',
                        'pyctrl.bbb.analog', 'Analog',
                        type = 'source',
                        pin = 'AIN0',
                        outputs = ['mic1'])

        # add source: mic2
        self.add_device('mic2',
                        'pyctrl.bbb.analog', 'Analog',
                        type = 'source',
                        pin = 'AIN1',
                        outputs = ['mic2'])

        # add source: prox1
        self.add_device('prox1',
                        'pyctrl.bbb.analog', 'Analog',
                        type = 'source',
                        pin = 'AIN2',
                        outputs = ['prox1'])

        # add source: prox2
        self.add_device('prox2',
                        'pyctrl.bbb.analog', 'Analog',
                        type = 'source',
                        pin = 'AIN3',
                        outputs = ['prox2'])

        # add sink: motor1
        self.add_device('motor1', 
                        'pyctrl.bbb.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor1'],
                        pwm_pin = 'P9_14',
                        dir_A = 'P9_15',
                        dir_B = 'P9_23') 

        # add sink: motor2
        self.add_device('motor2', 
                        'pyctrl.bbb.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor2'],
                        pwm_pin='P9_16',
                        dir_B='P9_12',
                        dir_A='P9_27') 


if __name__ == "__main__":

    import time, math
    import pyctrl.block as block
    from pyctrl.block.linear import Feedback, Gain

    # initialize robut
    robut = Controller()

    print("> WELCOME TO ROBUT")
    
    print(robut.info('all'))

    # install printer
    robut.add_sink('printer', 
                   block.Printer(endln = '\r'), 
                   ['clock',
                    'motor1', 'encoder1',
                    'motor2', 'encoder2',
                    #'imu',
                    'mic1','mic2',
                    'prox1','prox2'])

    # install controller
    robut.add_signal('reference1')
    robut.add_filter('controller', 
                     Feedback(block = Gain(gain = 1)),
                     ['prox2', 'reference1'], 
                     ['motor1'])    

    with robut:
        for k in range(100):
            mic1 = robut.get_signal('mic1')
            print('> mic1 = {}'.format(mic1))
            time.sleep(1)

    print("> BYE")
