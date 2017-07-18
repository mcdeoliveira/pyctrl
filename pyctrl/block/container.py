"""
This module provides the basic building blocks for implementing Containers.
"""

import warnings
import sys
import numpy
import math
import importlib
from threading import Thread, Timer, Condition
from time import perf_counter, sleep
import re

from .. import block
from .. import BlockType

class ContainerWarning(block.BlockWarning):
    pass

class ContainerException(block.BlockException):
    pass

class Input(block.Source, block.BufferBlock):
    """
    :py:class:`pyctrl.block.container.Input` provides a block that connects a container input signals to local container signals .
    """

    def write(self, *values):
        block.BufferBlock.write(self, *values)
    
class Output(block.Sink, block.BufferBlock):
    """
    :py:class:`pyctrl.block.container.Output` provides a block that connects local container signals to a container output signals.
    """
    
    def read(self):
        return block.BufferBlock.read(self)
    
class Container(block.Filter, block.Block):
    """
    :py:class:`pyctrl.block.container.Container` provides a block that can contain other blocks.
    """

    def __init__(self, **kwargs):

        # set enabled as False by default
        if 'enabled' not in kwargs:
            kwargs['enabled'] = False
        
        # call super
        super().__init__(**kwargs)

        # call _reset
        self._reset()
        
    def _reset(self):

        # disable first
        if self.enabled:
            self.set_enabled(False)
            sleep(1)
            
        # signals
        self.signals = { }

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
        
    # reset
    def reset(self):
        """
        Reset all sources, sinks, filters, and timers.
        """

        # call reset for each block
        for label in self.sources_order:
            self.sources[label]['block'].reset()

        for label in self.filters_order:
            self.filters[label]['block'].reset()

        for label in self.sinks_order:
            self.sinks[label]['block'].reset()

        for label, device in self.timers.items():
            device['block'].reset()

    # get
    def get(self, *keys, exclude = ()):
        return super().get(*keys, exclude = exclude + ("running_timers",))
            
    def html(self, *keys):
        """
        Format :py:class:`pyctrl.block.Block` in HTML.

        By default uses the result of :py:meth:`pyctrl.block.Block.get`.

        :param keys: string or tuple of strings with property names
        :raise: :py:class:`KeyError` if :py:attr:`key` is not defined
        """

        recursive = True
        
        # keys?
        if len(keys) == 0:
            keys = ('summary', 'signals', 'timers', 'sources', 'filters', 'sinks')
        
        # open div
        result = '<div>'

        # summary
        if 'summary' in keys:
            result += '<p>' + '&lt;{}&gt; with: {} timer(s), {} signal(s), {} source(s), {} filter(s), and {} sink(s)</p>' \
                      .format(str(self.__class__)[1:-1],
                              len(self.timers),
                              len(self.signals),
                              len(self.sources), 
                              len(self.filters),
                              len(self.sinks))
        
        # timers
        if 'timers' in keys:
            result += '<h2>timers</h2>'
            result += '<ol>'
            for label in self.timers:
                device = self.timers[label]
                block = device['block']
                result += '<li>'
                if device['inputs']:
                    result += ', '.join(device['inputs']) + ' &Gt; '
                result += label + '[' + \
                    type(block).__name__ + ', '
                result += 'period = {}, '.format(device['period'])
                if device['repeat']:
                    result += 'repeat, '
                    if block.is_enabled():
                        result += 'enabled'
                    else:
                        result += 'disabled'
                    result += ']'
                    if device['outputs']:
                        result += ' &Gt; ' + ', '.join(device['outputs'])
                    result += '</li>'
                if recursive and isinstance(block, Container):
                    result += block.info(*vargs, **fkwargs)
            result += '</ol>'
            
        # sources
        if 'sources' in keys:
            result += '<h2>signals</h2>'
            result += '<ol>'
            for label in sorted(self.signals.keys()):
                result += '<li>' + label + '</li>'
            result += '</ol>'

            # sources
            result += '<h2>sources</h2>'
            result += '<ol>'
            for label in self.sources_order:
                device = self.sources[label]
                block = device['block']
                result += '<li>' + label + '[' + \
                          type(block).__name__ + ', '
                if block.is_enabled():
                    result += 'enabled'
                else:
                    result += 'disabled'
                result += '] &Gt; ' + ', '.join(device['outputs']) + '</li>'
            result += '</ol>'

        # filters
        if 'filters' in keys:
            result += '<h2>filters</h2>'
            result += '<ol>'
            for label in self.filters_order:
                device = self.filters[label]
                block = device['block']
                result += '<li>' + ', '.join(device['inputs']) + \
                          ' &Gt; ' + label + '[' + \
                          type(block).__name__ + ', '
                if block.is_enabled():
                    result += 'enabled'
                else:
                    result += 'disabled'
                result += '] &Gt; ' + ', '.join(device['outputs']) + '</li>'
                if isinstance(block, Container):
                    result += block.html(*keys)
            result += '</ol>'

        # sinks
        if 'sinks' in keys:
            result += '<h2>sinks</h2>'
            result += '<ol>'
            for label in self.sinks_order:
                device = self.sinks[label]
                block = device['block']
                result += '<li>' + ', '.join(device['inputs']) + \
                          ' &Gt; ' + label + '[' + \
                          type(block).__name__ + ', '
                if block.is_enabled():
                    result += 'enabled'
                else:
                    result += 'disabled'
                result += ']' + '</li>'
            result += '</ol>'

        # close div
        result += '</div>'

        return result
        
    # info
    def info(self, *vargs, **kwargs):
        """
        Returns a string with information on the Container.

        :param options: can be one of `signals`, `devices`, `sources`, `filters`, `sinks`, `timers`, `all`, `summary`, or `class`
        :return: string with information on the Container
        """

        # default is summary
        if not vargs:
            vargs = ('summary',)

        # initialize result
        result = ''

        # all?
        if 'all' in vargs:
            vargs = ('summary',
                     'timers', 'signals',
                     'sources', 'filters', 'sinks')

        # recurse
        recursive = kwargs.pop('recursive', True)

        # indent
        indent = ' ' * kwargs.pop('indent', 0)
        
        for options in vargs:
        
            options = options.lower()

            if options == 'sources':

                result += indent + '> sources\n'
                for (k, label) in enumerate(self.sources_order):
                    device = self.sources[label]
                    source = device['block']
                    result += indent + '  {}. '.format(k+1) + \
                              label + '[' + \
                              type(source).__name__ + ', '
                    if source.is_enabled():
                        result += 'enabled'
                    else:
                        result += 'disabled'
                    result += '] >> ' + ', '.join(device['outputs']) + '\n'

            elif options == 'filters':

                fkwargs = kwargs
                fkwargs.update({'indent': len(indent) + 5})
                
                result += indent + '> filters\n'
                for (k,label) in enumerate(self.filters_order):
                    device = self.filters[label]
                    filter_ = device['block']
                    result += indent + '  {}. '.format(k+1) + \
                              ', '.join(device['inputs']) + \
                              ' >> ' + label + '[' + \
                              type(filter_).__name__ + ', '
                    if filter_.is_enabled():
                        result += 'enabled'
                    else:
                        result += 'disabled'
                    result += '] >> ' + ', '.join(device['outputs']) + '\n'
                    if recursive and isinstance(filter_, Container):
                        result += filter_.info(*vargs, **fkwargs)
                        

            elif options == 'sinks':

                result += indent + '> sinks\n'
                for (k, label) in enumerate(self.sinks_order):
                    device = self.sinks[label]
                    sink = device['block']
                    result += indent + '  {}. '.format(k+1) + \
                              ', '.join(device['inputs']) + \
                              ' >> ' + label + '[' + \
                              type(sink).__name__ + ', '
                    if sink.is_enabled():
                        result += 'enabled'
                    else:
                        result += 'disabled'
                    result += ']' + '\n'

            elif options == 'timers':

                fkwargs = kwargs
                fkwargs.update({'indent': len(indent) + 5})
                
                result += indent + '> timers\n'
                for (k,label) in enumerate(self.timers):
                    device = self.timers[label]
                    block_ = device['block']
                    result += indent + '  {}. '.format(k+1)
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
                    if recursive and isinstance(block_, Container):
                        result += block_.info(*vargs, **fkwargs)

            elif options == 'signals':

                result += indent + '> signals' + \
                          ''.join('\n  ' + indent + '{}. {}'.format(k+1,key) 
                                  for k,key in 
                                  enumerate(sorted(self.signals.keys()))) + '\n'

            elif options == 'class':

                result += '{}'.format(self.__class__)

            elif options == 'summary':

                result += (indent + '{} with:\n' + indent + '  {} timer(s), {} signal(s),\n' + indent + '  {} source(s), {} filter(s), and {} sink(s)\n') \
                    .format(self.__class__,
                            len(self.timers),
                            len(self.signals),
                            len(self.sources), 
                            len(self.filters),
                            len(self.sinks))

            else:
                warnings.warn("Unknown option '{}'.".format(options))

        return result

    # get container
    def resolve_label(self, label):
        
        # parse label
        split_label = label.split(sep='/',maxsplit = 1)

        # global name starting with '/'
        if split_label[0] == '':
            if self.parent:
                # pass to parent
                return self.parent.resolve_label(label)
            else:
                # or treat as local name
                split_label[0] = '.'
            
        # parent name starting with '..'
        if split_label[0] == '..':
            if self.parent:
                # pass to parent
                return self.parent.resolve_label(split_label[1])
            else:
                raise ContainerException("Container '..' does not exist")
            
        # local name starting with '.'
        if split_label[0] == '.':
            # split again
            split_label = split_label[1].split(sep='/',maxsplit = 1)

        if len(split_label) > 1:
            # inside container?
            try:

                # special timer label?
                if split_label[0] == 'timer':

                    # split again
                    split_label = split_label[1].split(sep='/',maxsplit = 1)

                    # retrieve container from timers
                    container = self.timers[split_label[0]]['block']
                    if isinstance(container, Container):
                        return container.resolve_label(split_label[1])
                    else:
                        raise ContainerException("Timer '{}' is not a container".format(label))
                        
                else:

                    # retrieve container from filters
                    container = self.filters[split_label[0]]['block']
                    if isinstance(container, Container):
                        return container.resolve_label(split_label[1])
                    else:
                        raise ContainerException("Filter '{}' is not a container".format(label))
            except KeyError:
                raise ContainerException("Container '{}' does not exist".format(label))

        else:
            # otherwise return local name
            return (self, split_label[0])

    # signals
    def add_signal(self, label):
        """
        Add signal to Container.

        :param str label: the signal label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.add_signal(label)

        # local signal
        if label in self.signals:
            warnings.warn("Signal '{}' already present.".format(label),
                          ContainerWarning)
        else:
            self.signals[label] = 0

    def add_signals(self, *labels):
        """
        Add multiple signal to Container.

        :param vargs labels: the signal labels
        """
        for label in labels:
            self.add_signal(label)

    def remove_signal(self, label):
        """
        Remove signal from Container.

        :param str label: the signal label to be removed
        """

        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.remove_signal(label)

        # used in a source?
        for (l, device) in self.sources.items():
            if label in device['outputs']:
                warnings.warn("Signal '{}' still in use by source '{}' and can't be removed.".format(label, l),
                              ContainerWarning)
                return

        # used in a filter?
        for (l, device) in self.filters.items():
            if label in device['outputs'] or label in device['inputs']:
                warnings.warn("Signal '{}' still in use by filter '{}' and can't be removed.".format(label, l),
                              ContainerWarning)
                return
                
        # used in a sink?
        for (l, device) in self.sinks.items():
            if label in device['inputs']:
                warnings.warn("Signal '{}' still in use by sink '{}' and can't be removed.".format(label, l),
                              ContainerWarning)
                return
                
        # used in a filter?
        for (l, device) in self.timers.items():
            if label in device['outputs'] or label in device['inputs']:
                warnings.warn("Signal '{}' still in use by timer '{}' and can't be removed.".format(label, l),
                              ContainerWarning)
                return

        # otherwise go ahead
        self.signals.pop(label)

    def set_signal(self, label, value):
        """
        Set the value of signal. Call method :py:meth:`pyctrl.block.Block.set`.

        :param str label: the signal label
        :param value: the value to be set
        """

        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.set_signal(label, value)

        # local signal
        if label not in self.signals:
            raise ContainerException("Signal '{}' does not exist".format(label))
        self.signals[label] = value

    def get_signal(self, label):
        """
        Get the value of signal.

        :param str label: the signal label
        :return: the signal value
        """
        
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.get_signal(label)

        # local label
        return self.signals[label]

    def get_signals(self, *labels):
        """
        Get the values of signals.

        :param vargs labels: the signal labels
        :return: the signal values
        :rtype: list
        """
        return [self.signals[label] for label in labels]

    def list_signals(self):
        """
        List of the signals currently on Container.

        :return: a list of signal labels
        :rtype: list
        """
        return list(self.signals.keys())

    # sources
    def add_source(self, label, source, outputs, **kwargs):
        """
        Add source to Container.

        :param str label: the source label
        :param pyctrl.block source: the source block
        :param list outputs: a list of output signals
        :param int order: if positive, set execution order, otherwise add as last (default `-1`)
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.add_source(label, source,
                                        outputs, **kwargs)

        # local label
        if label in self.sources:
            warnings.warn("Source '{}' already exists and is been replaced.".format(label),
                          ContainerWarning)
            self.remove_source(label)

        # object or tuple?
        if isinstance(source, tuple):

            # dkwargs
            dkwargs = kwargs.pop('kwargs', {})

            # create device
            device_module, device_class = source
            source = getattr(importlib.import_module(device_module), 
                             device_class)(**dkwargs)
            
        assert isinstance(source, block.Block)
        assert isinstance(source, block.Source)
        assert isinstance(outputs, (list, tuple))

        # order
        order = kwargs.pop('order', None)
        
        # enable
        enable = kwargs.pop('enable', None)
        if enable is None:
            if isinstance(source, Container):
                enable = True
            else:
                enable = False

        # left over arguments?
        if len(kwargs) > 0:
            raise ContainerException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

        # local names only in outputs
        if any(s.count('/') for s in outputs):
            raise ContainerException("Qualified names are not allowed in 'outputs'")
        
        # enable
        if enable:
            source.set_enabled(False)
        
        self.sources[label] = {
            'block': source,
            'outputs': outputs,
            'enable': enable
        }

        # order
        if order is None:
            self.sources_order.append(label)
        else:
            self.sources_order.insert(order, label)

        # reference parent
        source.set_parent(self)
        
        # make sure output signals exist
        for s in outputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added.".format(s),
                              ContainerWarning)
                self.add_signal(s)

    def remove_source(self, label):
        """
        Remove source from Container.

        :param str label: the source label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.remove_source(label)

        # local label
        self.sources_order.remove(label)
        self.sources.pop(label)

    def set_source(self, label, **kwargs):
        """
        Set source attributes. Call method :py:meth:`pyctrl.block.Block.set`.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the source label
        :param list outputs: set source output signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.set_source(label, **kwargs)

        # local label
        if label not in self.sources:
            raise ContainerException("Source '{}' does not exist".format(label))

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.sources[label]['outputs'] = values

        if 'enable' in kwargs:
            enable = kwargs.pop('enable')
            assert isinstance(enable, bool)
            self.sources[label]['enable'] = enable 
            
        self.sources[label]['block'].set(**kwargs)

    def get_source(self, label, *keys):
        """
        Get attributes from source. Call method :py:meth:`pyctrl.block.Block.get`.

        :param str label: the source label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes or single value
        :rtype: dict or value
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.get_source(label, *keys)

        # local label
        if label not in self.sources:
            raise ContainerException("Source '{}' does not exist".format(label))

        return self.sources[label]['block'].get(*keys)

    def read_source(self, label):
        """
        Read from source. Call method :py:meth:`pyctrl.block.Block.read`.
        
        :param str label: the source label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.read_source(label)

        # local label
        return self.sources[label]['block'].read()

    # def write_source(self, label, *values):
    #     """
    #     Write to source. Call method :py:meth:`pyctrl.block.Block.write`.
        
    #     :param str label: the source label
    #     :param vargs values: the values to write to source
    #     """
    #     # resolve label
    #     (container, label) = self.resolve_label(label)
    #     if container is not self:
    #         return container.write_source(label, *values)

    #     # local label
    #     self.sources[label]['block'].write(*values)

    def list_sources(self):
        """
        List of the sources currently on Container.

        :return: a list of source labels
        :rtype: list
        """
        return list(self.sources.keys())

    # sinks
    def add_sink(self, label, sink, inputs, **kwargs):
        """
        Add sink to Container.

        :param str label: the sink label
        :param pyctrl.block sink: the sink block
        :param list inputs: a list of input signals
        :param int order: if positive, set execution order, otherwise add as last (default `-1`)
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.add_sink(label, sink,
                                      inputs, **kwargs)

        # local label
        if label in self.sinks:
            warnings.warn("Sink '{}' already exists and is been replaced.".format(label), 
                          ContainerWarning)
            self.remove_sink(label)

        # object or tuple?
        if isinstance(sink, tuple):

            # dkwargs
            dkwargs = kwargs.pop('kwargs', {})

            # create device
            device_module, device_class = sink
            sink = getattr(importlib.import_module(device_module), 
                              device_class)(**dkwargs)
            
        assert isinstance(sink, block.Block)
        assert isinstance(sink, block.Sink)
        assert isinstance(inputs, (list, tuple))

        # order
        order = kwargs.pop('order', None)
        
        # enable
        enable = kwargs.pop('enable', None)
        if enable is None:
            if isinstance(sink, Container):
                enable = True
            else:
                enable = False
                
        # left over arguments?
        if len(kwargs) > 0:
            raise ContainerException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))
        
        # local names only in inputs
        if any(s.count('/') for s in inputs):
            raise ContainerException("Qualified names are not allowed in 'inputs'")
        
        # enable
        if enable:
            sink.set_enabled(False)
        
        self.sinks[label] = {
            'block': sink,
            'inputs': inputs,
            'enable': enable
        }

        # order
        if order is None:
            self.sinks_order.append(label)
        else:
            self.sinks_order.insert(order, label)

        # reference parent
        sink.set_parent(self)
        
        # make sure input signals exist
        for s in inputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added.".format(s),
                              ContainerWarning)
                self.add_signal(s)
                
    def remove_sink(self, label):
        """
        Remove sink from Container.

        :param str label: the sink label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.remove_sink(label)

        # local label
        self.sinks_order.remove(label)
        self.sinks.pop(label)

    def set_sink(self, label, **kwargs):
        """
        Set sink attributes. Call method :py:meth:`pyctrl.block.Block.set`.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the sink label
        :param list inputs: set sink input signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.set_sink(label, **kwargs)

        # local label
        if label not in self.sinks:
            raise ContainerException("Sink '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.sinks[label]['inputs'] = values
            
        if 'enable' in kwargs:
            enable = kwargs.pop('enable')
            assert isinstance(enable, bool)
            self.sinks[label]['enable'] = enable 
                
        self.sinks[label]['block'].set(**kwargs)

    def get_sink(self, label, *keys):
        """
        Get attributes from sink. Call method :py:meth:`pyctrl.block.Block.get`.

        :param str label: the sink label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes
        :rtype: dict
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.get_sink(label, *keys)

        # local label
        if label not in self.sinks:
            raise ContainerException("Sink '{}' does not exist".format(label))

        return self.sinks[label]['block'].get(*keys)

    def find_sink(self, value):
        """
        Return label if object value is a sink. Otherwise return None.

        :return: the sink label
        :rtype: str
        """
        for k,v in self.sinks.items():
            if v['block'] is value:
                return k

    def find_filter(self, value):
        """
        Return label if object value is a filter. Otherwise return None.

        :return: the filter label
        :rtype: str
        """
        for k,v in self.filters.items():
            if v['block'] is value:
                return k
            
    def find_source(self, value):
        """
        Return label if object value is a source. Otherwise return None.

        :return: the source label
        :rtype: str
        """
        for k,v in self.sources.items():
            if v['block'] is value:
                return k
            
    def find_timer(self, value):
        """
        Return label if object value is a timer. Otherwise return None.

        :return: the timer label
        :rtype: str
        """
        for k,v in self.timers.items():
            if v['block'] is value:
                return k
            
    # def read_sink(self, label):
    #     """
    #     Read from sink. Call method :py:meth:`pyctrl.block.Block.read`.
        
    #     :param str label: the sink label
    #     """
    #     # resolve label
    #     (container, label) = self.resolve_label(label)
    #     if container is not self:
    #         return container.read_sink(label)

    #     # local label
    #     return self.sinks[label]['block'].read()

    def write_sink(self, label, *values):
        """
        Write to sink. Call method :py:meth:`pyctrl.block.Block.write`.
        
        :param str label: the sink label
        :param vargs values: the values to write to sink
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.write_sink(label, *values)

        # local label
        self.sinks[label]['block'].write(*values)

    def list_sinks(self):
        """
        List of the sinks currently on Container.

        :return: a list of sink labels
        :rtype: list
        """
        return list(self.sinks.keys())

    # filters
    def add_filter(self, label, filter_, inputs, outputs, **kwargs):
        """
        Add filter to Container.

        :param str label: the filter label
        :param pyctrl.block filter: the filter block
        :param list inputs: a list of input signals
        :param list outputs: a list of output signals
        :param int order: if positive, set execution order, otherwise add as last (default `-1`)
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.add_filter(label, filter_,
                                        inputs, outputs,
                                        **kwargs)

        # local label
        if label in self.filters:
            warnings.warn("Filter '{}' already exists and is been replaced.".format(label),
                          ContainerWarning)
            self.remove_filter(label)

        # object or tuple?
        if isinstance(filter_, tuple):

            # dkwargs
            dkwargs = kwargs.pop('kwargs', {})

            # create device
            device_module, device_class = filter_
            filter_ = getattr(importlib.import_module(device_module), 
                              device_class)(**dkwargs)
            
        assert isinstance(filter_, block.Block)
        assert isinstance(filter_, block.Filter)
        assert isinstance(inputs, (list, tuple))
        assert isinstance(outputs, (list, tuple))

        # order
        order = kwargs.pop('order', None)
        
        # enable
        enable = kwargs.pop('enable', None)
        if enable is None:
            if isinstance(filter_, Container):
                enable = True
            else:
                enable = False

        # left over arguments?
        if len(kwargs) > 0:
            raise ContainerException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))
        
        # local names only in inputs
        if any(s.count('/') for s in inputs):
            raise ContainerException("Qualified names are not allowed in 'inputs'")
        
        # local names only in outputs
        if any(s.count('/') for s in outputs):
            raise ContainerException("Qualified names are not allowed in 'outputs'")
        
        # enable
        if enable:
            filter_.set_enabled(False)

        self.filters[label] = { 
            'block': filter_,  
            'inputs': inputs,
            'outputs': outputs,
            'enable': enable
        }

        # order
        if order is None:
            self.filters_order.append(label)
        else:
            self.filters_order.insert(order, label)

        # reference parent
        filter_.set_parent(self)
            
        # make sure input signals exist
        for s in inputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added.".format(s),
                              ContainerWarning)
                self.add_signal(s)
                
        # make sure output signals exist
        for s in outputs:
            if s not in self.signals:
                warnings.warn("Signal '{}' was not present and is being automatically added".format(s),
                              ContainerWarning)
                self.add_signal(s)
            
    def remove_filter(self, label):
        """
        Remove filter from Container.

        :param str label: the filter label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.remove_filter(label)

        # local label
        self.filters_order.remove(label)
        self.filters.pop(label)

    def set_filter(self, label, **kwargs):
        """
        Set filter attributes. Call method :py:meth:`pyctrl.block.Block.set`.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the filter label
        :param list inputs: set filter input signals
        :param list outputs: set filter output signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.set_filter(label, **kwargs)

        # local label
        if label not in self.filters:
            raise ContainerException("Filter '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.filters[label]['inputs'] = values

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.filters[label]['outputs'] = values

        if 'enable' in kwargs:
            enable = kwargs.pop('enable')
            assert isinstance(enable, bool)
            self.filters[label]['enable'] = enable 
                
        self.filters[label]['block'].set(**kwargs)
            
    def get_filter(self, label, *keys):
        """
        Get attributes from filter. Call method :py:meth:`pyctrl.block.Block.get`.

        :param str label: the filter label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes
        :rtype: dict
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.get_filter(label, *keys)

        # local label
        if label not in self.filters:
            raise ContainerException("Filter '{}' does not exist".format(label))

        return self.filters[label]['block'].get(*keys)

    def read_filter(self, label):
        """
        Read from filter. Call method method :py:meth:`pyctrl.block.Block.read`.
        
        :param str label: the filter label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.read_filter(label)

        # local label
        return self.filters[label]['block'].read()

    def write_filter(self, label, *values):
        """
        Write to filter. Call method method :py:meth:`pyctrl.block.Block.write`.
        
        :param str label: the filter label
        :param vargs values: the values to write to filter
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.write_filter(label, *values)

        # local label
        self.filters[label]['block'].write(*values)

    def list_filters(self):
        """
        List of the filters currently on Container.

        :return: a list of filter labels
        :rtype: list
        """
        return list(self.filters.keys())

    # devices
    def add_device(self, 
                   label, device_module, device_class, 
                   **kwargs):
        """
        Add device to Container.

        :param str label: the device label
        :param str device_module: the device module
        :param str device_class: the device class
        :param bool enable: if the device needs to be enable and disabled when calling `set_enable` (default False)
        :param list inputs: a list of input signals (default `[]`)
        :param list outputs: a list of output signals (default `[]`)
        :param bool verbose: if verbose issue warning (default `False`)
        :param BlockType type: the device type; only required if BlockType.timer (default None)
        :param kwargs kwargs: other keyword arguments to be passed to the device class initialization
        """

        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.add_device(label,
                                        device_module,
                                        device_class, 
                                        **kwargs)

        # local label
        
        # parameters
        inputs = kwargs.pop('inputs', [])
        outputs = kwargs.pop('outputs', [])

        verbose = kwargs.pop('verbose', True)

        dkwargs = kwargs.pop('kwargs', {})

        # is it a timer?
        match = re.match('timer/(\w+)', label)
        if match:
            label = match.group(1)
            is_timer = True
        else:
            is_timer = False

        if is_timer:

            # look for period and repeat
            period = kwargs.pop('period')
            repeat = kwargs.pop('repeat', False)
            
        # Install device
        if verbose:
            warnings.warn("> Installing device '{}'".format(label))

        try:

            # create device
            obj_class = getattr(importlib.import_module(device_module), 
                                device_class)
            instance = obj_class(**dkwargs)

        except Exception as e:

            warnings.warn("> Exception raised:\n  {}".format(e))
            warnings.warn("> Failed to install device '{}'".format(label))
            return None

        # add device to controller
        if is_timer:

            # add device as timer
            self.add_timer(label, instance, inputs, outputs,
                           period, repeat, **kwargs)

        else:

            # get devtype
            devtype = instance.get_type()

            # add device as source
            if devtype is BlockType.source:

                # warn if inputs are defined
                if inputs:
                    warnings.warn("Sources do not have inputs. Inputs ignored.",
                                  ContainerWarning)

                # add device as source
                self.add_source(label, instance, outputs, **kwargs)
            
            # add device as sink
            elif devtype is BlockType.sink:

                # warn if inputs are defined
                if outputs:
                    warnings.warn("Sinks do not have outputs. Outputs ignored.",
                                  ContainerWarning)

                # add device as sink
                self.add_sink(label, instance, inputs, **kwargs)

            # add device as filter
            elif devtype is BlockType.filter:

                # add device as filter
                self.add_filter(label, instance, inputs, outputs, **kwargs)

            else:
            
                raise NameError("Unknown device type '{}'. Must be sink, source, filter or timer.".format(devtype))

        # left over parameters?

        return instance

    # timers
    def add_timer(self,
                  label,
                  blk,
                  inputs,
                  outputs,
                  period,
                  repeat = True,
                  **kwargs):
        """
        Add timer to Container.

        :param str label: the timer label
        :param pyctrl.block blk: the timer block
        :param list inputs: a list of input signals
        :param list outputs: a list of output signals
        :param int period: run timer in period seconds
        :param bool repeat: repeat if True (default True)
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.add_timer(label, blk,
                                       inputs, outputs,
                                       period, repeat,
                                       **kwargs)
        
        # local label
        if label in self.timers:
            warnings.warn("Timer '{}' already exists and is been replaced.".format(label),
                          ContainerWarning)
            self.remove_timer(label)
            
            # object or tuple?
        if isinstance(blk, tuple):

            # dkwargs
            dkwargs = kwargs.pop('kwargs', {})

            # create device
            device_module, device_class = blk
            blk = getattr(importlib.import_module(device_module), 
                          device_class)(**dkwargs)
            
        assert isinstance(blk, block.Block)
        if inputs:
            assert isinstance(inputs, (list, tuple))
        if outputs:
            assert isinstance(outputs, (list, tuple))
        assert isinstance(period, (int, float))
        assert isinstance(repeat, (int, bool))
        
        # enable
        enable = kwargs.pop('enable', None)
        if enable is None:
            if isinstance(blk, Container):
                enable = True
            else:
                enable = False

        # left over arguments?
        if len(kwargs) > 0:
            raise ContainerException("Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))

        if inputs:
            # local names only in inputs
            if any(s.count('/') for s in inputs):
                raise ContainerException("Qualified names as not allowed in 'inputs'")

        if outputs:
            # local names only in outputs
            if any(s.count('/') for s in outputs):
                raise ContainerException("Qualified names as not allowed in 'outputs'")

        # enable
        if enable:
            blk.set_enabled(False)
            
        self.timers[label] = { 
            'block': blk,  
            'inputs': inputs,
            'outputs': outputs,
            'period': period,
            'repeat': repeat,
            'enable': enable
        }

        # reference parent
        blk.set_parent(self)

    def remove_timer(self, label):
        """
        Remove timer from Container.

        :param str label: the timer label
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.remove_timer(label)

        # local label
        self.timers.pop(label)
        
    def set_timer(self, label, **kwargs):
        """
        Set timer attributes. Call method :py:meth:`pyctrl.block.Block.set`.

        All attributes must be passed as key-value pairs and vary
        depending on the type of block.

        :param str label: the timer label
        :param list inputs: set timer input signals
        :param list outputs: set timer output signals
        :param kwargs kwargs: other key-value pairs of attributes
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.set_timer(label, **kwargs)

        # local label
        if label not in self.timers:
            raise ContainerException("Timer '{}' does not exist".format(label))

        if 'inputs' in kwargs:
            values = kwargs.pop('inputs')
            assert isinstance(values, (list, tuple))
            self.timers[label]['inputs'] = values

        if 'outputs' in kwargs:
            values = kwargs.pop('outputs')
            assert isinstance(values, (list, tuple))
            self.timers[label]['outputs'] = values

        if 'enable' in kwargs:
            enable = kwargs.pop('enable')
            assert isinstance(enable, bool)
            self.timers[label]['enable'] = enable
            
        self.timers[label]['block'].set(**kwargs)
        
    def get_timer(self, label, *keys):
        """
        Get attributes from timer. Call method :py:meth:`pyctrl.block.Block.get`.

        :param str label: the timer label
        :param vargs keys: the keys of the attributes to get
        :return: dictionary of attributes
        :rtype: dict
        """
        # resolve label
        (container, label) = self.resolve_label(label)
        if container is not self:
            return container.get_timer(label, *keys)

        # local label
        if label not in self.timers:
            raise ContainerException("Timer '{}' does not exist".format(label))

        return self.timers[label]['block'].get(*keys)

    # def read_timer(self, label):
    #     """
    #     Read from timer. Call method :py:meth:`pyctrl.block.Block.read`.
        
    #     :param str label: the timer label
    #     """
    #     # resolve label
    #     (container, label) = self.resolve_label(label)
    #     if container is not self:
    #         return container.read_timer(label)

    #     # local label
    #     return self.timers[label]['block'].read()

    # def write_timer(self, label, *values):
    #     """
    #     Write to timer. Call method :py:meth:`pyctrl.block.Block.write`.
        
    #     :param str label: the timer label
    #     :param vargs values: the values to write to timer
    #     """
    #     # resolve label
    #     (container, label) = self.resolve_label(label)
    #     if container is not self:
    #         return container.write_timer(label, *values)

    #     # local label
    #     self.timers[label]['block'].write(*values)

    def list_timers(self):
        """
        List of the timers currently on Container.

        :return: a list of timer labels
        :rtype: list
        """
        return list(self.timers.keys())

    # read and write methods
    
    def write(self, *values):
        """
        Write to :py:class:`pyctrl.block.container.Container`.

        :param vararg values: values
        :raise: :py:class:`pyctrl.block.container.ContainerException` if block does not support write
        """

        # Iterate on inputs
        value = iter(values)

        try:

            # Write to all sources of type Input
            for label in self.sources_order:
                block = self.sources[label]
                source = block['block']
                if isinstance(source, Input):
                    # write to Input
                    source.write(next(value))

        except StopIteration:

            raise ContainerException('Number of inputs exceeds Input sources')

        # warn if there are inputs left without an Input source
        if next(value, None) is not None:
            
            warnings.warn('Number of Input sources is smaller than the number of inputs',
                          ContainerWarning)
            
    def read(self):
        """
        Read from :py:class:`pyctrl.block.container.Container`.

        :return: values
        :retype: tuple
        :raise: :py:class:`pyctrl.block.container.ContainerException` if block does not support read
        """

        # run container
        self.run()
        
        # create empty buffer
        buffer = ()
        
        # Read from all sinks of type Output
        for label in self.sinks_order:
            block = self.sinks[label]
            sink = block['block']
            if isinstance(sink, Output):
                # read from Output
                buffer += sink.read()

        return buffer

    def run(self):

        # profiling
        t0 = 0
        first = True

        # Read all sources
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

        # return duty time
        return perf_counter() - t0
                
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

        while self.enabled:

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
            try:
                # this is to prevent a wierd 'cannot release
                # un-acquired lock' condition
                device['condition'].release()
            except RuntimeError as e:
                warnings.warn("Missed release '{}'.".format(repr(e)))
            
            # repeat
            if not device['repeat']:
                break
            
    def set_enabled(self, enabled = True):
        """
        Enable Container.
        """

        # does nothing if already enabled or disabled
        if self.enabled == enabled:
            return
            
        # call super
        super().set_enabled(enabled)

        # enable
        if self.enabled:

            # print('> container:: ENABLE')
            
            # enable sources
            for label in self.sources_order:
                if self.sources[label]['enable']:
                    self.sources[label]['block'].set_enabled(True)

            # enable filters
            for label in self.filters_order:
                if self.filters[label]['enable']:
                    self.filters[label]['block'].set_enabled(True)

            # enable sinks
            for label in self.sinks_order:
                if self.sinks[label]['enable']:
                    self.sinks[label]['block'].set_enabled(True)
                
            # start timer threads
            for label, device in self.timers.items():
                if device['enable']:
                    device['block'].set_enabled(True)
                device['condition'] = Condition()
                thread = Thread(target = self.run_timer,
                                args = (label, device))
                thread.start()

        # disable
        else:

            # print('< container:: DISABLE')
            
            # stops timer threads
            for (label,timer) in self.running_timers.items():
                
                # Try cancelling timer
                timer.cancel()
                
                # then release condition
                device = self.timers[label]
                device['condition'].acquire()
                device['condition'].notify_all()
                device['condition'].release()

            # wait for timers to terminate
            for (label,timer) in self.running_timers.items():

                # join threads
                timer.join()
                
            self.running_timers = { }

            # disable sources
            for label in self.sources_order:
                if self.sources[label]['enable']:
                    self.sources[label]['block'].set_enabled(False)
                
            # disable filters
            for label in self.filters_order:
                if self.filters[label]['enable']:
                    self.filters[label]['block'].set_enabled(False)

            # disable sinks
            for label in self.sinks_order:
                if self.sinks[label]['enable']:
                    self.sinks[label]['block'].set_enabled(False)
                
            # disable timers
            for label, device in self.timers.items():
                if device['enable']:
                    device['block'].set_enabled(False)
                
