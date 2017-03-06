import warnings
import time

import rc
import ctrl
import rc.ctrl as rc_ctrl

class Controller(rc_ctrl.Controller):

    def __reset(self):

        # call super
        super().__reset()

        # add source: encoder1
        self.add_device('encoder1',
                        'rc.ctrl.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder1'],
                        encoder = 3, 
                        ratio = 60 * 35.557)

        # add source: encoder2
        self.add_device('encoder2',
                        'rc.ctrl.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder2'],
                        encoder = 2, 
                        ratio = - 60 * 35.557)

        # add source: imu
        self.add_device('imu',
                        'rc.ctrl.imu', 'Inclinometer',
                        type = 'source',
                        enable = False,
                        outputs = ['theta','theta_dot'])

        # add sink: motor1
        self.add_device('motor1', 
                        'rc.ctrl.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor1'],
                        motor = 3)

        # add sink: motor2
        self.add_device('motor2', 
                        'rc.ctrl.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor2'],
                        motor = 2,
                        gain = -1/100) 

        # set state as RUNNING
        rc.set_state(rc.RUNNING)

        # register cleanup function
        rc.add_cleanup(self.set_state, (ctrl.EXITING,))
        
        # # Initializing devices
        # warnings.warn("> Initializing devices ...")
        # self.start()
        # time.sleep(2)
        # self.stop()
        # warnings.warn("> Done.")
