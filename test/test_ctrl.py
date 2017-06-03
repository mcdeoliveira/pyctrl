import pytest
import time

HOST, PORT = "localhost", 9998
start_server = True
#start_server = False

def test_local():

    from pyctrl import Controller
    run(Controller())

def test_clock():

    from pyctrl import Controller
    from pyctrl.block.clock import Clock, TimerClock

    controller = Controller()
    print(controller.info('all'))

    period = 0.01
    controller.add_signal('clock')
    clock = Clock()
    controller.add_source('clock', clock, ['clock'])
    K = 10
    k = 0
    while k < K:
        (t,) = controller.read_source('clock')
        k += 1

    assert clock.get('count') == 10

    controller.set_source('clock', reset = True)

    (t,) = controller.read_source('clock')
    assert t < 0.01

    controller.remove_source('clock')

    clock = TimerClock(period = period)
    controller.add_source('clock', clock, ['clock'])

    K = 10
    k = 0
    while k < K:
        (t,) = controller.read_source('clock')
        k += 1

    assert t > 0.9 * K * period

    controller.set_source('clock', reset = True)

    (t,) = controller.read_source('clock')
    assert t < 0.9 * 2 * period

    clock.set_enabled(False)

def run(controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd

    # initial signals
    _signals = controller.list_signals()
    _sinks = controller.list_sinks()
    _sources = controller.list_sources()
    _filters = controller.list_filters()

    # period
    #assert controller.get_period() == 0.01 # default
    #controller.set_period(0.1)
    #assert controller.get_period() == 0.1

    # test signals
    #assert 'clock' in controller.list_signals() # clock is default

    controller.add_signal('_test_')
    assert '_test_' in controller.list_signals()

    #with pytest.raises(pyctrl.ControllerException):
    controller.add_signal('_test_')

    assert controller.get_signal('_test_') == 0

    controller.set_signal('_test_', 1.2)
    assert controller.get_signal('_test_') == 1.2

    controller.remove_signal('_test_')
    assert '_test_' not in controller.list_signals()

    with pytest.raises(pyctrl.ControllerException):
        controller.set_signal('_test_', 1.2)

    controller.add_signals('_test1_', '_test2_')
    assert '_test1_' in controller.list_signals()
    assert '_test2_' in controller.list_signals()

    controller.remove_signal('_test1_')
    controller.remove_signal('_test2_')
    assert '_test1_' not in controller.list_signals()
    assert '_test2_' not in controller.list_signals()

    # test info
    assert isinstance(controller.info(), str)
    assert isinstance(controller.info('summary'), str)
    assert isinstance(controller.info('source','sink'), str)
    
    # test sink

    controller.add_signal('clock')

    controller.add_sink('_logger_', block.Logger(), ['_test_'])
    assert '_logger_' in controller.list_sinks()
    assert '_test_' in controller.list_signals()

    assert controller.get_sink('_logger_') == {'current': 0, 'auto_reset': False, 'page': 0, 'enabled': True}

    assert controller.get_sink('_logger_', 'current', 'auto_reset') == {'current': 0, 'auto_reset': False}
    
    assert controller.get_sink('_logger_','current') == 0
    
    controller.set_sink('_logger_',current = 1)

    assert controller.get_sink('_logger_','current') == 1
    
    # try to remove signal _test_
    controller.remove_signal('_test_')
    assert '_test_' in controller.list_signals()

    controller.add_sink('_logger_', block.Logger(), ['clock'])
    assert '_logger_' in controller.list_sinks()
    
    # TODO: test for changed signals

    controller.set_sink('_logger_', reset = True)

    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape == (0, 0)

    with pytest.raises(block.BlockException):
        controller.set_sink('_logger_', _reset = True)

    with controller:
        time.sleep(.2)

    log = controller.read_sink('_logger_')

    #print(log)
    assert isinstance(log, numpy.ndarray)
    assert log.shape[0] > 1
    assert log.shape[1] == 1

    controller.set_sink('_logger_', reset = True)
    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape == (0,1)

    controller.remove_sink('_logger_')
    assert '_logger_' not in controller.list_sinks()

    controller.add_signal('_test_')

    controller.add_sink('_logger_', block.Logger(), ['clock', '_test_'])
    assert '_logger_' in controller.list_sinks()

    with controller:
        time.sleep(.2)

    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape[0] > 1
    assert log.shape[1] == 2

    controller.set_sink('_logger_', reset = True)
    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape == (0,2)

    controller.remove_sink('_logger_')
    assert '_logger_' not in controller.list_sinks()

    # test source

    controller.add_source('_rand_', blkrnd.Uniform(), ['clock'])
    assert '_rand_' in controller.list_sources()

    controller.add_source('_rand_', blkrnd.Uniform(), ['_test_'])
    assert '_rand_' in controller.list_sources()

    assert controller.get_source('_rand_') == {'demux': False, 'mux': False, 'low': 0, 'high': 1, 'enabled': True, 'seed': None, 'm': 1}

    assert controller.get_source('_rand_', 'low', 'high') == {'low': 0, 'high': 1}
    
    assert controller.get_source('_rand_','low') == 0

    controller.set_source('_rand_', low = 1)

    assert controller.get_source('_rand_','low') == 1
    
    # TODO: test for changed signals

    controller.set_source('_rand_', reset = True)

    a = controller.read_source('_rand_')
    assert isinstance(a[0], float)
    assert 0 <= a[0] <= 1

    with pytest.raises(block.BlockException):
        controller.set_source('_rand_', _reset = True)

    controller.remove_source('_rand_')
    assert '_rand_' not in controller.list_sources()

    # test filter

    controller.add_signal('_output_')

    controller.add_source('_rand_', blkrnd.Uniform(), ['_test_'])
    assert '_rand_' in controller.list_sources()

    controller.add_filter('_gain_', block.ShortCircuit(), 
                          ['_test_'], 
                          ['_output_'])
    assert '_gain_' in controller.list_filters()
    
    # TODO: test for changed block

    controller.add_filter('_gain_', system.Gain(gain = 2), 
                          ['_test_'], 
                          ['_output_'])
    assert '_gain_' in controller.list_filters()
        
    assert controller.get_filter('_gain_') == {'demux': False, 'enabled': True, 'gain': 2, 'mux': False}

    assert controller.get_filter('_gain_', 'demux', 'gain') == {'demux': False, 'gain': 2}
    
    assert controller.get_filter('_gain_','gain') == 2
    
    controller.add_sink('_logger_', block.Logger(), ['_test_', '_output_'])
    assert '_logger_' in controller.list_sinks()

    with controller:
        time.sleep(.2)

    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape[0] > 1
    assert log.shape[1] == 2

    assert numpy.all(numpy.fabs(log[:,1] / log[:,0] - 2) < 1e-6)

    # test reset
    signals = controller.list_signals()
    sinks = controller.list_sinks()
    sources = controller.list_sources()
    filters = controller.list_filters()
    print(signals, sources, filters, sinks)

    controller.reset()

    signals = controller.list_signals()
    sinks = controller.list_sinks()
    sources = controller.list_sources()
    filters = controller.list_filters()
    print(signals, sources, filters, sinks)

    assert signals == _signals
    assert sources == _sources
    assert filters == _filters
    assert sinks == _sinks

    # test is_running
    assert controller.get_signal('is_running') == False

    controller.start()
    assert controller.get_signal('is_running') == True

    controller.stop()
    assert controller.get_signal('is_running') == False

    # test timer
    controller.reset()

    print(controller.info('all'))

    controller.add_signal('timer')
    controller.add_timer('timer',
                         block.Constant(value = 1),
                         None, ['timer'], 1, False)

    print(controller.info('all'))

    assert controller.get_signal('timer') == 0

    assert controller.get_timer('timer') == {'enabled': True, 'demux': False, 'mux': False}

    assert controller.get_timer('timer', 'enabled', 'demux') == {'enabled': True, 'demux': False}
    
    assert controller.get_timer('timer','enabled') == True
    
    with controller:
        time.sleep(2)

    assert controller.get_signal('timer') == 1

    controller.set_signal('timer', 0)
    assert controller.get_signal('timer') == 0

    with controller:
        time.sleep(.5)

    assert controller.get_signal('timer') == 0

    controller.set_signal('timer', 0)
    assert controller.get_signal('timer') == 0

    controller.add_timer('stop',
                         block.Constant(value = 0),
                         None, ['is_running'], 2, False)
    
    with controller:
        controller.join()

    assert controller.get_signal('timer') == 1
   
    
def test_run():

    from pyctrl import Controller
    from pyctrl.block.clock import Clock, TimerClock
    from pyctrl.block import Map

    controller = Controller()
    print(controller.info('all'))

    clock = Clock()
    controller.add_source('clock', clock, ['clock'])

    # start/stop with condition

    controller.add_filter('condition', 
                          Map(function = lambda x: x < 1), 
                          ['clock'], ['is_running'])

    controller.set_source('clock', reset=True)
    controller.start()
    is_running = controller.get_signal('is_running')
    while is_running:
        is_running = controller.get_signal('is_running')
    controller.stop()

    tk = controller.get_signal('clock')
    assert tk > 1 and tk < 1.01

    # run with condition

    controller.set_source('clock', reset=True)
    controller.run()
    controller.stop()

    tk = controller.get_signal('clock')
    assert tk > 1 and tk < 1.01

    controller.remove_source('clock')

def test_client_server():

    import pyctrl.client

    if start_server:

        # initiate server
        print('> Starting server')

        import subprocess
        server = subprocess.Popen(["pyctrl_start_server",
                                   "-H{}".format(HOST),
                                   "-p{}".format(PORT)],
                                  stdout = subprocess.PIPE)

        time.sleep(1)

    try:

        client = pyctrl.client.Controller(host = HOST, port = PORT)

        # test client
        run(client)

        assert client.info('class') == "<class 'pyctrl.Controller'>"
        
        # other tests
        client.reset(module = 'pyctrl.timer', pyctrl_class = 'Controller')

        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"

        with pytest.raises(Exception):
            client.reset(module = 'pyctrl.timer', pyctrl_class = 'wrong')

        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"

        client.reset(module = 'pyctrl.timer')

        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"
        
        client.reset()
        
        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"

        client.reset(pyctrl_class = 'Controller')

        assert client.info('class') == "<class 'pyctrl.Controller'>"
        
        client.reset(pyctrl_class = 'Controller', module = 'pyctrl.timer')

        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"

        client.reset(module = 'pyctrl.timer', period = 2)
        
        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"
        assert client.get_source('clock','period') == 2

        client = pyctrl.client.Controller(host = HOST, port = PORT,
                                        module = 'pyctrl.timer',
                                        period = 1)

        assert client.info('class') == "<class 'pyctrl.timer.Controller'>"
        assert client.get_source('clock','period') == 1
        
    except Exception as e:
        
        print('** EXCEPTION RAISED **')
        print(e)
        raise e
    
    finally:
        if start_server:
            # stop server
            print('> Terminating server')
            server.terminate()

            
if __name__ == "__main__":

    print('> Local')
    test_local()

    print('> Client-Server')
    test_client_server()

    print('> Clock')
    test_clock()

