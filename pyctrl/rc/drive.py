import rcpy
import pyctrl
import pyctrl.rc
from pyctrl import BlockType

class Controller(pyctrl.rc.Controller):

    def _reset(self):

        # call super
        super()._reset()

        self.add_signals('pitch','roll','yaw',
                         'encoder1','encoder2',
                         'pwm1','pwm2')
        
        # add source: imu
        self.add_source('orientation',
                        ('pyctrl.rc.mpu9250', 'TaitBryanAngles'),
                        ['pitch','roll','yaw'],
                        kwargs = {'demux': True})

        # add source: encoder1
        self.add_source('encoder1',
                        ('pyctrl.rc.encoder', 'Encoder'),
                        ['encoder1'],
                        kwargs = {'encoder': 3, 
                                  'ratio': 60 * 35.557})

        # add source: encoder2
        self.add_source('encoder2',
                        ('pyctrl.rc.encoder', 'Encoder'),
                        ['encoder2'],
                        kwargs = {'encoder': 2, 
                                  'ratio': - 60 * 35.557})

        # add sink: motor1
        self.add_sink('motor1', 
                      ('pyctrl.rc.motor', 'Motor'),
                      ['pwm1'],
                      kwargs = {'motor': 3},
                      enable = True)

        # add sink: motor2
        self.add_sink('motor2', 
                      ('pyctrl.rc.motor', 'Motor'),
                      ['pwm2'],
                      kwargs = {'motor': 2,
                                'ratio': -100},
                      enable = True) 
