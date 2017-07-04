#!/usr/bin/env python3

def main():

    # import python's standard math module and numpy
    import math, numpy, sys
    
    # import Controller and other blocks from modules
    from pyctrl.rc import Controller
    from pyctrl.block import Interp, Logger, Constant
    from pyctrl.block.system import System, Differentiator
    from pyctrl.system.tf import DTTF, LPF

    # initialize controller
    Ts = 0.01
    bbb = Controller(period = Ts)

    # add encoder as source
    bbb.add_source('encoder1',
                   ('pyctrl.rc.encoder', 'Encoder'),
                   ['encoder'],
                   kwargs = {'encoder': 3, 
                             'ratio': 60 * 35.557})
    
    # add motor as sink
    bbb.add_sink('motor1', 
                 ('pyctrl.rc.motor', 'Motor'),
                 ['pwm'],
                 kwargs = {'motor': 3},
                 enable = True)

    # build interpolated input signal
    ts = [0, 1, 2,   3,   4,   5,   5, 6]
    us = [0, 0, 100, 100, -50, -50, 0, 0]
    
    # add filter to interpolate data
    bbb.add_filter('input',
		   Interp(xp = us, fp = ts),
		   ['clock'],
                   ['pwm'])
    
    # add motor speed signal
    bbb.add_signal('speed')
    
    # add motor speed filter
    bbb.add_filter('speed',
                   Differentiator(),
                   ['clock','encoder'],
                   ['speed'])
    
    # add low-pass signal
    bbb.add_signal('fspeed')
    
    # add low-pass filter
    bbb.add_filter('LPF',
                   System(model = LPF(fc = 5, period = Ts)),
                   ['speed'],
                   ['fspeed'])
    
    # add logger
    bbb.add_sink('logger',
                 Logger(),
                 ['clock','pwm','encoder','speed','fspeed'])
    
    # Add a timer to stop the controller
    bbb.add_timer('stop',
		  Constant(value = 0),
		  None, ['is_running'],
                  period = 6, repeat = False)
    
    # print controller info
    print(bbb.info('all'))
    
    try:
        
        # run the controller
        print('> Run the controller.')

        # reset clock
        bbb.set_source('clock', reset = True)
        with bbb:

            # wait for the controller to finish on its own
            bbb.join()
            
        print('> Done with the controller.')
            
    except KeyboardInterrupt:
        pass

    # read logger
    data = bbb.read_sink('logger')
    clock = data[:,0]
    pwm = data[:,1]
    encoder = data[:,2]
    speed = data[:,3]
    fspeed = data[:,4]

    try:

        # import matplotlib
        import matplotlib.pyplot as plt

    except:

        print('! Could not load matplotlib, skipping plots')
        sys.exit(0)

    print('> Will plot')
        
    try:
        
        # start plot
        plt.figure()

    except:

        print('! Could not plot graphics')
        print('> Make sure you have a connection to a windows manager')
        sys.exit(0)
    
    # plot pwm 
    plt.subplot(2,1,1)
    plt.plot(clock, pwm, 'b')
    plt.ylabel('pwm (%)')
    plt.ylim((-120,120))
    plt.xlim(0,6)
    plt.grid()
    
    # plot encoder
    plt.subplot(2,1,2)
    plt.plot(clock, encoder,'b')
    plt.ylabel('encoder (cycles)')
    plt.ylim((0,25))
    plt.xlim(0,6)
    plt.grid()
    
    # start plot
    plt.figure()
    
    # plot pwm
    ax1 = plt.gca()
    
    ax1.plot(clock, pwm,'g', label='pwm')
    ax1.set_ylabel('pwm (%)')
    ax1.set_ylim((-60,120))
    ax1.grid()
    plt.legend(loc = 2)

    # plot velocity
    ax2 = plt.twinx()

    ax2.plot(clock, speed,'b', label='speed')
    ax2.plot(clock, fspeed, 'r', label='fspeed')
    ax2.set_ylabel('speed (Hz)')
    ax2.set_ylim((-6,12))
    ax2.set_xlim(0,6)
    ax2.grid()
    plt.legend(loc = 1)

    # show plots
    plt.show()
    
if __name__ == "__main__":
    
    main()
