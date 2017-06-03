import warnings
from threading import Thread, Timer, Condition
import numpy
import importlib

from . import block

# alternative perf_counter
import sys
from time import perf_counter

class ControllerWarning(Warning):
    pass

class ControllerException(Exception):
    pass

# state
IDLE = 0
RUNNING = 1
EXITING = 2

class Controller:
    """
    :py:class:`pyctrl.Controller` provides functionality for running
    signal flow tasks.

    A Controller can be in one of three states:

    1. IDLE
    2. RUNNING
    3. EXITING

    Upon initialization a Controller state is set to IDLE.

    :param kwargs: should be left empty
    :raises: :py:class:`pyctrl.ControllerException` if any parameters are passed to py:data`**kwargs`

    """
    def __init__(self, **kwargs):

        # debug
        self.debug = 0

        # state
        self.state = IDLE
        
        # real-time loop
        self.is_running = False

        # duty
        self.duty = 0

        # noclock
        self.noclock = kwargs.pop('noclock', False)
        
        # no arguments are supposed to be left out
        if len(kwargs) > 0:
            raise ControllerException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

        # call __reset
        self.__reset()

    def __reset(self):

        # signals
        self.signals = { 'is_running': self.is_running, 
                         'duty': self.duty }

        # devices
        self.devices = { }

        # sources
        self.sources = { }
        self.sources_order = [ ]

        # sinks
        self.sinks = { }
        self.sinks_order = [ ]

        # filters
        self.filters = { }
        self.filters_order = [ ]

        # timers
        self.timers = { }
        self.running_timers = { }

        if not self.noclock:

            # add signal clock
            self.add_signal('clock')

            # add device clock
            self.add_device('clock',
                            'pyctrl.block.clock', 'Clock',
                            type = 'source', 
                            outputs = ['clock'],
                            verbose = False,
                            enable = True)

            # reset clock
            self.set_source('clock', reset=True)
        
    # __str__ and __repr__
    def __str__(self):
        return self.info()

    __repr__ = __str__
    
    # reset
    def reset(self):
        """
        Stop the controller, remove all devices, sources, sinks,
        filters, and all signals except `is_running` and `duty`.

        Objects that inherit from `Controller` can customize `reset()`
        by overloading the private method `__reset()`.
        """
        # call stop
        self.stop()

        # call __reset
        self.__reset()

    # get_state
    def get_state(self):
        """
        Return the current state of the Controller.

        :return: the state of the Controller
        """
        return self.state

    # set_state
    def set_state(self, state):
        """
        Set the current state of the Controller.

        :param state: the state of the controller
        """
        self.state = state
    
    # info
    def info(self, *vargs):
        """
        Returns a string with information on the Controller.

        :param options: can be one of `devices`, `signals`, `sources`, `filters`, `sinks`, `timers`, `all`, `summary`, or `class`
        :return: string with information on the Controller
        """

        # default is summary
        if not vargs:
            vargs = ('summary',)

        # initialize result
        result = ''

        # all?
        if 'all' in vargs:
            vargs = ('summary',
                     'devices', 'timers', 'signals',
                     'sources', 'filters', 'sinks')
        
        for options in vargs:
        
            options = options.lower()

            if options == 'devices':

                result += '> devices\n'
                k = 1
                for label, device in self.devices.items():
                    result += '  {}. '.format(k) + \
                              label + '[' + \
                              device['type'] + ']\n'
                    k += 1

            elif options == 'sources':

                result += '> sources\n'
                for (k, label) in enumerate(self.sources_order):
                    device = self.sources[label]
                    source = device['block']
                    result += '  {}. '.format(k+1) + \
                              label + '[' + \
                              type(source).__name__ + ', '
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
                              ' >> ' + label + '[' + \
                              type(filter_).__name__ + ', '
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
                              ' >> ' + label + '[' + \
                              type(sink).__name__ + ', '
                    if sink.is_enabled():
                        result += 'enabled'
                    else:
                        result += 'disabled'
                    result += ']' + '\n'

            elif options == 'timers':

                result += '> timers\n'
                for (k,label) in enumerate(self.timers):
                    device = self.timers[label]
                    block_ = device['block']
                    result += '  {}. '.format(k+1)
                    if device['inputs']:
                        result += ', '.join(device['inputs']) + ' >> '
                    result += label + '[' + \
                              type(block_).__name__ + ', '
                    result += 'period = {}, '.format(device['period'])
                    if device['repeat']:
                        result += 'repeat, '
                    if block_.is_enabled():
                        result += 'enabled'
                    else:
                        result += 'disabled'
                    result += ']'
                    if device['outputs']:
                        result += ' >> ' + ', '.join(device['outputs'])
                    result += '\n'

            elif options == 'signals':

                result += '> signals\n  ' + \
                          '\n  '.join('{}. {}'.format(k+1,key) 
                                      for k,key in 
                                      enumerate(sorted(self.signals.keys()))) + '\n'

            elif options == 'class':

                result += '{}'.format(self.__class__)

            elif options == 'summary':

                result += '{} with:\n  {} device(s), {} timer(s), {} signal(s),\n  {} source(s), {} filter(s), and {} sink(s)\n' \
                    .format(self.__class__,
                            len(self.devices),
                            len(self.timers),
                            len(self.signals),
                            len(self.sources), 
                            len(self.filters),
                            len(self.sinks))

            else:
                warnings.warn("Unknown option '{}'.".format(options))

        return result

    # signals
    def add_signal(self, label):
        """
        Add signal to Controller.

        :param str label: the signal label
        """
        assert isinstance(label, str)
        if label in self.signals:
            warnings.warn("Signal '{}' already present.".format(label),
                          ControllerWarning)
        else:
            self.signals[label] = 0

    def add_signals(self, *labels):
        """
        Add multiple signal to Controller.

        :param vargs labels: the signal labels
        """
        for label in labels:
            self.add_signal(label)

    def remove_signal(self, label):
        """
        Remove signal from Controller.

        :param str label: the signal label to be removed
        """
        # used in a source?
        for (l, device) in self.sources.items():
            if label in device['outputs']:
                warnings.warn("Signal '{}' still in use by source '{}' and can't be removed.".format(label, l),
                              ControllerWarning)
                return

        # used in a filter?
        for (l, device) in self.filters.items():
            if label in device['outputs'] or label in device['inputs']:
                warnings.warn("Signal '{}' still in use by filter '{}' and can't be removed.".format(label, l),
                              ControllerWarning)
                return
                
        # used in a sink?
        for (l, device) in self.sinks.items():
            if label in device['inputs']:
                warnings.warn("Signal '{}' still in use by sink '{}' and can't be removed.".format(label, l),
                              ControllerWarning)
                return
                
        # used in a filter?
        for (l, device) in self.timers.items():
            if label in device['outputs'] or label in device['inputs']:
                warnings.warn("Signal '{}' still in use by timer '{}' and can't be removed.".format(label, l),
                              ControllerWarning)
                return

        # otherwise go ahead
        self.signals.pop(label)

    def set_signal(self, label, value):
        """
        Set the value of signal.

        :param str label: the signal label
        :param value: the value to be set
        """
        if label not in self.signals:
            raise ControllerException("Signal '{}' does not exist".format(label))
        self.signals[label] = value

    def get_signal(self, label):
        """
        Get the value of signal.

        :param str label: the signal label
        :return: the signal value
        """
        return self.signals[label]

    def get_signals(self, *labels):
        """
        Get the value of signals.

        :param vargs labels: the signal labels
        :return: the signal values
        :rtype: list
        """
        return [self.signals[label] for label in labels]

    def list_signals(self):
        """
        List of the signals currently on Controller.

        :return: a list of signal labels
        :rtype: list
        """
        return list(self.signals.keys())

    # sources
    def add_source(self, label, source, outputs, order = -1):
        """
        Add source to Controller.

        :param str label: the source label
        :param pyctrl.block source: the source block
        :param list outputs: a list of output signals
        :param int order: if positive, set execution order, otherwise add as last (default `-1`)
        """
        assert isinstance(label, str)
        if label in self.sources:
            warnings.warn("Source '{}' already exists and is been replaced.".format(label),
                          ControllerWarning)
            self.remove_source(label)

        assert isinstance(source, block.Block)
        assert isinstance(outputs, (list, tuple))
        self.sources[label] = {
            'block': source,
            'outputs': outputs
        }
        if order < 0:
            self.sources_order.append(label)
        else:
            self.sources_order.insert(order, label)

        # make sure output signals exist
        for s in outputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added.".format(s),
                              ControllerWarning)
                self.add_signal(s)

    def remove_source(self, label):
        """
        Remove source from Controller.

        :param str label: the source label
        """
        self.sources_order.remove(label)
        self.sources.pop(label)

    def set_source(self, label, **kwargs):
        """
        Set source attributes.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the source label
        :param list outputs: set source output signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        if label not in self.sources:
            raise ControllerException("Source '{}' does not exist".format(label))

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.sources[label]['outputs'] = values

        self.sources[label]['block'].set(**kwargs)

    def get_source(self, label, *keys):
        """
        Get attributes from source.

        :param str label: the source label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes or single value
        :rtype: dict or value
        """
        if label not in self.sources:
            raise ControllerException("Source '{}' does not exist".format(label))

        return self.sources[label]['block'].get(*keys)

    def read_source(self, label):
        """
        Read from source. Call method `pyctrl.block.read()`.
        
        :param str label: the source label
        """
        return self.sources[label]['block'].read()

    def write_source(self, label, *values):
        """
        Write to source. Call method `pyctrl.block.write(*values)`.
        
        :param str label: the source label
        :param vargs values: the values to write to source
        """
        self.sources[label]['block'].write(*values)

    def list_sources(self):
        """
        List of the sources currently on Controller.

        :return: a list of source labels
        :rtype: list
        """
        return list(self.sources.keys())


    # sinks
    def add_sink(self, label, sink, inputs, order = -1):
        """
        Add sink to Controller.

        :param str label: the sink label
        :param pyctrl.block sink: the sink block
        :param list inputs: a list of input signals
        :param int order: if positive, set execution order, otherwise add as last (default `-1`)
        """
        assert isinstance(label, str)
        if label in self.sinks:
            warnings.warn("Sink '{}' already exists and is been replaced.".format(label), 
                          ControllerWarning)
            self.remove_sink(label)

        assert isinstance(sink, block.Block)
        assert inputs == '*' or isinstance(inputs, (list, tuple))
        self.sinks[label] = {
            'block': sink,
            'inputs': inputs
        }
        if order < 0:
            self.sinks_order.append(label)
        else:
            self.sinks_order.insert(order, label)

        # make sure input signals exist
        for s in inputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added.".format(s),
                              ControllerWarning)
                self.add_signal(s)
                
    def remove_sink(self, label):
        """
        Remove sink from Controller.

        :param str label: the sink label
        """
        self.sinks_order.remove(label)
        self.sinks.pop(label)

    def set_sink(self, label, **kwargs):
        """
        Set sink attributes.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the sink label
        :param list inputs: set sink input signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        if label not in self.sinks:
            raise ControllerException("Sink '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.sinks[label]['inputs'] = values
            
        self.sinks[label]['block'].set(**kwargs)

    def get_sink(self, label, *keys):
        """
        Get attributes from sink.

        :param str label: the sink label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes
        :rtype: dict
        """
        if label not in self.sinks:
            raise ControllerException("Sink '{}' does not exist".format(label))

        return self.sinks[label]['block'].get(*keys)

    def read_sink(self, label):
        """
        Read from sink. Call method `pyctrl.block.read()`.
        
        :param str label: the sink label
        """
        return self.sinks[label]['block'].read()

    def write_sink(self, label, *values):
        """
        Write to sink. Call method `pyctrl.block.write(*values)`.
        
        :param str label: the sink label
        :param vargs values: the values to write to sink
        """
        self.sinks[label]['block'].write(*values)

    def list_sinks(self):
        """
        List of the sinks currently on Controller.

        :return: a list of sink labels
        :rtype: list
        """
        return list(self.sinks.keys())

    # filters
    def add_filter(self, label, 
                   filter_, inputs, outputs, 
                   order = -1):
        """
        Add filter to Controller.

        :param str label: the filter label
        :param pyctrl.block filter: the filter block
        :param list inputs: a list of input signals
        :param list outputs: a list of output signals
        :param int order: if positive, set execution order, otherwise add as last (default `-1`)
        """
        assert isinstance(label, str)
        if label in self.filters:
            warnings.warn("Filter '{}' already exists and is been replaced.".format(label),
                          ControllerWarning)
            self.remove_filter(label)

        assert isinstance(filter_, block.Block)
        assert isinstance(inputs, (list, tuple))
        assert isinstance(outputs, (list, tuple))
        self.filters[label] = { 
            'block': filter_,  
            'inputs': inputs,
            'outputs': outputs
        }
        if order < 0:
            self.filters_order.append(label)
        else:
            self.filters_order.insert(order, label)

        # make sure input signals exist
        for s in inputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added.".format(s),
                              ControllerWarning)
                self.add_signal(s)
                
        # make sure output signals exist
        for s in outputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added".format(s),
                              ControllerWarning)
                self.add_signal(s)
            
    def remove_filter(self, label):
        """
        Remove filter from Controller.

        :param str label: the filter label
        """
        self.filters_order.remove(label)
        self.filters.pop(label)

    def set_filter(self, label, **kwargs):
        """
        Set filter attributes.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the filter label
        :param list inputs: set filter input signals
        :param list outputs: set filter output signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        if label not in self.filters:
            raise ControllerException("Filter '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.filters[label]['inputs'] = values

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.filters[label]['outputs'] = values

        self.filters[label]['block'].set(**kwargs)
            
    def get_filter(self, label, *keys):
        """
        Get attributes from filter.

        :param str label: the filter label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes
        :rtype: dict
        """
        if label not in self.filters:
            raise ControllerException("Filter '{}' does not exist".format(label))

        return self.filters[label]['block'].get(*keys)

    def read_filter(self, label):
        """
        Read from filter. Call method `pyctrl.block.read()`.
        
        :param str label: the filter label
        """
        return self.filters[label]['block'].read()

    def write_filter(self, label, *values):
        """
        Write to filter. Call method `pyctrl.block.write(*values)`.
        
        :param str label: the filter label
        :param vargs values: the values to write to filter
        """
        self.filters[label]['block'].write(*values)

    def list_filters(self):
        """
        List of the filters currently on Controller.

        :return: a list of filter labels
        :rtype: list
        """
        return list(self.filters.keys())

    # devices
    def add_device(self, 
                   label, device_module, device_class, 
                   **kwargs):
        """
        Add device to Controller.

        :param str label: the device label
        :param str device_module: the device module
        :param str device_class: the device class
        :param str type: the device type, `source`, `filter`, or `sink` (default `source`)
        :param bool enable: if the device needs to be enable at `start()` and disabled at `stop()` (default False)
        :param list inputs: a list of input signals (default `[]`)
        :param list outputs: a list of output signals (default `[]`)
        :param bool verbose: if verbose issue warning (default `False`)
        :param kwargs kwargs: parameters to be passed to the device class initialization
        """

        # parameters
        devtype = kwargs.pop('type', 'source')
        enable = kwargs.pop('enable', False)
        force = kwargs.pop('force', False)

        inputs = kwargs.pop('inputs', [])
        outputs = kwargs.pop('outputs', [])

        verbose = kwargs.pop('verbose', True)
        
        # Install device
        if verbose:
            warnings.warn("> Installing device '{}'".format(label))

        try:

            # create device
            obj_class = getattr(importlib.import_module(device_module), 
                                device_class)
            instance = obj_class(**kwargs)

        except Exception as e:

            warnings.warn("> Exception raised:\n  {}".format(e))
            warnings.warn("> Failed to install device '{}'".format(label))
            return None

        # add device to controller
        if devtype == 'source':

            # warn if inputs are defined
            if inputs:
                warnings.warn("Sources do not have inputs. Inputs ignored.",
                              ControllerWarning)

            # add device as source
            self.add_source(label, instance, outputs)
            
        elif devtype == 'sink':

            # warn if inputs are defined
            if outputs:
                warnings.warn("Sinks do not have outputs. Outputs ignored.",
                              ControllerWarning)

            # add device as sink
            self.add_sink(label, instance, inputs)

        elif devtype == 'filter':

            # add device as filter
            self.add_filter(label, instance, inputs, outputs)

        else:
            
            raise NameError("Unknown device type '{}'. Must be sink, source or filter.".format(devtype))

        # add signals
        #self.add_signals(*outputs)
        #self.add_signals(*inputs)

        # store device
        self.devices[label] = {
            'instance': instance,
            'type': devtype,
            'inputs': inputs,
            'outputs': outputs,
            'enable': enable,
            'params': kwargs
        }

        return instance

    def list_devices(self):
        """
        List of the devices currently on Controller.

        :return: a list of devices labels
        :rtype: list
        """
        return list(self.devices.keys())
    
    # timers
    def add_timer(self,
                  label,
                  blk,
                  inputs,
                  outputs,
                  period,
                  repeat = True):
        """
        Add timer to Controller.

        :param str label: the timer label
        :param pyctrl.block blk: the timer block
        :param list inputs: a list of input signals
        :param list outputs: a list of output signals
        :param int period: run timer in period seconds
        :param bool repeat: repeat if True (default True)
        """
        assert isinstance(label, str)
        if label in self.timers:
            warnings.warn("Timer '{}' already exists and is been replaced.".format(label),
                          ControllerWarning)
            self.remove_timer(label)

        assert isinstance(blk, block.Block)
        if inputs:
            assert isinstance(inputs, (list, tuple))
        if outputs:
            assert isinstance(outputs, (list, tuple))
        assert isinstance(period, (int, float))
        assert isinstance(repeat, (int, bool))
        self.timers[label] = { 
            'block': blk,  
            'inputs': inputs,
            'outputs': outputs,
            'period': period,
            'repeat': repeat
        }

    def remove_timer(self, label):
        """
        Remove timer from Controller.

        :param str label: the timer label
        """
        self.timers.pop(label)
        
    def set_timer(self, label, **kwargs):
        """
        Set timer attributes.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the timer label
        :param list inputs: set timer input signals
        :param list outputs: set timer output signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        if label not in self.timers:
            raise ControllerException("Timer '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.timers[label]['inputs'] = values

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.timers[label]['outputs'] = values

        self.timers[label]['block'].set(**kwargs)
        
    def get_timer(self, label, *keys):
        """
        Get attributes from timer.

        :param str label: the timer label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes
        :rtype: dict
        """
        if label not in self.timers:
            raise ControllerException("Timer '{}' does not exist".format(label))

        return self.timers[label]['block'].get(*keys)

    def read_timer(self, label):
        """
        Read from timer. Call method `pyctrl.block.read()`.
        
        :param str label: the timer label
        """
        return self.timers[label]['block'].read()

    def write_timer(self, label, *values):
        """
        Write to timer. Call method `pyctrl.block.write(*values)`.
        
        :param str label: the timer label
        :param vargs values: the values to write to timer
        """
        self.timers[label]['block'].write(*values)

    def list_timers(self):
        """
        List of the timers currently on Controller.

        :return: a list of timer labels
        :rtype: list
        """
        return list(self.timers.keys())
        
    def __enter__(self):
        if self.debug > 0:
            print('> Starting controller')
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if self.debug > 0:
            print('> Stoping controller')
        self.stop()

    def run(self):

        # Loop
        self.is_running = True
        self.signals['is_running'] = self.is_running

        self.duty = 0
        self.signals['duty'] = self.duty

        while self.is_running and self.state != EXITING:

            # Run the loop
            #print("*** LOOP ****")
            
            # Read all sources
            first = True
            t0 = 0
            for label in self.sources_order:
                block = self.sources[label]
                source = block['block']
                if source.is_enabled():
                    # retrieve outputs
                    self.signals.update(dict(zip(block['outputs'], 
                                                 source.read())))
                    # Begin profiling
                    if first:
                        t0 = perf_counter()
                        first = False

            # Process all filters
            for label in self.filters_order:
                block = self.filters[label]
                fltr = block['block']
                if fltr.is_enabled():
                    # write signals to inputs
                    fltr.write(*[self.signals[label] 
                                 for label in block['inputs']])
                    # retrieve outputs
                    self.signals.update(dict(zip(block['outputs'], 
                                                 fltr.read())))

            # Write to all sinks
            for label in self.sinks_order:
                block = self.sinks[label]
                sink = block['block']
                if sink.is_enabled():
                    # write inputs
                    sink.write(*[self.signals[label]
                                 for label in block['inputs']])

            # update is_running
            self.is_running = self.signals['is_running']

            # update duty
            duty = perf_counter() - t0
            self.signals['duty'] = duty
            self.duty = max(self.duty, duty)

    def tick(self, label, device):

        # Acquire lock
        device['condition'].acquire()

        # Got a tick, run device
        
        if device['inputs']:
            
            # write signals to inputs
            device['block'].write(*[self.signals[label] 
                                    for label in device['inputs']])
            
        if device['outputs']:
                
            # retrieve outputs
            self.signals.update(dict(zip(device['outputs'], 
                                         device['block'].read())))

        # Notify lock
        device['condition'].notify_all()
        
        # Release lock
        device['condition'].release()
    
    def run_timer(self, label, device):

        while self.is_running and self.state != EXITING:

            # Acquire condition
            device['condition'].acquire()
            
            # Setup timer
            self.running_timers[label] = Timer(device['period'],
                                               self.tick,
                                               args = (label, device))
            self.running_timers[label].start()

            # Wait 
            device['condition'].wait()

            # and release
            device['condition'].release()

            # repeat
            if not device['repeat']:
                break
            
    def start(self):
        """
        Start Controller loop.
        """

        # enable devices
        for label, device in self.devices.items():
            if device['enable']:
                device['instance'].set_enabled(True)

        # Start thread
        self.thread = Thread(target = self.run)
        self.thread.start()

        # start timer threads
        for label, device in self.timers.items():
            device['condition'] = Condition()
            thread = Thread(target = self.run_timer,
                            args = (label, device))
            thread.start()
        
        # change state to running
        self.state = RUNNING

    def stop(self):
        """
        Stop Controller loop.
        """

        # Stop thread
        if self.is_running:
            self.is_running = False
            self.signals['is_running'] = self.is_running

        # start timer threads
        for (label,t) in self.running_timers.items():
            # Try cancelling timer
            t.cancel()
            # Release condition
            device = self.timers[label]
            device['condition'].acquire()
            device['condition'].notify_all()
            device['condition'].release()

        self.running_timers = { }

        # then disable devices
        for label, device in self.devices.items():
            if device['enable']:
                device['instance'].set_enabled(False)

        # change state to idle
        self.state = IDLE

    def join(self):
        """
        Wait for Controller thread to terminate.
        """
        if self.thread:
            self.thread.join()
