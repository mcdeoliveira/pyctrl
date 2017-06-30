import rcpy
import pyctrl
import pyctrl.rc
from pyctrl import BlockType

class Controller(pyctrl.rc.Controller):

    def _reset(self):

        # call super
        super()._reset()

        self.add_signals('theta','theta_dot',
                         'encoder1','encoder2',
                         'pwm1','pwm2')
        
        # add source: imu
        self.add_device('inclinometer',
                        'pyctrl.rc.mpu9250', 'Inclinometer',
                        enable = False,
                        outputs = ['theta','theta_dot'])

        # add source: encoder1
        self.add_device('encoder1',
                        'pyctrl.rc.encoder', 'Encoder',
                        outputs = ['encoder1'],
                        kwargs = {'encoder': 3, 
                                  'ratio': 60 * 35.557})

        # add source: encoder2
        self.add_device('encoder2',
                        'pyctrl.rc.encoder', 'Encoder',
                        outputs = ['encoder2'],
                        kwargs = {'encoder': 2, 
                                  'ratio': - 60 * 35.557})

        # add sink: motor1
        self.add_device('motor1', 
                        'pyctrl.rc.motor', 'Motor',
                        inputs = ['pwm1'],
                        kwargs = {'motor': 3},
                        enable = True)

        # add sink: motor2
        self.add_device('motor2', 
                        'pyctrl.rc.motor', 'Motor',
                        inputs = ['pwm2'],
                        kwargs = {'motor': 2,
                                  'ratio': -100},
                        enable = True) 
