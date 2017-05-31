#!/usr/bin/env python3
def main():

    # import python's standard math module and numpy
    import math, numpy, sys
    
    # import Controller and other blocks from modules
    from ctrl.timer import Controller
    from ctrl.block import Interp, Logger, Constant
    from ctrl.block.system import System
    from ctrl.system.tf import DTTF

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
    
    # add logger
    simotor.add_sink('logger',
                     Logger(),
                     ['clock','pwm','encoder'])
    
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
    data = simotor.read_sink('logger')
    clock = data[:,0]
    pwm = data[:,1]
    encoder = data[:,2]
    
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
    
    # show plots
    plt.show()
    
if __name__ == "__main__":
    
    main()
