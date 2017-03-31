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
    from ctrl.block.clock import TimerClock

    # initialize controller
    hello = Controller()

    # add the signal myclock
    hello.add_signal('myclock')

    # add a TimerClock as a source
    hello.add_source('myclock',
                     TimerClock(period = 1),
                     ['myclock'])

    # add a Printer as a sink
    hello.add_sink('message',
                   Printer(message = 'Hello World!'),
                   ['myclock'])

    try:
        # run the controller
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)
            # disable Printer
            hello.set_sink('message', enabled = False)

    except KeyboardInterrupt:
        pass

    finally:
        # disable TimerClock
        hello.set_source('myclock', enabled = False)
    
if __name__ == "__main__":
    
    main()
