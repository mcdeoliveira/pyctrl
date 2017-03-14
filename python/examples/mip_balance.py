if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

import math
import time
import warnings
import numpy as np
import sys, tty, termios
import threading

def brief_warning(message, category, filename, lineno, line=None):
    return "*{}\n".format(message)

warnings.formatwarning = brief_warning

import ctrl

from ctrl.block.linear import MIMO, ShortCircuit, Subtract, Differentiator, Sum, Gain
from ctrl.block.logger import Logger
from ctrl.system.ss import DTSS

# read key stuff

ARROW_UP = "\033[A"
ARROW_DOWN = "\033[B"
ARROW_RIGHT = "\033[C"
ARROW_LEFT = "\033[D"

def read_key():

    key = sys.stdin.read(1)
    if ord(key) == 27:
        key = key + sys.stdin.read(2)
    elif ord(key) == 3:
        raise KeyboardInterrupt    

    return key

def get_arrows(mip, fd):

    phi_dot_reference = 0
    
    tty.setcbreak(fd)
    while mip.get_state() != ctrl.EXITING:
        
        print('\rforward velocity = {:3.0f} deg/s'
              .format(360*phi_dot_reference),
              end='')
        
        key = read_key()
        if key == ARROW_LEFT:
            print('LEFT')
        elif key == ARROW_RIGHT:
            print('RIGHT')
        elif key == ARROW_UP:
            phi_dot_reference = phi_dot_reference + 10/360
            mip.set_signal('phi_dot_reference', - phi_dot_reference)
        elif key == ARROW_DOWN:
            phi_dot_reference = phi_dot_reference - 10/360
            mip.set_signal('phi_dot_reference', - phi_dot_reference)
            
        
def main():

    # create mip
    from ctrl.rc.mip import Controller
    mip = Controller()

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

    # calculate theta errors
    mip.add_signal('theta_dot_reference')
    mip.add_signal('theta_dot_error')
    mip.add_filter('sub_theta',
                   Subtract(),
                   ['theta_dot','theta_dot_reference'],
                   ['theta_dot_error'])

    # calculate phi errors
    mip.add_signal('phi_dot_reference')
    mip.add_signal('phi_dot_error')
    mip.add_filter('sub_phi',
                   Subtract(),
                   ['phi_dot','phi_dot_reference'],
                   ['phi_dot_error'])

    # set references
    mip.set_signal('theta_dot_reference', 0)
    mip.set_signal('phi_dot_reference',0)

    # state-space controller
    # Ts = 0.01
    Ac = np.array([[0.913134, 0.0363383],[-0.0692862, 0.994003]])
    Bc = 2*np.pi*np.array([[0.00284353, -0.000539063], [0.00162443, -0.00128745]])
    Cc = np.array([[-383.009, 303.07]])
    Dc = 2*np.pi*np.array([[-1.22015, 0]])

    Bc = (100/7.4)*Bc
    Dc = (100/7.4)*Dc

    K = 0.8

    ssctrl = DTSS(Ac,K*Bc,Cc,K*Dc)

    mip.add_signal('voltage')
    mip.add_filter('controller',
                   MIMO(ssctrl),
                   ['theta_dot_error','phi_dot_error'],
                   ['voltage'])

    # connect controller to motors
    mip.add_filter('cl1',
                   ShortCircuit(),
                   ['voltage'],
                   ['motor1'])
    mip.add_filter('cl2',
                   ShortCircuit(),
                   ['voltage'],
                   ['motor2'])

    # print controller
    print(mip.info('all'))

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:

        print("""
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                       M I P   B A L A N C E                       *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
""")

        input('Hold your MIP upright and hit <ENTER> to start balancing')
        
        # reset everything
        mip.set_source('clock',reset=True)
        mip.set_source('encoder1',reset=True)
        mip.set_source('encoder2',reset=True)
        mip.set_filter('controller',reset=True)
        mip.set_source('inclinometer',reset=True)

        # start the controller
        mip.start()

        print("Press Ctrl-C to exit")

        # fire thread to update velocities
        thread = threading.Thread(target = get_arrows,
                                  args = (mip, fd))
        thread.daemon = True
        thread.start()
        
        # and wait until controller dies
        mip.join()
        
    except KeyboardInterrupt:

        print("> Balancing aborted")
        mip.set_state(ctrl.EXITING)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
if __name__ == "__main__":
    main()

