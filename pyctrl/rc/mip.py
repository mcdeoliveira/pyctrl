import rcpy
import pyctrl
import pyctrl.rc

class Controller(pyctrl.rc.Controller):

    def __reset(self):

        # call super
        super().__reset()

        self.add_signals('theta','theta_dot',
                         'encoder1','encoder2',
                         'pwm1','pwm2')
        
        # add source: imu
        self.add_device('inclinometer',
                        'pyctrl.rc.mpu9250', 'Inclinometer',
                        type = 'source',
                        enable = False,
                        outputs = ['theta','theta_dot'])

        # add source: encoder1
        self.add_device('encoder1',
                        'pyctrl.rc.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder1'],
                        encoder = 3, 
                        ratio = 60 * 35.557)

        # add source: encoder2
        self.add_device('encoder2',
                        'pyctrl.rc.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder2'],
                        encoder = 2, 
                        ratio = - 60 * 35.557)

        # add sink: motor1
        self.add_device('motor1', 
                        'pyctrl.rc.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['pwm1'],
                        motor = 3)

        # add sink: motor2
        self.add_device('motor2', 
                        'pyctrl.rc.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['pwm2'],
                        motor = 2,
                        ratio = -100) 
