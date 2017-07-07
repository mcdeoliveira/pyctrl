import pytest
import time

def test_container():

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.logic as logic
    import pyctrl.block.random as blkrnd

    from pyctrl import BlockType
    from pyctrl.block.container import Container
    container = Container()

    # initial signals
    _signals = container.list_signals()
    _sinks = container.list_sinks()
    _sources = container.list_sources()
    _filters = container.list_filters()

    assert not container.is_enabled()
    
    container.add_signal('_test_')
    assert '_test_' in container.list_signals()

    #with pytest.raises(pyctrl.block.container.ContainerException):
    container.add_signal('_test_')

    assert container.get_signal('_test_') == 0

    container.set_signal('_test_', 1.2)
    assert container.get_signal('_test_') == 1.2

    container.remove_signal('_test_')
    assert '_test_' not in container.list_signals()

    with pytest.raises(pyctrl.block.container.ContainerException):
        container.set_signal('_test_', 1.2)

    container.add_signals('_test1_', '_test2_')
    assert '_test1_' in container.list_signals()
    assert '_test2_' in container.list_signals()

    container.remove_signal('_test1_')
    container.remove_signal('_test2_')
    assert '_test1_' not in container.list_signals()
    assert '_test2_' not in container.list_signals()

    # test info
    assert isinstance(container.info(), str)
    assert isinstance(container.info('summary'), str)
    assert isinstance(container.info('source','sink'), str)
    
    # test sink

    container.add_signal('clock')

    container.add_sink('_logger_', block.Logger(), ['_test_'])
    assert '_logger_' in container.list_sinks()
    assert '_test_' in container.list_signals()

    assert container.get_sink('_logger_') == {'current': 0, 'auto_reset': False, 'page': 0, 'enabled': True, 'labels': ['_test_'], 'index': None}

    assert container.get_sink('_logger_', 'current', 'auto_reset') == {'current': 0, 'auto_reset': False}
    
    assert container.get_sink('_logger_','current') == 0
    
    container.set_sink('_logger_',current = 1)

    assert container.get_sink('_logger_','current') == 1
    
    # try to remove signal _test_
    container.remove_signal('_test_')
    assert '_test_' in container.list_signals()

    container.add_sink('_logger_', block.Logger(), ['clock'])
    assert '_logger_' in container.list_sinks()
    
    # TODO: test for changed signals

    container.set_sink('_logger_', reset = True)

    log = container.get_sink('_logger_', 'log')
    assert isinstance(log['clock'], numpy.ndarray)
    assert log['clock'].shape == (0,1)

    with pytest.raises(block.BlockException):
        container.set_sink('_logger_', _reset = True)

    container.set_enabled(True)
    container.run()
    container.run()
    container.set_enabled(False)
        
    log = container.get_sink('_logger_', 'log')

    #print(log)
    assert isinstance(log['clock'], numpy.ndarray)
    assert log['clock'].shape == (2,1)

    container.set_sink('_logger_', reset = True)
    log = container.get_sink('_logger_', 'log')
    assert isinstance(log['clock'], numpy.ndarray)
    assert log['clock'].shape == (0,1)

    container.remove_sink('_logger_')
    assert '_logger_' not in container.list_sinks()

    container.add_signal('_test_')

    container.add_sink('_logger_', block.Logger(), ['clock', '_test_'])
    assert '_logger_' in container.list_sinks()

    container.set_enabled(True)
    container.run()
    container.run()
    container.set_enabled(False)

    log = container.get_sink('_logger_', 'log')
    assert isinstance(log['clock'], numpy.ndarray)
    assert isinstance(log['_test_'], numpy.ndarray)
    assert log['clock'].shape == (2,1)
    assert log['_test_'].shape == (2,1)

    container.set_sink('_logger_', reset = True)
    log = container.get_sink('_logger_', 'log')
    assert isinstance(log['clock'], numpy.ndarray)
    assert isinstance(log['_test_'], numpy.ndarray)
    assert log['clock'].shape == (0,1)
    assert log['_test_'].shape == (0,1)

    container.remove_sink('_logger_')
    assert '_logger_' not in container.list_sinks()

    # test source

    container.add_source('_rand_', blkrnd.Uniform(), ['clock'])
    assert '_rand_' in container.list_sources()

    container.add_source('_rand_', blkrnd.Uniform(), ['_test_'])
    assert '_rand_' in container.list_sources()

    assert container.get_source('_rand_') == {'demux': False, 'mux': False, 'low': 0, 'high': 1, 'enabled': True, 'seed': None, 'm': 1}

    assert container.get_source('_rand_', 'low', 'high') == {'low': 0, 'high': 1}
    
    assert container.get_source('_rand_','low') == 0

    container.set_source('_rand_', low = 1)

    assert container.get_source('_rand_','low') == 1
    
    # TODO: test for changed signals

    container.set_source('_rand_', reset = True)

    a = container.read_source('_rand_')
    assert isinstance(a[0], float)
    assert 0 <= a[0] <= 1

    with pytest.raises(block.BlockException):
        container.set_source('_rand_', _reset = True)

    container.remove_source('_rand_')
    assert '_rand_' not in container.list_sources()

    # test filter

    container.add_signal('_output_')

    container.add_source('_rand_', blkrnd.Uniform(), ['_test_'])
    assert '_rand_' in container.list_sources()

    container.add_filter('_gain_', block.ShortCircuit(), 
                          ['_test_'], 
                          ['_output_'])
    assert '_gain_' in container.list_filters()
    
    # TODO: test for changed block

    container.add_filter('_gain_', system.Gain(gain = 2), 
                          ['_test_'], 
                          ['_output_'])
    assert '_gain_' in container.list_filters()
        
    assert container.get_filter('_gain_') == {'demux': False, 'enabled': True, 'gain': 2, 'mux': False}

    assert container.get_filter('_gain_', 'demux', 'gain') == {'demux': False, 'gain': 2}
    
    assert container.get_filter('_gain_','gain') == 2
    
    container.add_sink('_logger_', block.Logger(), ['_test_', '_output_'])
    assert '_logger_' in container.list_sinks()

    container.set_enabled(True)
    container.run()
    container.run()
    container.set_enabled(False)

    log = container.get_sink('_logger_', 'log')
    assert isinstance(log['_test_'], numpy.ndarray)
    assert isinstance(log['_output_'], numpy.ndarray)
    assert log['_test_'].shape == (2,1)
    assert log['_output_'].shape == (2,1)

    assert numpy.all(numpy.fabs(log['_output_'] - 2 * log['_test_']) < 1e-6)

    # test reset
    signals = container.list_signals()
    sinks = container.list_sinks()
    sources = container.list_sources()
    filters = container.list_filters()
    print(signals, sources, filters, sinks)

    print(container.info('all'))

    container.reset()

    container = Container()
    
    signals = container.list_signals()
    sinks = container.list_sinks()
    sources = container.list_sources()
    filters = container.list_filters()
    print(signals, sources, filters, sinks)

    assert signals == _signals
    assert sources == _sources
    assert filters == _filters
    assert sinks == _sinks

    print(container.info('all'))

    container.add_signal('timer')
    container.add_timer('timer',
                         block.Constant(value = 1),
                         None, ['timer'], 1, False)

    print(container.info('all'))

    assert container.get_signal('timer') == 0

    assert container.get_timer('timer') == {'enabled': True, 'demux': False, 'mux': False, 'value': 1}

    assert container.get_timer('timer', 'enabled', 'demux') == {'enabled': True, 'demux': False}
    
    assert container.get_timer('timer','enabled') == True
    
    container.set_enabled(True)
    container.run()
    time.sleep(2)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('timer') == 1

    container.set_signal('timer', 0)
    assert container.get_signal('timer') == 0

    container.set_enabled(True)
    container.run()
    time.sleep(.5)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('timer') == 0

    container.set_signal('timer', 0)
    assert container.get_signal('timer') == 0

    container.add_timer('stop',
                         block.Constant(value = 0),
                         None, ['is_running'], 2, False)
    
    #print('##########')
    container.set_enabled(True)
    container.run()
    #print('##########')

    time.sleep(3)
    
    container.run()

    container.set_enabled(False)

    assert container.get_signal('timer') == 1


    # test set
    container = Container()

    print('* * * TEST SET * * *')

    print(container.info('all'))

    container.add_signals('s1', 's2')
    
    container.add_source('const',
                          block.Constant(value = 1),
                          ['s1'])
    
    container.add_sink('set1',
                        logic.SetSource(label = 'const',
                                        on_rise = {'value': 0.6},
                                        on_fall = {'value': 0.4}),
                        ['s2'])

    container.set_enabled(True)
    container.run()
    container.set_enabled(False)

    print(container.get_source('const'))
        
    assert container.get_signal('s2') == 0
    assert container.get_source('const', 'value') == 1

    container.set_enabled(True)
    container.run()
    container.set_signal('s2', 1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 1
    assert container.get_source('const', 'value') == 0.6
    
    container.set_enabled(True)
    container.run()
    container.set_signal('s2', 0)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 0
    assert container.get_source('const', 'value') == 0.4
            
def test_container_input_output():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output
    from pyctrl.block.system import Gain
    
    container = Container()

    container.add_signal('s1')

    container.add_source('input1',
                         Input(),
                         ['s1'])
    
    container.add_sink('ouput1',
                       Output(),
                       ['s1'])

    container.set_enabled(True)
    container.write(1)
    values = container.read()
    container.set_enabled(False)

    assert values == (1,)
    
    container.add_sink('ouput2',
                       Output(),
                       ['s1'])
    
    container.set_enabled(True)
    container.write(1)
    values = container.read()
    container.set_enabled(False)

    assert values == (1,1)
    
    container.add_source('input2',
                         Input(),
                         ['s2'])
    
    container.add_sink('ouput2',
                       Output(),
                       ['s2'])

    container.set_enabled(True)
    container.write(1,2)
    values = container.read()
    container.set_enabled(False)

    assert values == (1,2)
    
    container.add_filter('gain1',
                         Gain(gain = 3),
                         ['s1'],['s1'])
    
    container.set_enabled(True)
    container.write(1,2)
    values = container.read()
    container.set_enabled(False)
    
    assert values == (3,2)
    
    container.add_sink('ouput1',
                       Output(),
                       ['s3'])
    
    container.add_filter('gain1',
                         Gain(gain = 3),
                         ['s1'],['s3'])
    
    container.set_enabled(True)
    container.write(1,2)
    values = container.read()
    container.set_enabled(False)
    
    assert values == (2,3)

def test_enable():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output
    from pyctrl.block.system import Gain

    # create subcontainer first
    
    subcontainer = Container()
    
    subcontainer.add_signals('s1', 's2')
    
    subcontainer.add_source('input1',
                            Input(),
                            ['s1'],
                            enable = True)
    
    subcontainer.add_filter('gain1',
                            Gain(gain = 3),
                            ['s1'],['s2'])
    
    subcontainer.add_sink('output1',
                          Output(),
                          ['s2'])

    print(subcontainer.info('all'))
    
    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)
    
    assert values == (3,)

    print(subcontainer.info('all'))
    
    subcontainer.set_source('input1', enable = False)
    subcontainer.set_signal('s1', 0)

    print(subcontainer.info('all'))
    
    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)
    
    assert values == (0,)

    subcontainer.set_source('input1', enable = True)
    subcontainer.set_filter('gain1', enable = True)

    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)
    
    assert values == (3,)

    subcontainer.set_filter('gain1', enable = False)
    subcontainer.set_signal('s2', 0)

    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)
    
    assert values == (0,)

    subcontainer.set_filter('gain1', enable = True)
    subcontainer.set_sink('output1', enable = True)
    subcontainer.set_signal('s2', 0)

    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)
    
    assert values == (3,)

    subcontainer.set_sink('output1', enable = False)
    subcontainer.set_signal('s2', 0)

    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)

    assert values == (None,)
    
