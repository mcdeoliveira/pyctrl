if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl import Controller
    from ctrl.block import Printer, Constant

    # initialize controller
    hello = Controller()

    # add a Printer as a timer
    hello.add_timer('message',
		    Printer(message = 'Hello World @ {:3.1f} s '),
		    ['clock'], None,
                    period = 1, repeat = True)

    # Add a timer to stop the controller
    hello.add_timer('stop',
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
        print('> Run the controller.')
        with hello:

            # wait for the controller to finish on its own
            hello.join()
            
        print('> Done with the controller.')

    except KeyboardInterrupt:
        pass

    finally:
        pass

if __name__ == "__main__":
    
    main()
