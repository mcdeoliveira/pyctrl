#!/usr/bin/env python3

def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.client import Controller
    from pyctrl.block import Printer

    # initialize controller
    hello = Controller(host = 'localhost', port = 9999,
                       module = 'pyctrl.timer',
                       kwargs = {'period': 1})

    # add a Printer as a sink
    hello.add_sink('message',
                   Printer(message = 'Hello World @ {:4.2f}s'),
                   ['clock'],
                   enable = True)

    # print controller information
    print(hello.info('all'))

    try:
        # run the controller
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    
    # print message to initialize server
    print("""
Hello World!

If you have not started a pyctrl_server yet open a new terminal
and start a server by typing:

    pyctrl_start_server
""")
    input('and hit <ENTER>')

    # run main    
    main()
