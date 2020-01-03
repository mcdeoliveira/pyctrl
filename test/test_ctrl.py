import unittest
import time

HOST, PORT = "localhost", 9998
start_server = True
#start_server = False

# MODULAR TESTS, TESTS START BELOW

class BaseTest(unittest.TestCase):

    def assertShape(self, _shape, shape, dim=None):
        if not isinstance(_shape, tuple):
            _shape = _shape()
        if dim is None:
            return self.assertEqual(_shape, shape)
        elif dim == 0:
            return self.assertEqual(_shape[0], shape)
        else: # dim == 1:
            return self.assertEqual(_shape[1], shape)

    def assertShapeGreater(self, _shape, shape, dim=0):
        if not isinstance(_shape, tuple):
            _shape = _shape()
        if dim == 0:
            return self.assertTrue(_shape[0] > shape)
        else: # dim == 1:
            return self.assertTrue(_shape[1] > shape)

    def _test_basic(self, controller):

        import pyctrl
        import numpy
        import pyctrl.block as block
        import pyctrl.block.system as system
        # import pyctrl.block.random as blkrnd

        print('\n> * * * TEST BASIC {} * * *'.format(controller.__class__))

        # reset controller
        controller.reset()

        # initial signals
        _signals = controller.list_signals()
        _sinks = controller.list_sinks()
        _sources = controller.list_sources()
        _filters = controller.list_filters()

        # period
        #self.assertTrue( controller.get_period() == 0.01 # default
        #controller.set_period(0.1)
        #self.assertTrue( controller.get_period() == 0.1

        # test signals
        #self.assertTrue( 'clock' in controller.list_signals() # clock is default

        controller.add_signal('_test_')
        self.assertTrue( '_test_' in controller.list_signals() )

        #with self.assertRaises(pyctrl.ControllerException):
        controller.add_signal('_test_')

        self.assertTrue( controller.get_signal('_test_') == 0 )

        controller.set_signal('_test_', 1.2)
        self.assertTrue( controller.get_signal('_test_') == 1.2 )

        controller.remove_signal('_test_')
        self.assertTrue( '_test_' not in controller.list_signals() )

        with self.assertRaises(Exception):
            controller.set_signal('_test_', 1.2)

        controller.add_signals('_test1_', '_test2_')
        self.assertTrue( '_test1_' in controller.list_signals() )
        self.assertTrue( '_test2_' in controller.list_signals() )

        controller.remove_signal('_test1_')
        controller.remove_signal('_test2_')
        self.assertTrue( '_test1_' not in controller.list_signals() )
        self.assertTrue( '_test2_' not in controller.list_signals() )

        # test info
        self.assertTrue( isinstance(controller.info(), str) )
        self.assertTrue( isinstance(controller.info('summary'), str) )
        self.assertTrue( isinstance(controller.info('sources','sinks'), str) )

        # test sink

        controller.add_signal('clock')

        logger = block.Logger()
        controller.add_sink('_logger_', logger , ['_test_'])
        self.assertTrue( '_logger_' in controller.list_sinks() )
        self.assertTrue( '_test_' in controller.list_signals() )

        self.assertTrue( controller.get_sink('_logger_') == {'current': 0, 'auto_reset': False, 'page': 0, 'enabled': True, 'labels': ['_test_'], 'index': None} )

        self.assertTrue( controller.get_sink('_logger_', 'current', 'auto_reset') == {'current': 0, 'auto_reset': False} )

        self.assertTrue( controller.get_sink('_logger_','current') == 0 )

        controller.set_sink('_logger_',current = 1)

        self.assertTrue( controller.get_sink('_logger_','current') == 1 )

        # try to remove signal _test_
        controller.remove_signal('_test_')
        self.assertTrue( '_test_' in controller.list_signals() )

        controller.add_sink('_logger_', block.Logger(), ['clock'])
        self.assertTrue( '_logger_' in controller.list_sinks() )

        # TODO: test for changed signals

        controller.set_sink('_logger_', reset = True)

        log = controller.get_sink('_logger_', 'log')

        self.assertTrue( not hasattr(logger, 'log') )

        self.assertTrue( isinstance(log['clock'], numpy.ndarray) )
        self.assertShape( log['clock'].shape, (0, 1) )

        with self.assertRaises(block.BlockException):
            controller.set_sink('_logger_', _reset = True)

        with controller:
            time.sleep(.2)

        log = controller.get_sink('_logger_', 'log')

        self.assertTrue( isinstance(log['clock'], numpy.ndarray) )
        self.assertShape( log['clock'].shape, 1, 1 )
        self.assertShapeGreater( log['clock'].shape, 1, 0 )

        controller.set_sink('_logger_', reset = True)

        log = controller.get_sink('_logger_', 'log')

        self.assertTrue( isinstance(log['clock'], numpy.ndarray) )
        self.assertShape( log['clock'].shape, (0, 1) )

        controller.remove_sink('_logger_')
        self.assertTrue( '_logger_' not in controller.list_sinks() )

        controller.add_signal('_test_')

        controller.add_sink('_logger_', block.Logger(), ['clock', '_test_'])
        self.assertTrue( '_logger_' in controller.list_sinks() )

        with controller:
            time.sleep(.2)

        log = controller.get_sink('_logger_', 'log')

        self.assertTrue( isinstance(log['clock'], numpy.ndarray) )
        self.assertTrue( isinstance(log['_test_'], numpy.ndarray) )
        self.assertShape( log['clock'].shape, 1, 1 )
        self.assertShapeGreater( log['clock'].shape, 1, 0 )
        self.assertShape( log['_test_'].shape, 1, 1 )
        self.assertShapeGreater( log['_test_'].shape, 1, 0 )

        controller.set_sink('_logger_', reset = True)

        log = controller.get_sink('_logger_', 'log')

        self.assertTrue( isinstance(log['clock'], numpy.ndarray) )
        self.assertTrue( isinstance(log['_test_'], numpy.ndarray) )
        self.assertShape( log['clock'].shape, (0, 1) )
        self.assertShape( log['_test_'].shape, (0, 1) )

        controller.remove_sink('_logger_')
        self.assertTrue( '_logger_' not in controller.list_sinks() )

        # test source

        #controller.add_source('_rand_', blkrnd.Uniform(), ['clock'])
        controller.add_source('_rand_', block.Constant(), ['clock'])
        self.assertTrue( '_rand_' in controller.list_sources() )

        #controller.add_source('_rand_', blkrnd.Uniform(), ['_test_'])
        controller.add_source('_rand_', block.Constant(value=2), ['_test_'])
        self.assertTrue( '_rand_' in controller.list_sources() )

        self.assertTrue( controller.get_source('_rand_') == {'demux': False, 'mux': False, 'value': 2, 'enabled': True } )

        self.assertTrue( controller.get_source('_rand_', 'value', 'demux') == {'value': 2, 'demux': False} )

        self.assertTrue( controller.get_source('_rand_','value') == 2 )

        controller.set_source('_rand_', value = 1)

        self.assertTrue( controller.get_source('_rand_','value') == 1 )

        # TODO: test for changed signals

        controller.set_source('_rand_', reset = True)

        a, = controller.read_source('_rand_')
        self.assertTrue( a == 1 )

        with self.assertRaises(block.BlockException):
            controller.set_source('_rand_', _reset = True)

        controller.remove_source('_rand_')
        self.assertTrue( '_rand_' not in controller.list_sources() )

        # test filter

        controller.add_signal('_output_')

        controller.add_source('_rand_', block.Constant(), ['_test_'])
        self.assertTrue( '_rand_' in controller.list_sources() )

        controller.add_filter('_gain_', block.ShortCircuit(),
                              ['_test_'],
                              ['_output_'])
        self.assertTrue( '_gain_' in controller.list_filters() )

        # TODO: test for changed block

        controller.add_filter('_gain_', system.Gain(gain = 2),
                              ['_test_'],
                              ['_output_'])
        self.assertTrue( '_gain_' in controller.list_filters() )

        self.assertTrue( controller.get_filter('_gain_') == {'demux': False, 'enabled': True, 'gain': 2, 'mux': False} )

        self.assertTrue( controller.get_filter('_gain_', 'demux', 'gain') == {'demux': False, 'gain': 2} )

        self.assertTrue( controller.get_filter('_gain_','gain') == 2 )

        with controller:
            time.sleep(.2)

        controller.add_sink('_logger_', block.Logger(), ['_test_', '_output_'])
        self.assertTrue( '_logger_' in controller.list_sinks() )

        with controller:
            time.sleep(.2)

        log = controller.get_sink('_logger_', 'log')

        self.assertTrue( isinstance(log['_test_'], numpy.ndarray) )
        self.assertTrue( isinstance(log['_output_'], numpy.ndarray) )
        self.assertShape( log['_test_'].shape, 1, 1 )
        self.assertShapeGreater( log['_test_'].shape, 1, 0 )
        self.assertShape( log['_test_'].shape, 1, 1 )
        self.assertShapeGreater( log['_test_'].shape, 1, 0 )

        self.assertTrue( numpy.array_equal(log['_output_'], log['_test_'] * 2) )

        # test reset
        signals = controller.list_signals()
        sinks = controller.list_sinks()
        sources = controller.list_sources()
        filters = controller.list_filters()

        controller.reset()

        signals = controller.list_signals()
        sinks = controller.list_sinks()
        sources = controller.list_sources()
        filters = controller.list_filters()

        self.assertTrue(signals == _signals)
        self.assertTrue(sources == _sources)
        self.assertTrue(filters == _filters)
        self.assertTrue(sinks == _sinks)

        # test is_running
        self.assertTrue( controller.get_signal('is_running') == False )

        controller.start()
        time.sleep(1)
        self.assertTrue( controller.get_signal('is_running') == True )

        controller.stop()
        time.sleep(1)
        self.assertTrue( controller.get_signal('is_running') == False )


