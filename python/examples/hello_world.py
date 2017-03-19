if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl import Controller
    from ctrl.block import Printer, ShortCircuit
    from ctrl.block.clock import TimerClock

    # initialize controller
    hello = Controller()

    # add the signal clock
    hello.add_signal('clock')
    
    # add a TimerClock as a source
    hello.add_source('clock',
		     TimerClock(period = 1),
		     ['clock'])

    # add a Printer as a sink
    hello.add_sink('message',
		   Printer(message = 'Hello World @ {:3.1f} s'),
		   ['clock'])

    # add a ShortCircuit as a filter
    hello.add_sink('message',
		   Printer(message = 'Hello World @ {:3.1f} s'),
		   ['clock'])
    
    # print controller info
    print(hello.info('all'))
    
    try:
        # run the controller
        print('> Will run the controller.')

        print('> Doing nothing for 5 s with the controller on...')
        with hello:
	    # do nothing for 5 seconds
            time.sleep(5)

        print('> Doing nothing for 1 s with the controller off...')
        time.sleep(2)
        
        print('> Doing nothing for 5 s with the controller on...')
        with hello:
	    # do nothing for 5 seconds
            time.sleep(5)
            
        print('> Done with the controller.')

    except KeyboardInterrupt:
        pass

    finally:
        # disable Printer and TimerClock
        hello.set_sink('message', enabled = False)
        hello.set_source('clock', enabled = False)

if __name__ == "__main__":
    
    main()
