#!/usr/bin/env python3

def main():

    # import python's standard math module and numpy
    import math, numpy, sys
    
    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block import Interp, Logger, Constant
    from pyctrl.block.system import System, Differentiator
    from pyctrl.system.tf import DTTF, LPF

    # initialize controller
    Ts = 0.01
    simotor = Controller(period = Ts)

    # build interpolated input signal
    ts = [0, 1, 2,   3,   4,   5,   5, 6]
    us = [0, 0, 100, 100, -50, -50, 0, 0]
    
    # add pwm signal
    simotor.add_signal('pwm')
    
    # add filter to interpolate data
    simotor.add_filter('input',
		       Interp(xp = us, fp = ts),
		       ['clock'],
                       ['pwm'])

    # Motor model parameters
    tau = 1/55   # time constant (s)
    g = 0.092    # gain (cycles/sec duty)
    c = math.exp(-Ts/tau)
    d = (g*Ts)*(1-c)/2

    # add motor signals
    simotor.add_signal('encoder')

    # add motor filter
    simotor.add_filter('motor',
                       System(model = DTTF( 
                           numpy.array((0, d, d)), 
                           numpy.array((1, -(1 + c), c)))),
                       ['pwm'],
                       ['encoder'])
    
    # add motor speed signal
    simotor.add_signal('speed')
    
    # add motor speed filter
    simotor.add_filter('speed',
                       Differentiator(),
                       ['clock','encoder'],
                       ['speed'])
    
    # add low-pass signal
    simotor.add_signal('fspeed')
    
    # add low-pass filter
    simotor.add_filter('LPF',
                       System(model = LPF(fc = 5, period = Ts)),
                       ['speed'],
                       ['fspeed'])
    
    # add logger
    simotor.add_sink('logger',
                     Logger(),
                     ['clock','pwm','encoder','speed','fspeed'])
    
    # Add a timer to stop the controller
    simotor.add_timer('stop',
		      Constant(value = 0),
		      None, ['is_running'],
                      period = 6, repeat = False)
    
    # print controller info
    print(simotor.info('all'))
    
    try:

        # run the controller
        print('> Run the controller.')
        with simotor:

            # wait for the controller to finish on its own
            simotor.join()
            
        print('> Done with the controller.')

    except KeyboardInterrupt:
        pass

    finally:
        pass

    # read logger
    data = simotor.get_sink('logger', 'log')
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
