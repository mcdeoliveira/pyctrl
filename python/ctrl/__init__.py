import warnings
from threading import Thread
import numpy

from . import block

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
    
    # period
    def set_period(self, value):
        self.period = value

    def get_period(self):
        return self.period

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

    def list_signals(self):
        return self.signals.keys()

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

    def read_source(self, label):
        return self.sources[label]['block'].read()

    def write_source(self, label, values):
        self.sources[label]['block'].write(values)

    def list_sources(self):
        return self.sources.keys()


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

    def read_sink(self, label):
        return self.sinks[label]['block'].read()

    def write_sink(self, label, values):
        self.sinks[label]['block'].write(values)

    def list_sinks(self):
        return self.sinks.keys()

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
            
    def read_filter(self, label):
        return self.filters[label]['block'].read()

    def write_filter(self, label, values):
        self.filters[label]['block'].write(values)

    def list_filters(self):
        return self.filters.keys()

    # clock

    def get_time(self):

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

    def _run(self):

        # Loop
        self.is_running = True
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
            
    def start(self):
        """Start controller loop
        """

        # Start thread
        self.thread = Thread(target = self._run)
        self.thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