def test_sub_container():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output, ContainerException
    from pyctrl.block.system import Gain

    # create subcontainer first
    
    subcontainer = Container()
    
    subcontainer.add_signals('s1', 's2')
    
    subcontainer.add_source('input1',
                            Input(),
                            ['s1'])
    
    subcontainer.add_filter('gain1',
                            Gain(gain = 3),
                            ['s1'],['s2'])
    
    subcontainer.add_sink('output1',
                          Output(),
                          ['s2'])
    
    subcontainer.set_enabled(True)
    subcontainer.write(1)
    values = subcontainer.read()
    subcontainer.set_enabled(False)
    
    assert values == (3,)

    # add to container
    
    container = Container()

    container.add_signals('s1', 's2')
    
    container.add_filter('container',
                         subcontainer,
                         ['s1'], ['s2'])
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3

    # signals in subcontainer
    container.set_signal('container/s1', 2)

    container.add_signal('container/s3')
    container.set_signal('container/s3', 4)

    assert container.get_signal('s1') == 1
    assert container.get_signal('container/s1') == 2
    assert container.get_signal('container/s3') == 4

    container.remove_signal('container/s3')
    with pytest.raises(KeyError):
        container.get_signal('container/s3')

    # sources in subcontainer
    assert container.get_source('container/input1', 'enabled')

    container.set_source('container/input1', enabled = False)

    assert not container.get_source('container/input1', 'enabled')

    container.add_source('container/source1', Input(), ['s1'])
    assert container.get_source('container/source1', 'enabled')

    container.remove_source('container/source1')
    with pytest.raises(ContainerException):
        container.get_source('container/source1')
    
    # sinks in subcontainer
    assert container.get_sink('container/output1', 'enabled')

    container.set_sink('container/output1', enabled = False)

    assert not container.get_sink('container/output1', 'enabled')

    container.add_sink('container/sink1', Output(), ['s1'])
    assert container.get_sink('container/sink1', 'enabled')

    container.remove_sink('container/sink1')
    with pytest.raises(ContainerException):
        container.get_sink('container/sink1')
    
    # filters in subcontainer
    assert container.get_filter('container/gain1', 'enabled')

    container.set_filter('container/gain1', enabled = False)

    assert not container.get_filter('container/gain1', 'enabled')

    container.add_filter('container/filter1', Gain(), ['s1'], ['s1'])
    assert container.get_filter('container/filter1', 'enabled')

    container.remove_filter('container/filter1')
    with pytest.raises(ContainerException):
        container.get_filter('container/filter1')
        

