import ctrl.bbb as ctrl

class Controller(ctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # Initialize controller
        super().__init__(*vargs, **kwargs)

    def __reset(self):

        # call super
        super().__reset()

        # add source: encoder1
        self.add_device('encoder1',
                        'ctrl.bbb.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder1'],
                        encoder = 2, 
                        ratio = 60 * 35.557)

        self.add_device('encoder2',
                        'ctrl.bbb.encoder', 'Encoder',
                        type = 'source',
                        outputs = ['encoder2'],
                        encoder = 1, 
                        ratio = 60 * 35.557)

        # add sink: motor1
        self.add_device('motor1', 
                        'ctrl.bbb.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor1'],
                        pwm_pin = 'P9_14',
                        dir_A = 'P9_12',
                        dir_B = 'P9_13',
                        enable_pin = 'P9_42') 

        # add sink: motor2
        self.add_device('motor2', 
                        'ctrl.bbb.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor2'],
                        pwm_pin = 'P9_16',
                        dir_A = 'P9_15',
                        dir_B = 'P8_38',
                        enable_pin = 'P9_42')
