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

    # add the signal clock
    hello.add_signal('clock')

    # add a TimerClock as a source
    hello.add_source('clock',
                     TimerClock(period = 1),
                     ['clock'])

    # add a Printer as a sink
    hello.add_sink('message',
                   Printer(message = 'Hello World!'),
                   ['clock'])

    try:
        # run the controller
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        # disable Printer and TimerClock
        hello.set_sink('message', enabled = False)
        hello.set_source('clock', enabled = False)
    
if __name__ == "__main__":
    
    main()
