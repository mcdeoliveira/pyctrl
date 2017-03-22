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
    from ctrl.block.logger import Logger
    from ctrl.block.system import Constant, System, Differentiator
    from ctrl.system.tf import DTTF

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

    # add velocity filter
    hello.add_filter('speed',
                     Differentiator(),
                    ['clock','encoder'], ['speed'])
    
    # add logger
    hello.add_sink('logger',
                   Logger(),
                   ['clock','voltage','encoder','speed'])
    
    # Add a step the voltage
    hello.add_timer('step',
		    Constant(value = 1),
		    None, ['voltage'],
                    period = .3, repeat = False)

    # Add a timer to stop the controller
    hello.add_timer('stop',
		    Constant(value = 0),
		    None, ['is_running'],
                    period = 1, repeat = False)
    
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
        
        # plot voltage and velocity
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        
        ax1.plot(clock, speed, clock, encoder)
        ax1.set_xlabel('time')
        ax1.set_ylabel('speed')
        ax1.grid()
        
        ax2.plot(clock, voltage)
        ax2.set_xlabel('time')
        ax2.set_ylabel('voltage')
        ax2.grid()

        plt.show()
        
    except KeyboardInterrupt:
        pass

    finally:
        pass

if __name__ == "__main__":
    
    main()
