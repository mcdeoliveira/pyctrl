import sys
sys.path.append('..')

import pytest
import time

HOST, PORT = "localhost", 9999
start_server = True

def test_local():

    from ctrl import Controller
    run(Controller())

def test_client_server():

    import ctrl.client

    if start_server:

        # initiate server
        print('> Starting server')

        import subprocess
        server = subprocess.Popen(["python3", "../server.py"], 
                                  stdout = subprocess.PIPE)

        time.sleep(1)

    try:
        run(ctrl.client.Controller(host = HOST, port = PORT))
    except Exception as e:
        print('** EXCEPTION RAISED **')
        raise e
    finally:
        if start_server:
            # stop server
            print('> Terminating server')
            server.terminate()

def run(controller):

    import ctrl
    import numpy
    import ctrl.block.logger as logger
    import ctrl.block as block
    import ctrl.block.linear as linear
    import ctrl.block.random as blkrnd

    # period
    assert controller.get_period() == 0.01 # default
    controller.set_period(0.1)
    assert controller.get_period() == 0.1

    # test signals
    assert 'clock' in controller.list_signals() # clock is default

    controller.add_signal('_test_')
    assert '_test_' in controller.list_signals()

    with pytest.raises(ctrl.ControllerException):
        controller.add_signal('_test_')

    assert controller.get_signal('_test_') == 0

    controller.set_signal('_test_', 1.2)
    assert controller.get_signal('_test_') == 1.2

    controller.remove_signal('_test_')
    assert '_test_' not in controller.list_signals()

    with pytest.raises(ctrl.ControllerException):
        controller.set_signal('_test_', 1.2)

    controller.add_signals('_test1_', '_test2_')
    assert '_test1_' in controller.list_signals()
    assert '_test2_' in controller.list_signals()

    controller.remove_signal('_test1_')
    controller.remove_signal('_test2_')
    assert '_test1_' not in controller.list_signals()
    assert '_test2_' not in controller.list_signals()

    # test sink

    controller.add_sink('_logger_', logger.Logger(), ['clock'])
    assert '_logger_' in controller.list_sinks()

    with pytest.raises(ctrl.ControllerException):
        controller.add_sink('_logger_', logger.Logger(), ['clock'])

    controller.set_sink('_logger_', 'reset')

    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape == (0, 0)

    with pytest.raises(ctrl.ControllerException):
        controller.set_sink('_logger_', '_reset')

    with controller:
        time.sleep(.2)

    log = controller.read_sink('_logger_')

    #print(log)
    assert isinstance(log, numpy.ndarray)
    assert log.shape[0] > 1
    assert log.shape[1] == 1

    controller.set_sink('_logger_', 'reset')
    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape == (0,1)

    controller.remove_sink('_logger_')
    assert '_logger_' not in controller.list_sinks()

    controller.add_signal('_test_')

    controller.add_sink('_logger_', logger.Logger(), ['clock', '_test_'])
    assert '_logger_' in controller.list_sinks()

    with controller:
        time.sleep(.2)

    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape[0] > 1
    assert log.shape[1] == 2

    controller.set_sink('_logger_', 'reset')
    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape == (0,2)

    controller.remove_sink('_logger_')
    assert '_logger_' not in controller.list_sinks()

    # test source

    controller.add_source('_rand_', blkrnd.RandomUniform(), ['_test_'])
    assert '_rand_' in controller.list_sources()

    with pytest.raises(ctrl.ControllerException):
        controller.add_source('_rand_', blkrnd.RandomUniform(), ['clock'])

    controller.set_source('_rand_', 'reset')

    a = controller.read_source('_rand_')
    assert isinstance(a[0], float)
    assert 0 <= a[0] <= 1

    with pytest.raises(ctrl.ControllerException):
        controller.set_source('_rand_', '_reset')

    controller.remove_source('_rand_')
    assert '_rand_' not in controller.list_sources()

    # test filter

    controller.add_signal('_output_')

    controller.add_source('_rand_', blkrnd.RandomUniform(), ['_test_'])
    assert '_rand_' in controller.list_sources()

    controller.add_filter('_gain_', linear.Gain(gain = 2), 
                          ['_test_'], 
                          ['_output_'])
    assert '_gain_' in controller.list_filters()
        
    controller.add_sink('_logger_', logger.Logger(), ['_test_', '_output_'])
    assert '_logger_' in controller.list_sinks()

    with controller:
        time.sleep(.2)

    log = controller.read_sink('_logger_')
    assert isinstance(log, numpy.ndarray)
    assert log.shape[0] > 1
    assert log.shape[1] == 2

    assert numpy.all(numpy.fabs(log[:,1] / log[:,0] - 2) < 1e-6)

if __name__ == "__main__":

    print('> Local')
    test_local()

    print('> Client-Server')
    test_client_server()