def test_sub_sub_container():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output, ContainerException
    from pyctrl.block.system import Gain

    # create container first
    
    container = Container()

    container.add_signals('s1', 's2', 's3')
    
    # add subcontainer

    container1 = Container()
    container.add_filter('container1',
                         container1,
                         ['s1'], ['s2','s3'])

    assert container.resolve_label('container1') == (container, 'container1')
    assert container.resolve_label('./container1') == (container, 'container1')
    assert container.resolve_label('/container1') == (container, 'container1')

    with pytest.raises(pyctrl.block.container.ContainerException):
        container.resolve_label('/container2/something')
    
    with pytest.raises(pyctrl.block.container.ContainerException):
        container.resolve_label('../something')
        
    container.add_signals('container1/s1', 'container1/s2')
    
    assert container.resolve_label('container1/s1') == (container1, 's1')
    assert container.resolve_label('./container1/s1') == (container1, 's1')
    assert container.resolve_label('/container1/s1') == (container1, 's1')

    assert container1.resolve_label('../s1') == (container, 's1')
    
    assert container1.resolve_label('s1') == (container1, 's1')
    assert container1.resolve_label('./s1') == (container1, 's1')
    assert container1.resolve_label('/container1/s1') == (container1, 's1')

    container.add_source('container1/input1',
                         Input(),
                         ['s1'])
    
    container.add_filter('container1/gain1',
                         Gain(gain = 3),
                         ['s1'],['s2'])
    
    container.add_sink('container1/output1',
                       Output(),
                       ['s2'])
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3
   
    # add subsubcontainer

    container.add_sink('container1/output2',
                       Output(),
                       ['s3'])

    container2 = Container()
    container.add_filter('container1/container2',
                         container2,
                         ['s1'], ['s3'])
    
    container.add_signals('container1/container2/s1', 'container1/container2/s2')
    
    assert container.resolve_label('container1/container2/s1') == (container2, 's1')
    assert container.resolve_label('./container1/container2/s1') == (container2, 's1')
    assert container.resolve_label('/container1/container2/s1') == (container2, 's1')
    
    assert container.resolve_label('container1/container2/s1') == (container2, 's1')
    assert container.resolve_label('./container1/container2/s1') == (container2, 's1')
    assert container.resolve_label('/container1/container2/s1') == (container2, 's1')

    assert container1.resolve_label('container2/s1') == (container2, 's1')
    assert container1.resolve_label('./container2/s1') == (container2, 's1')
    assert container1.resolve_label('/container1/container2/s1') == (container2, 's1')
    
    assert container2.resolve_label('s1') == (container2, 's1')
    assert container2.resolve_label('./s1') == (container2, 's1')
    assert container2.resolve_label('/container1/container2/s1') == (container2, 's1')

    assert container2.resolve_label('../s1') == (container1, 's1')
    assert container2.resolve_label('../../s1') == (container, 's1')
    assert container2.resolve_label('../container2/s1') == (container2, 's1')

    
    container.add_source('container1/container2/input1',
                         Input(),
                         ['s1'])
    
    container.add_filter('container1/container2/gain1',
                         Gain(gain = 5),
                         ['s1'],['s2'])
    
    container.add_sink('container1/container2/output1',
                       Output(),
                       ['s2'])
    
    print(container.info('all'))
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3
    assert container.get_signal('s3') == 5

