#!/usr/bin/env python3
def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl.client import Controller
    from ctrl.block import Printer
    from ctrl.block.clock import TimerClock

    # initialize controller
    hello = Controller(host = 'localhost', port = 9999,
                       module = 'ctrl.timer',
                       period = 1)

    # add a Printer as a sink
    hello.add_sink('message',
                   Printer(message = 'Hello World @ {:3.1f}s'),
                   ['clock'])

    # print controller information
    print(hello.info('all'))

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
        hello.set_source('clock', enabled = False)
    
if __name__ == "__main__":
    
    # print message to initialize server
    print("""
Hello World!

If you have not started a ctrl_server yet open a new terminal
and start a server by typing:

    ctrl_start_server
""")
    input('and hit <ENTER>')

    # run main    
    main()
