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
                        ratio = 48 * 172)

        # add source: analog1
        self.add_device('analog1', 
                        'ctrl.bbb.analog', 'Analog',
                        type = 'source',
                        outputs = ['analog1'],
                        pin = 'AIN0',
                        full_scale = 0.85,
                        invert = True) 
        
        # add sink: motor1
        self.add_device('motor1', 
                        'ctrl.bbb.motor', 'Motor',
                        type = 'sink',
                        enable = True,
                        inputs = ['motor1'],
                        pwm_pin = 'P9_14',
                        dir_A = 'P9_15',
                        dir_B = 'P9_23') 