def test_sub_container_timer():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output, ContainerException
    from pyctrl.block.system import Gain
    from pyctrl.block import Constant

    # create container first
    
    container = Container()

    container.add_signals('s1', 's2', 's3')
    
    # add subcontainer
    
    container.add_filter('container1',
                         Container(),
                         ['s1'], ['s2','s3'])
    
    container.add_signals('container1/s1', 'container1/s2', 'container1/s3')
    
    container.add_source('container1/input1',
                         Input(),
                         ['s1'])
    
    container.add_filter('container1/gain1',
                         Gain(gain = 3),
                         ['s1'],['s2'])
    
    container.add_timer('container1/constant1',
                        Constant(value = 5),
                        None,['s3'],
                        period = 1, repeat = False)
    
    container.add_sink('container1/output1',
                       Output(),
                       ['s2'])
    
    container.add_sink('container1/output2',
                       Output(),
                       ['s3'])
    
    print(container.info('all'))
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3
    assert container.get_signal('s3') == 0
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    time.sleep(1.1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3
    assert container.get_signal('s3') == 5

def test_timer_sub_container():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output, ContainerException
    from pyctrl.block.system import Gain
    from pyctrl.block import Constant

    # create container first
    
    container = Container()

    container.add_signals('s1', 's2', 's3')
    
    # add subcontainer
    
    container.add_timer('container1',
                        Container(),
                        ['s1'], ['s2','s3'],
                        period = 1, repeat = False)
    
    container.add_signals('timer/container1/s1',
                          'timer/container1/s2',
                          'timer/container1/s3')
    
    container.add_source('timer/container1/input1',
                         Input(),
                         ['s1'])
    
    container.add_filter('timer/container1/gain1',
                         Gain(gain = 3),
                         ['s1'],['s2'])
    
    container.add_filter('timer/container1/gain2',
                         Gain(gain = 5),
                         ['s1'],['s3'])
    
    container.add_sink('timer/container1/output1',
                       Output(),
                       ['s2'])
    
    container.add_sink('timer/container1/output2',
                       Output(),
                       ['s3'])
    
    print(container.info('all'))
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    container.set_enabled(False)
    
    assert container.get_signal('s2') == 0
    assert container.get_signal('s3') == 0
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    time.sleep(1.1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3
    assert container.get_signal('s3') == 5
    
def test_add_device():

    import pyctrl
    from pyctrl.block.container import Container
    
    # create container first
    
    container = Container()

    container.add_signals('s1', 's2', 's3')
    
    # add subcontainer
    
    container.add_timer('container1',
                        ('pyctrl.block.container', 'Container'),
                        inputs = ['s1'], outputs = ['s2','s3'],
                        period = 1, repeat = False)

    print(container.info('all'))

    container.add_signals('timer/container1/s1',
                          'timer/container1/s2',
                          'timer/container1/s3')
    
    container.add_source('timer/container1/input1',
                         ('pyctrl.block.container', 'Input'),
                         ['s1'])
    
    container.add_filter('timer/container1/gain1',
                         ('pyctrl.block.system', 'Gain'),
                         ['s1'], ['s2'],
                         kwargs = {'gain': 3})
    
    container.add_filter('timer/container1/gain2',
                         ('pyctrl.block.system', 'Gain'),
                         ['s1'], ['s3'],
                         kwargs = {'gain': 5})
    
    container.add_sink('timer/container1/output1',
                       ('pyctrl.block.container', 'Output'),
                       ['s2'])
    
    container.add_sink('timer/container1/output2',
                       ('pyctrl.block.container', 'Output'),
                       ['s3'])
    
    print(container.info('all'))
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    container.set_enabled(False)
    
    assert container.get_signal('s2') == 0
    assert container.get_signal('s3') == 0
    
    container.set_enabled(True)
    container.set_signal('s1', 1)
    container.run()
    time.sleep(1.1)
    container.run()
    container.set_enabled(False)

    assert container.get_signal('s2') == 3
    assert container.get_signal('s3') == 5
