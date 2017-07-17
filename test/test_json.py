import pytest

def test_sub_container():

    import pyctrl
    import pyctrl.block as block

    from pyctrl.block.container import Container, Input, Output, ContainerException
    from pyctrl.block.system import Gain, DTTF

    container = Container()

    container.add_signals('s1', 's2', 's3')
    
    # add subcontainer

    container1 = Container()
    container.add_filter('container1',
                         container1,
                         ['s1'], ['s2','s3'])

    container.add_signals('container1/s1', 'container1/s2')
    
    container.add_source('container1/input1',
                         Input(),
                         ['s1'])
    
    container.add_filter('container1/gain1',
                         Gain(gain = 3),
                         ['s1'],['s2'])
    
    container.add_sink('container1/output1',
                       Output(),
                       ['s2'])
    
    # add subsubcontainer

    container.add_sink('container1/output2',
                       Output(),
                       ['s3'])

    container2 = Container()
    container.add_filter('container1/container2',
                         container2,
                         ['s1'], ['s3'])
    
    container.add_signals('container1/container2/s1', 'container1/container2/s2')
    
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

    from pyctrl.flask import JSONEncoder, JSONDecoder

    json1 = JSONEncoder(sort_keys = True, indent = 4).encode(container) 

    obj = JSONDecoder().decode(json1)

    json2 = JSONEncoder(sort_keys = True, indent = 4).encode(obj) 

    assert json1 == json2

    print('json = \n{}'.format(json1))

def _test_mip_balance():

    import numpy as np
    from pyctrl import Controller
    from pyctrl.block.container import Container, Input, Output
    from pyctrl.block.system import System, Subtract, Differentiator, Sum, Gain
    from pyctrl.block.nl import ControlledCombination, Product
    from pyctrl.block import Fade, Printer
    from pyctrl.system.ss import DTSS
    from pyctrl.block.logic import CompareAbsWithHysterisis, SetFilter, State

    GRN_LED = 61
    PAUSE_BTN = 62
    
    # create mip
    mip = Controller()

    # add signals
    mip.add_signals('theta','theta_dot','encoder1','encoder2','pwm1','pwm2')
    
    # phi is the average of the encoders
    mip.add_signal('phi')
    mip.add_filter('phi',
                   Sum(gain=0.5),
                   ['encoder1','encoder2'],
                   ['phi'])

    # phi dot
    mip.add_signal('phi_dot')
    mip.add_filter('phi_dot',
                   Differentiator(),
                   ['clock','phi'],
                   ['phi_dot'])

    # phi dot and steer reference
    mip.add_signals('phi_dot_reference', 'phi_dot_reference_fade')
    mip.add_signals('steer_reference', 'steer_reference_fade')

    # add fade in filter
    mip.add_filter('fade',
                   Fade(target = [0, 0.5], period = 5),
                   ['clock','phi_dot_reference','steer_reference'],
                   ['phi_dot_reference_fade','steer_reference_fade'])
    
    # state-space matrices
    A = np.array([[0.913134, 0.0363383],[-0.0692862, 0.994003]])
    B = np.array([[0.00284353, -0.000539063], [0.00162443, -0.00128745]])
    C = np.array([[-383.009, 303.07]])
    D = np.array([[-1.22015, 0]])

    B = 2*np.pi*(100/7.4)*np.hstack((-B, B[:,1:]))
    D = 2*np.pi*(100/7.4)*np.hstack((-D, D[:,1:]))

    ssctrl = DTSS(A,B,C,D)

    # state-space controller
    mip.add_signals('pwm')
    mip.add_filter('controller',
                   System(model = ssctrl),
                   ['theta_dot','phi_dot','phi_dot_reference_fade'],
                   ['pwm'])

    # enable pwm only if about small_angle
    mip.add_signals('small_angle', 'small_angle_pwm')
    mip.add_filter('small_angle_pwm',
                   Product(),
                   ['small_angle', 'pwm'],
                   ['small_angle_pwm'])
    
    # steering biasing
    mip.add_filter('steer',
                   ControlledCombination(),
                   ['steer_reference_fade',
                    'small_angle_pwm','small_angle_pwm'],
                   ['pwm1','pwm2'])

    # set references
    mip.set_signal('phi_dot_reference',0)
    mip.set_signal('steer_reference',0.5)

    # add supervisor actions on a timer
    # actions are inside a container so that they are executed all at once
    mip.add_timer('supervisor',
                  Container(),
                  ['theta'],
                  ['small_angle','is_running'],
                  period = 0.5, repeat = True)

    mip.add_signals('timer/supervisor/theta',
                    'timer/supervisor/small_angle',
                    'timer/supervisor/is_running')
    
    mip.add_source('timer/supervisor/theta',
                   Input(),
                   ['theta'])
    
    mip.add_sink('timer/supervisor/small_angle',
                 Output(),
                 ['small_angle'])
    
    mip.add_sink('timer/supervisor/is_running',
                 Output(),
                 ['is_running'])
    
    # add small angle sensor
    mip.add_filter('timer/supervisor/is_angle_small',
                   CompareAbsWithHysterisis(threshold = 0.11,
                                            hysterisis = 0.09,
                                            offset = -0.07,
                                            state = (State.LOW,)),
                   ['theta'],
                   ['small_angle'])
    
    # reset controller and fade
    mip.add_sink('timer/supervisor/reset_controller',
                 SetFilter(label = ['/controller','/fade'],
                           on_rise = {'reset': True}),
                 ['small_angle'])
    
    # add pause button on a timer
    mip.add_source('timer/supervisor/pause_button',
                 ('pyctrl.block', 'Constant'),
                   ['is_running'],
                   kwargs = {'value': 0},
                   enable = True)
    
    from pyctrl.flask import JSONEncoder, JSONDecoder

    json1 = JSONEncoder(sort_keys = True, indent = 4).encode(mip)

    obj = JSONDecoder().decode(json1)

    json2 = JSONEncoder(sort_keys = True, indent = 4).encode(obj) 

    assert json1 == json2

    print('json = \n{}'.format(json1))
