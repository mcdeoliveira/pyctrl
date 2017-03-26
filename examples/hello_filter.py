if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

def main():

    # import python's standard time module
    import time

    # import numpy and math
    import numpy, math
    
    # import Controller and other blocks from modules
    from ctrl.timer import Controller
    from ctrl.block import Interp
    from ctrl.block.logger import Logger
    from ctrl.block.system import Constant, System, Differentiator
    from ctrl.system.tf import DTTF, LPF

    # import matplotlib
    import matplotlib.pyplot as plt
    
    # initialize controller
    Ts = 0.01
    hello = Controller(period = Ts)

    # Motor model parameters
    a = 17   # 1/s
    k = 0.11 # cycles/s duty
    c = math.exp(-a * Ts)

    # add motor signals
    hello.add_signals('voltage', 'encoder')

    # add motor filter
    hello.add_filter('motor',
                     System(model = DTTF( 
                        numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                        numpy.array((1, -(1 + c), c)))),
                    ['voltage'], ['encoder'])

    # add motor speed signal
    hello.add_signals('speed')

    # add motor speed filter
    hello.add_filter('speed',
                     Differentiator(),
                    ['clock','encoder'], ['speed'])

    # add low-pass signal
    hello.add_signals('fspeed')
    
    # add low-pass filter
    hello.add_filter('LPF',
                     System(model = LPF(fc = 10, period = Ts)),
                     ['speed'], ['fspeed'])
    
    # add logger
    hello.add_sink('logger',
                   Logger(),
                   ['clock','voltage','encoder','speed','fspeed'])

    # build interpolated input signal
    ts = [0, 1, 2,   3,   4,   5,   5, 6]
    us = [0, 0, 100, 100, -50, -50, 0, 0]
    
    # Add a step the voltage
    hello.add_filter('input',
		     Interp(signal = us, time = ts),
		     ['clock'], ['voltage'])

    # Add a timer to stop the controller
    hello.add_timer('stop',
		    Constant(value = 0),
		    None, ['is_running'],
                    period = 6, repeat = False)
    
    # print controller info
    print(hello.info('all'))
    
    try:

        # run the controller
        print('> Run the controller.')
        with hello:

            # wait for the controller to finish on its own
            hello.join()
            
        print('> Done with the controller.')

        # read logger
        data = hello.read_sink('logger')
        clock = data[:,0]
        voltage = data[:,1]
        encoder = data[:,2]
        speed = data[:,3]
        fspeed = data[:,4]

        # start plot
        plt.figure()
        
        # plot input 
        plt.subplot(3,1,1)
        plt.plot(clock, voltage, 'b')
        plt.ylabel('input (%duty)')
        plt.ylim((-120,120))
        plt.xlim(0,6)
        plt.grid()
        
        # plot velocity
        plt.subplot(3,1,2)
        plt.plot(clock, speed,'b', clock, fspeed, 'r')
        plt.ylabel('speed (Hz)')
        plt.ylim((-12,12))
        plt.xlim(0,6)
        plt.grid()

        # plot position
        plt.subplot(3,1,3)
        plt.plot(clock, encoder,'b')
        plt.ylabel('position (cycles)')
        plt.ylim((0,25))
        plt.xlim(0,6)
        plt.grid()

        # show plots
        plt.show()
        
    except KeyboardInterrupt:
        pass

    finally:
        pass

if __name__ == "__main__":
    
    main()
