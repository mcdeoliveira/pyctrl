import warnings
from threading import Thread
import numpy

class ControllerException(Exception):
    pass

class Controller:

    def __init__(self, period = .01):

        # debug
        self.debug = 0

        # real-time loop
        self.period = period
        self.is_running = False

        # signals
        self.signals = { 'clock': 0 }

        # sources
        self.sources = { }
        self.sources_order = [ ]

        # sinks
        self.sinks = { }
        self.sinks_order = [ ]

        # filters
        self.filters = { }
        self.filters_order = [ ]

    # __str__ and __repr__
    def __str__(self):
        return self.info()

    __repr__ = __str__

    # info
    def info(self, options = 'summary'):

        options = options.lower()
        result = ''

        if options == 'sources':

            result += '> sources\n'
            for (k, label) in enumerate(self.sources_order):
                device = self.sources[label]
                source = device['block']
                result += '  {}. '.format(k+1) + \
                          label + '[' 
                if source.is_enabled():
                    result += 'enabled'
                else:
                    result += 'disabled'
                result += '] >> ' + ', '.join(device['outputs']) + '\n'
                k += 1
            
        elif options == 'filters':

            result += '> filters\n'
            for (k,label) in enumerate(self.filters_order):
                device = self.filters[label]
                filter_ = device['block']
                result += '  {}. '.format(k+1) + \
                          ', '.join(device['inputs']) + \
                          ' >> ' + label + '[' 
                if filter_.is_enabled():
                    result += 'enabled'
                else:
                    result += 'disabled'
                result += '] >> ' + ', '.join(device['outputs']) + '\n'

        elif options == 'sinks':

            result += '> sinks\n'
            for (k, label) in enumerate(self.sinks_order):
                device = self.sinks[label]
                sink = device['block']
                result += '  {}. '.format(k+1) + \
                          ', '.join(device['inputs']) + \
                          ' >> ' + label + '[' 
                if sink.is_enabled():
                    result += 'enabled'
                else:
                    result += 'disabled'
                result += ']' + '\n'

        elif options == 'signals':

            result += '> signals\n  ' + \
                      '\n  '.join('{}. {}'.format(k+1,key) 
                                  for k,key in 
                                  sorted(enumerate(self.signals.keys()))) + '\n'

        elif options == 'period':

            result += '> period = {}s\n'.format(self.period)

        elif options == 'all':
            
            result = ''.join(map(lambda x: self.info(x), 
                                 ['summary', 'period', 'signals', 'sources', 
                                  'filters', 'sinks']))
            
        else: # options == 'summary':
        
            result += '> Controller with {} signal(s), {} source(s), {} sink(s), and {} filter(s)' \
                .format(len(self.signals),
                        len(self.sources), 
                        len(self.sinks), 
                        len(self.filters)) + '\n'

        return result

    # signals
    def add_signal(self, label):
        assert isinstance(label, str)
        if label in self.signals:
            raise ControllerException("Signal '{}' already present".format(label))
        else:
            self.signals[label] = 0

    def add_signals(self, *labels):
        for label in labels:
            self.add_signal(label)

    def remove_signal(self, label):
        self.signals.pop(label)

    def set_signal(self, label, value):
        if label not in self.signals:
            raise ControllerException("Signal '{}' does not exist".format(label))
        self.signals[label] = value

    def get_signal(self, label):
        return self.signals[label]

    # sources
    def add_source(self, label, source, signals):
        assert isinstance(label, str)
        if label in self.sources:
            raise ControllerException("Source '{}' already present".format(label))
        assert isinstance(source, block.Block)
        assert isinstance(signals, (list, tuple))
        self.sources[label] = {
            'block': source,
            'outputs': signals
        }
        self.sources_order.append(label)

    def remove_source(self, label):
        self.sources_order.remove(label)
        self.sources.pop(label)

    def set_source(self, label, key, values = None):
        if label not in self.sources:
            raise ControllerException("Source '{}' does not exist".format(label))
        key = key.lower()
        if key == 'outputs':
            assert isinstance(values, (list, tuple))
            self.sources[label][key] = values
        elif key == 'reset':
            self.sources[label]['block'].reset()
        else:
            raise ControllerException("Unknown key '{}'".format(key))

    def get_source(self, label):
        return self.source[label]['block']

    # sinks
    def add_sink(self, label, sink, signals):
        assert isinstance(label, str)
        if label in self.sinks:
            raise ControllerException("Sink '{}' already present".format(label))
        assert isinstance(sink, block.Block)
        assert signals == '*' or isinstance(signals, (list, tuple))
        self.sinks[label] = {
            'block': sink,
            'inputs': signals
        }
        self.sinks_order.append(label)

    def remove_sink(self, label):
        self.sinks_order.remove(label)
        self.sinks.pop(label)

    def set_sink(self, label, key, values = None):
        if label not in self.sinks:
            raise ControllerException("Sink '{}' does not exist".format(label))
        key = key.lower()
        if key == 'inputs':
            assert isinstance(values, (list, tuple))
            self.sinks[label][key] = values
        elif key == 'reset':
            self.sinks[label]['block'].reset()
        else:
            raise ControllerException("Unknown key '{}'".format(key))

    def get_sink(self, label):
        return self.sinks[label]['block']

    def read_sink(self, label):
        return self.sinks[label]['block'].read()

    # filters
    def add_filter(self, label, 
                       filter_, input_signals, output_signals):
        assert isinstance(label, str)
        if label in self.filters:
            raise ControllerException("Filter '{}' already present".format(label))
        assert isinstance(filter_, block.Block)
        assert isinstance(input_signals, (list, tuple))
        assert isinstance(output_signals, (list, tuple))
        self.filters[label] = { 
            'block': filter_,  
            'inputs': input_signals,
            'outputs': output_signals
        }
        self.filters_order.append(label)

    def remove_filter(self, label):
        self.filters_order.remove(label)
        self.filters.pop(label)

    def set_filter(self, label, key, values = None):
        if label not in self.filters:
            raise ControllerException("Filter '{}' does not exist".format(label))
        key = key.lower()
        if key == 'inputs' or key == 'outputs':
            assert isinstance(values, (list, tuple))
            self.filters[label][key] = values
        elif key == 'reset':
            self.filters[label]['block'].reset()
        else:
            raise ControllerException("Unknown key '{}'".format(key))
            
    def get_filter(self, label):
        return self.filters[label]['block']

    # clock

    def get_clock(self):

        device = self.sources['clock']
        source = device['block']
        if source.is_enabled():
            self.signals.update(dict(zip(device['outputs'], 
                                         source.read())))

        return self.signals['clock']

    def __enter__(self):
        if self.debug > 0:
            print('> Starting controller')
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if self.debug > 0:
            print('> Stoping controller')
        self.stop()

    # def set_motor1_pwm(self, value = 0):
    #     if value > 0:
    #         self.motor1_pwm = value
    #         self.motor1_dir = 1
    #     else:
    #         self.motor1_pwm = -value
    #         self.motor1_dir = -1

    # def set_motor2_pwm(self, value = 0):
    #     if value > 0:
    #         self.motor2_pwm = value
    #         self.motor2_dir = 1
    #     else:
    #         self.motor2_pwm = -value
    #         self.motor2_dir = -1

    def set_delta_mode(self, value = 0):
        self.delta_mode = value

    # def calibrate(self, eps = 0.05, T = 5, K = 20):
        
    #     # save controllers
    #     controller1 = self.controller1
    #     controller2 = self.controller2
    #     echo = self.echo
        
    #     # remove controllers
    #     self.controller1 = None
    #     self.controller2 = None
    #     self.echo = 0

    #     print('> Calibrating period...')
    #     print('  ITER   TARGET   ACTUAL ACCURACY')

    #     k = 1
    #     est_period = (1 + 2 * eps) * self.period
    #     error = abs(est_period - self.period) / self.period
    #     while error > eps:

    #         # run loop for T seconds
    #         k0 = self.current
    #         t0 = perf_counter()
    #         self.start()
    #         time.sleep(T)
    #         self.stop()
    #         t1 = perf_counter()
    #         k1 = self.current
            
    #         # estimate actual period
    #         est_period = (t1 - t0) / (k1 - k0)
    #         error = abs(est_period - self.period) / self.period
    #         print('  {:4}  {:6.5f}  {:6.5f}   {:5.2f}%'
    #               .format(k, self.period, est_period, 100 * error))
    #         self.delta_period += (est_period - self.period)
            
    #         # counter
    #         k = k + 1
    #         if k > K:
    #             warnings.warn("Could not calibrate to '{}' accuracy".format(eps))
    #             break

    #     print('< ...done.')

    #     # restore controllers
    #     self.controller1 = controller1
    #     self.controller2 = controller2
    #     self.echo = echo

    def _run(self):
        # Loop
        self.is_running = True
        #self.time_current = perf_counter() - self.time_origin
        #self.time_current = self.get_clock() - self.time_origin
        while self.is_running:

            # Call run
            self.run()

    def run(self):
        # Run the loop

        # Read all sources
        for label in self.sources_order:
            device = self.sources[label]
            source = device['block']
            if source.is_enabled():
                # retrieve outputs
                self.signals.update(dict(zip(device['outputs'], 
                                             source.read())))

        #encoder1, pot1, encoder2, pot2 = self.read_sensors()
        #time_stamp = perf_counter() - self.time_origin

        # Get time stamp
        #time_stamp = self.signals['clock'] - self.time_origin

        # Process all filters
        for label in self.filters_order:
            device = self.filters[label]
            fltr = device['block']
            if fltr.is_enabled():
                # write inputs
                fltr.write(list(self.signals[label] 
                                   for label in device['inputs']))
                # retrieve outputs
                self.signals.update(dict(zip(device['outputs'], 
                                             fltr.read())))


        # # Calculate delta T
        # time_delta = time_stamp - self.time_current
        # if self.delta_mode or time_delta == 0:
        #     time_delta = self.period
        #     # if abs(time_delta / self.period) > 1.2:
        #     #     print('time_delta = {}'.format(time_delta))

        # # Update reference
        # if self.reference1_mode:
        #     reference1 = 2 * (pot1 - 50)
        # else:
        #     reference1 = self.signals['reference1']

        # if self.reference2_mode:
        #     reference2 = 2 * (pot2 - 50)
        # else:
        #     reference2 = self.reference2

        # # Call controller
        # pwm1 = pwm2 = 0
        # if self.controller1 is not None:
        #     pwm1 = self.controller1.update(encoder1, reference1, time_delta)
        #     if pwm1 > 0:
        #         pwm1 = min(pwm1, 100)
        #     else:
        #         pwm1 = max(pwm1, -100)
        #     self.set_motor1_pwm(pwm1)

        # if self.controller2 is not None:
        #     pwm2 = self.controller2.update(encoder2, reference2, time_delta)
        #     if pwm2 > 0:
        #         pwm2 = min(pwm2, 100)
        #     else:
        #         pwm2 = max(pwm2, -100)
        #     self.set_motor2_pwm(pwm2)

        # Write to all sinks
        for label in self.sinks_order:
            device = self.sinks[label]
            sink = device['block']
            if sink.is_enabled():
                # write inputs
                if device['inputs'] == '*':
                    sink.write(self.signals.values())
                else:
                    sink.write(self.signals[label] 
                               for label in device['inputs'])

        # # Log data
        # self.data[self.current, :] = ( time_stamp,
        #                                encoder1, reference1, pwm1,
        #                                encoder2, reference2, pwm2 )

        # if self.current < self.data.shape[0] - 1:
        #     # increment current pointer
        #     self.current += 1
        # else:
        #     # reset current pointer
        #     self.current = 0
        #     self.page += 1

        # # Echo
        # if self.echo:
        #     coeff, self.echo_counter = divmod(self.echo_counter, self.echo)
        #     if self.echo_counter == 0:
        #         print('\r  {0:12.4f}'.format(time_stamp), end='')
        #         if self.controller1 is not None:
        #             if isinstance(self.controller1, algo.VelocityController):
        #                 print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
        #                       .format(self.controller1.velocity,
        #                               reference1, pwm1),
        #                       end='')
        #             else:
        #                 print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
        #                       .format(encoder1, reference1, pwm1),
        #                       end='')
        #         if self.controller2 is not None:
        #             if isinstance(self.controller2, algo.VelocityController):
        #                 print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
        #                       .format(self.controller2.velocity,
        #                               reference2, pwm2),
        #                       end='')
        #             else:
        #                 print(' {0:+10.2f} {1:+6.1f} {2:+6.1f}'
        #                       .format(encoder2, reference2, pwm2),
        #                       end='')
        #     self.echo_counter += 1

        # Update current time
        # self.time_current = time_stamp

    # def read_sensors(self):
    #     # Randomly generate sensor outputs
    #     self.encoder1 = random.randint(0,65355)/653.55;
    #     self.pot1 = random.randint(0,65355)/653.55;

    #     self.encoder2 = random.randint(0,65355)/653.55;
    #     self.pot2 = random.randint(0,65355)/653.55;

    #     return (self.encoder1, self.pot1, self.encoder2, self.pot2)

    # def set_encoder1(self, value):
    #     self.encoder1 = value

    # def set_encoder2(self, value):
    #     self.encoder2 = value

    # "public"

    def set_controller1(self, algorithm = None):
        self.controller1 = algorithm
        self.set_reference1(0)

    def set_controller2(self, algorithm = None):
        self.controller2 = algorithm
        self.set_reference2(0)

    def set_reference1(self, value = 0):
        self.signals['reference1'] = value

    def set_reference2(self, value = 0):
        self.reference2 = value

    def set_reference1_mode(self, value = 0):
        self.reference1_mode = value

    def set_reference2_mode(self, value = 0):
        self.reference2_mode = value

    def set_echo(self, value):
        self.echo = int(value)

    def set_period(self, value = 0.1):
        self.period = value

    # TODO: Complete get methods
    # TODO: Test Controller

    def get_echo(self):
        return self.echo

    def get_period(self):
        return self.period

    # def get_encoder1(self):
    #     return perf_counter(), self.encoder1

    # def get_encoder2(self):
    #     return perf_counter(), self.encoder2

    # def get_pot1(self):
    #     return perf_counter(), self.pot1

    # def get_pot2(self):
    #     return perf_counter(), self.pot2

    # def set_logger(self, duration):
    #     self.data = numpy.zeros((math.ceil(duration/self.period), 7), float)
    #     self.reset_logger()

    # def reset_logger(self):
    #     self.page = 0
    #     self.current = 0
    #     #self.time_origin = perf_counter()
    #     self.time_origin = self.get_clock()
    #     self.time_current = 0 

    # def get_log(self):
    #     if self.page == 0:
    #         return self.data[:self.current,:]
    #     else:
    #         return numpy.vstack((self.data[self.current:,:],
    #                              self.data[:self.current,:]))

    # def get_sample_number(self):
    #     return self.page * self.data.shape[0] + self.current
            
    def start(self):
        """Start controller loop"""
        # # Heading
        # if self.echo:
        #     print('          TIME', end='')
        #     if self.controller1 is not None:
        #         if isinstance(self.controller1, algo.VelocityController):
        #             print('       VEL1   REF1   PWM1', end='')
        #         else:
        #             print('       POS1   REF1   PWM1', end='')
        #     if self.controller2 is not None:
        #         if isinstance(self.controller2, algo.VelocityController):
        #             print('       VEL2   REF2   PWM2', end='')
        #         else:
        #             print('       POS2   REF2   PWM2', end='')
        #     print('')

        # Start thread
        self.thread = Thread(target = self._run)
        self.thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
        # if self.echo:
        #     print('')
