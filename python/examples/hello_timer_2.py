if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl import Controller
    from ctrl.block import Printer
    from ctrl.block.system import Constant

    # initialize controller
    hello = Controller()

    # add a Printer as a timer
    hello.add_timer('message',
		    Printer(message = 'Hello World @ {:3.1f} s '),
		    ['clock'], None,
                    period = 1, repeat = True)

    # Add a timer to kill controller
    hello.add_timer('killer',
		    Constant(value = 0),
		    None, ['is_running'],
                    period = 5, repeat = False)
    
    # add a Printer as a sink
    hello.add_sink('message',
		    Printer(message = 'Current time {:5.3f} s', endln = '\r'),
		    ['clock'])
    
    # print controller info
    print(hello.info('all'))
    
    try:

        # run the controller
        print('> Will run the controller.')
        hello.start()
            
        print('> Done, controller will be killed by timer.')

    except KeyboardInterrupt:
        pass

    finally:
        pass

if __name__ == "__main__":
    
    main()
