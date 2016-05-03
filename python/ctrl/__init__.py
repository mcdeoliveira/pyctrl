import warnings
from threading import Thread
import numpy
import importlib

from . import block

class ControllerWarning(Warning):
    pass

class ControllerException(Exception):
    pass

class Controller:

    def __init__(self):

        # debug
        self.debug = 0

        # real-time loop
        self.is_running = False

        # call __reset
        self.__reset()

    def __reset(self):

        # signals
        self.signals = { 'is_running': self.is_running }

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

    # __str__ and __repr__
    def __str__(self):
        return self.info()

    __repr__ = __str__
    
    # reset
    def reset(self):

        # call stop
        self.stop()

        # call __reset
        self.__reset()

    # info
    def info(self, options = 'summary'):

        options = options.lower()
        result = ''

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
                                  enumerate(sorted(self.signals.keys()))) + '\n'

        elif options == 'all':
            
            result = ''.join(map(lambda x: self.info(x), 
                                 ['summary', 'devices', 'signals', 
                                  'sources', 'filters', 'sinks']))
            
        elif options == 'summary':
        
            result += '> Controller with {} signal(s), {} source(s), {} sink(s), and {} filter(s)' \
                .format(len(self.signals),
                        len(self.sources), 
                        len(self.sinks), 
                        len(self.filters)) + '\n'

        else:
            warnings.warn("Unknown option '{}'.".format(options))

        return result

    # signals
    def add_signal(self, label):
        assert isinstance(label, str)
        if label in self.signals:
            warnings.warn("Signal '{}' already present.".format(label),
                          ControllerWarning)
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

    def list_signals(self):
        return list(self.signals.keys())

    # sources
    def add_source(self, label, source, outputs, order = -1):
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

    def remove_source(self, label):
        self.sources_order.remove(label)
        self.sources.pop(label)

    def set_source(self, label, **kwargs):

        if label not in self.sources:
            raise ControllerException("Source '{}' does not exist".format(label))

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.sources[label]['outputs'] = values

        self.sources[label]['block'].set(**kwargs)

    def get_source(self, label, *keys):
        
        if label not in self.sources:
            raise ControllerException("Source '{}' does not exist".format(label))

        return self.sources[label]['block'].get(keys)

    def read_source(self, label):
        return self.sources[label]['block'].read()

    def write_source(self, label, *values):
        self.sources[label]['block'].write(*values)

    def list_sources(self):
        return list(self.sources.keys())


    # sinks
    def add_sink(self, label, sink, inputs, order = -1):
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

    def remove_sink(self, label):
        self.sinks_order.remove(label)
        self.sinks.pop(label)

    def set_sink(self, label, **kwargs):

        if label not in self.sinks:
            raise ControllerException("Sink '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.sinks[label]['inputs'] = values
            
        self.sinks[label]['block'].set(**kwargs)

    def get_sink(self, label, *keys):
        
        if label not in self.sinks:
            raise ControllerException("Sink '{}' does not exist".format(label))

        return self.sinks[label]['block'].get(keys)

    def read_sink(self, label):
        return self.sinks[label]['block'].read()

    def write_sink(self, label, *values):
        self.sinks[label]['block'].write(*values)

    def list_sinks(self):
        return list(self.sinks.keys())

    # filters
    def add_filter(self, label, 
                   filter_, inputs, outputs, 
                   order = -1):
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

    def remove_filter(self, label):
        self.filters_order.remove(label)
        self.filters.pop(label)

    def set_filter(self, label, **kwargs):

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
        
        if label not in self.filters:
            raise ControllerException("Filter '{}' does not exist".format(label))

        return self.filters[label]['block'].get(keys)

    def read_filter(self, label):
        return self.filters[label]['block'].read()

    def write_filter(self, label, *values):
        self.filters[label]['block'].write(*values)

    def list_filters(self):
        return list(self.filters.keys())

    # devices
    def add_device(self, 
                   label, device_module, device_class, 
                   **kwargs):

        # parameters
        devtype = kwargs.pop('type', 'source')
        enable = kwargs.pop('enable', False)

        inputs = kwargs.pop('inputs', [])
        outputs = kwargs.pop('outputs', [])

        # Install device
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

            # add device as source
            self.add_sink(label, instance, inputs)

        elif devtype == 'filter':

            # add device as filter
            self.add_filter(label, instance, inputs, outputs)

        else:
            
            raise NameError("Unknown device type '{}'. Must be sink, source or filter.".format(devtype))

        # add signals
        self.add_signals(*outputs)
        self.add_signals(*inputs)

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
        while self.is_running:

            # Call run
            self._run()

    def _run(self):
        # Run the loop

        # Read all sources
        for label in self.sources_order:
            device = self.sources[label]
            source = device['block']
            if source.is_enabled():
                # retrieve outputs
                self.signals.update(dict(zip(device['outputs'], 
                                             source.read())))

        # Process all filters
        for label in self.filters_order:
            device = self.filters[label]
            fltr = device['block']
            if fltr.is_enabled():
                # write signals to inputs
                fltr.write(*[self.signals[label] 
                             for label in device['inputs']])
                # retrieve outputs
                self.signals.update(dict(zip(device['outputs'], 
                                             fltr.read())))

        # Write to all sinks
        for label in self.sinks_order:
            device = self.sinks[label]
            sink = device['block']
            if sink.is_enabled():
                # write inputs
                sink.write(*[self.signals[label]
                             for label in device['inputs']])

        # update is_running
        self.is_running = self.signals['is_running']
        
    def start(self):
        """Start controller loop
        """

        # enable devices
        for label, device in self.devices.items():
            if device['enable']:
                device['instance'].set_enabled(True)

        # Start thread
        self.thread = Thread(target = self.run)
        self.thread.start()

    def stop(self):
        """Stop controller loop
        """

        # Stop thread
        if self.is_running:
            self.is_running = False
            self.signals['is_running'] = self.is_running

        # then disable devices
        for label, device in self.devices.items():
            if device['enable']:
                device['instance'].set_enabled(False)

