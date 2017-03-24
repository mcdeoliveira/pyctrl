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
    from ctrl.block import Interp, Logger, Constant
    from ctrl.block.system import System, Differentiator, Feedback
    from ctrl.system.tf import DTTF, LPF, PID

    # initialize controller
    Ts = 0.01
    bbb = Controller(period = Ts)

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
                   inputs = ['pwm'],
                   motor = 3)

    # add motor speed signal
    bbb.add_signal('speed')
    
    # add motor speed filter
    bbb.add_filter('speed',
                   Differentiator(),
                   ['clock','encoder'],
                   ['speed'])

    # add motor speed signal
    bbb.add_signal('speed_reference')
    
    # add pid controller
    pid = System(model = PID(Kp = 30))
    
    bbb.add_filter('input',
		   Feedback(block = pid),
		   ['encoder','speed_reference'],
                   ['pwm'])
    
    # add logger
    bbb.add_sink('logger',
                 Logger(),
                 ['clock','pwm','encoder','speed','speed_reference'])
    
    # Add a timer to stop the controller
    bbb.add_timer('stop',
		  Constant(value = 0),
		  None, ['is_running'],
                  period = 1, repeat = False)
    
    # print controller info
    print(bbb.info('all'))
    
    try:
        
        # run the controller
        print('> Run the controller.')

        # set speed_reference
        bbb.set_signal('speed_reference', 3)

        # reset clock
        bbb.set_source('clock', reset = True)
        with bbb:

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
    speed_reference = data[:,4]
    
    # import matplotlib
    import matplotlib.pyplot as plt
    
    # start plot
    plt.figure()
    
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
    plt.ylabel('position (cycles)')
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
    ax2.plot(clock, speed_reference, 'r', label='fspeed')
    ax2.set_ylabel('speed (Hz)')
    ax2.set_ylim((-6,12))
    ax2.set_xlim(0,6)
    ax2.grid()
    plt.legend(loc = 1)

    # show plots
    plt.show()
    
if __name__ == "__main__":
    
    main()