def _test_timer(self, controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd

    print('> * * * TEST TIMER {} * * *'.format(controller.__class__))

    # test timer
    controller.reset()

    controller.add_signal('timer')
    controller.add_timer('timer',
                         block.Constant(value = 1),
                         None, ['timer'], 1, False)

    assert controller.get_signal('timer') == 0

    assert controller.get_timer('timer') == {'enabled': True, 'demux': False, 'mux': False, 'value': 1}

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


def _test_set(self, controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd
    import pyctrl.block.logic as logic

    print('> * * * TEST SET {} * * *'.format(controller.__class__))

    controller.reset()

    controller.add_signals('s1', 's2')

    controller.add_source('const',
                          block.Constant(value = 1),
                          ['s1'])

    controller.add_sink('set1',
                        logic.SetSource(label = 'const',
                                        on_rise = {'value': 0.6},
                                        on_fall = {'value': 0.4}),
                        ['s2'])

    with controller:
        time.sleep(.5)

    assert controller.get_signal('s2') == 0
    assert controller.get_source('const', 'value') == 1

    with controller:
        controller.set_signal('s2', 1)
        time.sleep(.5)

    assert controller.get_signal('s2') == 1
    assert controller.get_source('const', 'value') == 0.6

    with controller:
        controller.set_signal('s2', 0)
        time.sleep(.5)

    assert controller.get_signal('s2') == 0
    assert controller.get_source('const', 'value') == 0.4


def _test_sub_container(self, controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd
    import pyctrl.block.container as container

    print('> * * * TEST SUB CONTAINER {} * * *'.format(controller.__class__))

    controller.reset()

    # add subcontainer

    controller.add_signals('s1', 's2', 's3')

    controller.add_filter('container1',
                          container.Container(),
                          ['s1'], ['s2','s3'])


    controller.add_signals('container1/s1', 'container1/s2', 'container1/s3')

    controller.add_source('container1/input1',
                          container.Input(),
                          ['s1'])

    controller.add_filter('container1/gain1',
                          system.Gain(gain = 3),
                          ['s1'],['s2'])

    controller.add_sink('container1/output1',
                        container.Output(),
                        ['s2'])

    controller.set_signal('s2', 0)
    with controller:
        controller.set_signal('s1', 1)
        time.sleep(.2)

    assert controller.get_signal('s2') == 3

    # add subsubcontainer

    controller.add_filter('container1/container2',
                          container.Container(),
                          ['s1'], ['s3'])

    controller.add_signals('container1/container2/s1', 'container1/container2/s2')

    controller.add_sink('container1/output2',
                        container.Output(),
                        ['s3'])

    controller.add_source('container1/container2/input1',
                          container.Input(),
                          ['s1'])

    controller.add_filter('container1/container2/gain1',
                          system.Gain(gain = 5),
                          ['s1'],['s2'])

    controller.add_sink('container1/container2/output1',
                        container.Output(),
                        ['s2'])

    controller.set_signal('s2', 0)
    controller.set_signal('s3', 0)
    with controller:
        controller.set_signal('s1', 1)
        time.sleep(.2)

    assert controller.get_signal('s2') == 3
    assert controller.get_signal('s3') == 5


def _test_sub_container_timer(self, controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd
    import pyctrl.block.container as container

    print('> * * * TEST SUB CONTAINER TIMER {} * * *'.format(controller.__class__))

    controller.reset()

    controller.add_signals('s1', 's2', 's3')

    # add subcontainer

    controller.add_filter('container1',
                          container.Container(),
                          ['s1'], ['s2','s3'])

    controller.add_signals('container1/s1', 'container1/s2', 'container1/s3')

    controller.add_source('container1/input1',
                          container.Input(),
                          ['s1'])

    controller.add_filter('container1/gain1',
                          system.Gain(gain = 3),
                          ['s1'],['s2'])

    controller.add_timer('container1/constant1',
                         block.Constant(value = 5),
                         None,['s3'],
                         period = 1, repeat = False)

    controller.add_sink('container1/output1',
                        container.Output(),
                        ['s2'])

    controller.add_sink('container1/output2',
                        container.Output(),
                        ['s3'])

    with controller:
        controller.set_signal('s1', 1)
        time.sleep(.1)

    assert controller.get_signal('s2') == 3
    assert controller.get_signal('s3') == 0


    with controller:
        controller.set_signal('s1', 1)
        time.sleep(1.5)

    assert controller.get_signal('s2') == 3
    assert controller.get_signal('s3') == 5


def _test_timer_sub_container(self, controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd
    import pyctrl.block.container as container

    print('> * * * TEST TIMER SUB CONTAINER {} * * *'.format(controller.__class__))

    controller.reset()

    controller.add_signals('s1', 's2', 's3')

    # add subcontainer

    controller.add_timer('container1',
                         container.Container(),
                         ['s1'], ['s2','s3'],
                         period = 1, repeat = False)

    controller.add_signals('timer/container1/s1',
                           'timer/container1/s2',
                           'timer/container1/s3')

    controller.add_source('timer/container1/input1',
                          container.Input(),
                          ['s1'])

    controller.add_filter('timer/container1/gain1',
                          system.Gain(gain = 3),
                          ['s1'],['s2'])

    controller.add_filter('timer/container1/gain2',
                          system.Gain(gain = 5),
                          ['s1'],['s3'])

    controller.add_sink('timer/container1/output1',
                        container.Output(),
                        ['s2'])

    controller.add_sink('timer/container1/output2',
                        container.Output(),
                        ['s3'])

    assert controller.get_signal('s2') == 0
    assert controller.get_signal('s3') == 0

    with controller:
        controller.set_signal('s1', 1)
        time.sleep(.1)

    assert controller.get_signal('s2') == 0
    assert controller.get_signal('s3') == 0

    with controller:
        controller.set_signal('s1', 1)
        time.sleep(1.5)

    assert controller.get_signal('s2') == 3
    assert controller.get_signal('s3') == 5


def _test_add_device(self, controller):

    import pyctrl
    import numpy
    import pyctrl.block as block
    import pyctrl.block.system as system
    import pyctrl.block.random as blkrnd
    import pyctrl.block.container as container

    print('> * * * TEST ADD DEVICE {} * * *'.format(controller.__class__))

    controller.reset()

    controller.add_signals('s1', 's2', 's3')

    # add subcontainer

    controller.add_timer('container1',
                         ('pyctrl.block.container', 'Container'),
                         ['s1'], ['s2','s3'],
                         period = 1, repeat = False)

    controller.add_signals('timer/container1/s1',
                           'timer/container1/s2',
                           'timer/container1/s3')

    controller.add_source('timer/container1/input1',
                          ('pyctrl.block.container', 'Input'),
                          ['s1'])

    controller.add_filter('timer/container1/gain1',
                          ('pyctrl.block.system', 'Gain'),
                          ['s1'], ['s2'],
                          kwargs = {'gain': 3})

    controller.add_filter('timer/container1/gain2',
                          ('pyctrl.block.system', 'Gain'),
                          ['s1'], ['s3'],
                          kwargs = {'gain': 5})

    controller.add_sink('timer/container1/output1',
                        ('pyctrl.block.container', 'Output'),
                        ['s2'])

    controller.add_sink('timer/container1/output2',
                        ('pyctrl.block.container', 'Output'),
                        ['s3'])

    with controller:
        controller.set_signal('s1', 1)
        time.sleep(.1)

    assert controller.get_signal('s2') == 0
    assert controller.get_signal('s3') == 0

    with controller:
        controller.set_signal('s1', 1)
        time.sleep(1.5)

    assert controller.get_signal('s2') == 3
    assert controller.get_signal('s3') == 5


# TESTS START HERE

class TestUnittestAssertions(BaseTest):

    def test_clock(self):

        from pyctrl import Controller
        from pyctrl.block.clock import Clock, TimerClock

        controller = Controller()

        period = 0.01
        controller.add_signal('clock')
        clock = Clock()
        controller.add_source('clock', clock, ['clock'])
        K = 10
        k = 0
        while k < K:
            (t,) = controller.read_source('clock')
            k += 1

        self.assertTrue( clock.get('count') == 10 )

        controller.set_source('clock', reset = True)

        (t,) = controller.read_source('clock')
        self.assertTrue( t < 0.01 )

        controller.remove_source('clock')

        clock = TimerClock(period = period)
        controller.add_source('clock', clock, ['clock'])

        K = 10
        k = 0
        while k < K:
            (t,) = controller.read_source('clock')
            k += 1

        self.assertTrue( t > 0.9 * K * period )

        controller.set_source('clock', reset = True)

        (t,) = controller.read_source('clock')
        self.assertTrue( t < 0.9 * 2 * period )

        clock.set_enabled(False)

    def test_run(self):
    
        from pyctrl import Controller
        from pyctrl.block.clock import Clock, TimerClock
        from pyctrl.block import Map
    
        controller = Controller()
    
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
        self.assertTrue( tk > 1 and tk < 1.01 )
    
        # run with condition
    
        controller.set_source('clock', reset=True)
        controller.run()
        controller.stop()
    
        tk = controller.get_signal('clock')
        self.assertTrue( tk > 1 and tk < 1.01 )
    
        controller.remove_source('clock')

    def test_local(self):

        from pyctrl import Controller
        controller = Controller()

        self._test_basic(controller)
        #_test_timer(controller)
        #_test_set(controller)
        #_test_sub_container(controller)
        #_test_sub_container_timer(controller)
        #_test_timer_sub_container(controller)
        #_test_add_device(controller)

def test_local_timer():

    from pyctrl.timer import Controller
    controller = Controller()
    
    _test_basic(controller)
    _test_timer(controller)
    _test_set(controller)
    _test_sub_container(controller)
    _test_sub_container_timer(controller)
    _test_timer_sub_container(controller)
    _test_add_device(controller)
    
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
        _test_basic(client)
        _test_timer(client)
        _test_set(client)
        _test_sub_container(client)
        _test_sub_container_timer(client)
        _test_timer_sub_container(client)
        _test_add_device(client)

        self.assertTrue( client.info('class') == "<class 'pyctrl.Controller'>" )
        
        # other tests
        client.reset(module = 'pyctrl.timer', pyctrl_class = 'Controller')

        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )

        with self.assertRaises(Exception):
            client.reset(module = 'pyctrl.timer', pyctrl_class = 'wrong')

        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )

        client.reset(module = 'pyctrl.timer')

        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )
        
        client.reset()
        
        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )

        client.reset(pyctrl_class = 'Controller')

        self.assertTrue( client.info('class') == "<class 'pyctrl.Controller'>" )
        
        client.reset(pyctrl_class = 'Controller', module = 'pyctrl.timer')

        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )

        client.reset(module = 'pyctrl.timer', kwargs = {'period': 2})
        
        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )
        self.assertTrue( client.get_source('clock','period') == 2 )

        client = pyctrl.client.Controller(host = HOST, port = PORT,
                                          module = 'pyctrl.timer',
                                          kwargs = {'period': 1})

        self.assertTrue( client.info('class') == "<class 'pyctrl.timer.Controller'>" )
        self.assertTrue( client.get_source('clock','period') == 1 )
        
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
    unittest.main()
