#!/usr/bin/env python3

# Drive MIP in open-loop as a car

import math
import time
import warnings
import numpy as np
import sys, tty, termios
import threading

import pyctrl

def brief_warning(message, category, filename, lineno, line=None):
    return "*{}\n".format(message)

warnings.formatwarning = brief_warning

# read key stuff

ARROW_UP    = "\033[A"
ARROW_DOWN  = "\033[B"
ARROW_RIGHT = "\033[C"
ARROW_LEFT  = "\033[D"
DEL         = "."
END         = "/"
SPACE       = " "

def read_key():

    key = sys.stdin.read(1)
    if ord(key) == 27:
        key = key + sys.stdin.read(2)
    elif ord(key) == 3:
        raise KeyboardInterrupt    

    return key

def get_arrows(mip, fd):

    pwm = 0
    steer_reference = 0.5
    
    tty.setcbreak(fd)
    while mip.get_state() != pyctrl.EXITING:
        
        print('\rmotor = {:+5.0f} %'
              '  steering = {:+5.2f} %'
              .format(pwm,
                      100*(steer_reference-0.5)),
              end='')
        
        key = read_key()
        if key == ARROW_LEFT:
            steer_reference = max(steer_reference - 20/360, 0)
            mip.set_signal('steer_reference', steer_reference)
        elif key == ARROW_RIGHT:
            steer_reference = min(steer_reference + 20/360, 1)
            mip.set_signal('steer_reference', steer_reference)
        elif key == ARROW_UP:
            pwm = pwm + 10
            mip.set_signal('pwm', - pwm)
        elif key == ARROW_DOWN:
            pwm = pwm - 10
            mip.set_signal('pwm', - pwm)
        elif key == SPACE:
            pwm = 0
            mip.set_signal('pwm', - pwm)
            steer_reference = 0.5
            mip.set_signal('steer_reference', steer_reference)
        elif key == DEL:
            steer_reference = 0.5
            mip.set_signal('steer_reference', steer_reference)
        elif key == END:            
            pwm = 0
            mip.set_signal('pwm', - pwm)

def main():

    # import blocks and controller
    from pyctrl.rc.mip import Controller
    from pyctrl.block.container import Container, Input, Output
    from pyctrl.block.system import System, Subtract, Differentiator, Sum, Gain
    from pyctrl.block.nl import ControlledCombination, Product
    from pyctrl.block import Fade, Printer
    from pyctrl.system.ss import DTSS
    from pyctrl.block.logic import CompareAbsWithHysterisis, SetFilter, State
    from rcpy.gpio import GRN_LED, PAUSE_BTN
    from rcpy.led import red

    # export json?
    export_json = true

    # create mip
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

    # phi dot and steer reference
    mip.add_signals('pwm', 'pwm_fade')
    mip.add_signals('steer_reference', 'steer_reference_fade')

    # add fade in filter
    mip.add_filter('fade',
                   Fade(target = [0, 0.5], period = 5),
                   ['clock','pwm','steer_reference'],
                   ['pwm_fade','steer_reference_fade'])
    
    # steering biasing
    mip.add_filter('steer',
                   ControlledCombination(),
                   ['steer_reference_fade',
                    'pwm','pwm'],
                   ['pwm1','pwm2'])
    
    # print controller
    print(mip.info('all'))

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:

        print("""
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                         M I P   D R I V E                         *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
""")

        print("""
Use your keyboard to drive the mip as a car:

* UP and DOWN arrows move forward and back
* LEFT and RIGHT arrows steer
* / stops forward motion
* . stops steering
* SPACE resets forward motion and steering

""")
        

        # reset everything
        mip.set_source('clock',reset=True)
        mip.set_source('encoder1',reset=True)
        mip.set_source('encoder2',reset=True)
        mip.set_source('inclinometer',reset=True)

        # turn on red led
        red.on()
        
        # start the controller
        mip.start()

        print("Press Ctrl-C or press the <PAUSE> button to exit")

        # fire thread to update velocities
        thread = threading.Thread(target = get_arrows,
                                  args = (mip, fd))
        thread.daemon = False
        thread.start()
        
        # and wait until controller dies
        mip.join()

        # print message
        print("\nDone with driving")
        
    except KeyboardInterrupt:

        print("\nDriving aborted")

    finally:

        # turn off red led
        red.off()

        # make sure it exits
        mip.set_state(pyctrl.EXITING)

        print("Press any key to exit")
        
        thread.join()
        
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
