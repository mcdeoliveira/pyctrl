if __name__ == "__main__":

    # This is only necessary if package has not been installed
    import sys
    sys.path.append('..')

def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from ctrl.client import Controller
    from ctrl.block import Printer
    from ctrl.block.clock import TimerClock

    # print message to initialize server
    print("""Hello World!

If you have not started a ctrl_server yet open a new terminal
and start a server by typing:

    ctrl_server -m ctrl.timer -H localhost -P 9999
""")
    input('and hit <ENTER>')
    
    # initialize controller
    hello = Controller(host = 'localhost', port = 9999)
    hello.reset()
    hello.set_source('clock',period = 1)

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
            hello.set_sink('message', enabled = False)

    except KeyboardInterrupt:
        pass

    finally:
        # disable Printer and TimerClock
        hello.set_sink('message', enabled = False)
        time.sleep(1)
        hello.set_source('clock', enabled = False)
    
if __name__ == "__main__":
    
    main()
