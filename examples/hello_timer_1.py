def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl.timer import Controller
    from ctrl.block import Printer
    from ctrl.block.clock import TimerClock

    # initialize controller
    hello = Controller(period = 1)

    # add a Printer as a sink
    hello.add_sink('message',
		   Printer(message = 'Hello World @ {:3.1f} s'),
		   ['clock'])

    # print controller info
    print(hello.info('all'))
    
    try:
        # run the controller
        print('> Run the controller.')

        print('> Do nothing for 5 s with the controller on...')
        with hello:
	    # do nothing for 5 seconds
            time.sleep(5)
            hello.set_sink('message', enabled = False)

        print('> Do nothing for 2 s with the controller off...')
        time.sleep(2)
        
        print('> Do nothing for 5 s with the controller on...')
        hello.set_sink('message', enabled = True)
        with hello:
	    # do nothing for 5 seconds
            time.sleep(5)
            hello.set_sink('message', enabled = False)
            
        print('> Done with the controller.')

    except KeyboardInterrupt:
        pass

    finally:
        pass

if __name__ == "__main__":
    
    main()
