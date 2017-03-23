if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

def main():

    # import python's standard math module and numpy
    import math, numpy
    
    # import Controller and other blocks from modules
    import rc
    from ctrl.rc import Controller
    from ctrl.block import Printer, Interp, Logger, Constant
    from ctrl.block.system import System, Differentiator
    from ctrl.system.tf import DTTF, LPF

    # initialize controller
    Ts = 0.01
    bbb = Controller(period = Ts)

    # print controller info
    print(bbb.info('all'))
    
    # add encoder as source
    bbb.add_device('encoder1',
                   'ctrl.rc.encoder', 'Encoder',
                   type = 'source',
                   outputs = ['encoder'],
                   encoder = 3, 
                   ratio = 60 * 35.557)
    
    # add motor as sink
    bbb.add_device('motor1', 
                   'ctrl.rc.motor', 'Motor',
                   type = 'sink',
                   enable = True,
                   inputs = ['pmw'],
                   motor = 3)

    # build interpolated input signal
    ts = [0, 1, 2,   3,   4,   5,   5, 6]
    us = [0, 0, 100, 100, -50, -50, 0, 0]
    
    # add filter to interpolate data
    bbb.add_filter('input',
		   Interp(signal = us, time = ts),
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
    
    # add logger
    bbb.add_sink('printer',
                 Printer(message = 'time = {:3.1f} s, motor = {:+6.1f} %, encoder = {:+6.1f}',
                         endln = '\r'),
                 ['clock','pwm','encoder'])
    
    # print controller info
    print(bbb.info('all'))
    
    try:
        
        # run the controller
        print('> Run the controller.')
        with bbb:

            print(bbb.info('all'))
            
            # wait for the controller to finish on its own
            bbb.join()
            
        print('> Done with the controller.')
            
    except KeyboardInterrupt:
        pass

    finally:
        pass

    # read logger
    data = bbb.read_sink('logger')
    clock = data[:,0]
    pwm = data[:,1]
    encoder = data[:,2]
    speed = data[:,3]
    fspeed = data[:,4]
    
    # import matplotlib
    import matplotlib.pyplot as plt
    
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
