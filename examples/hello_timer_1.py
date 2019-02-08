#!/usr/bin/env python3


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block import Printer

    # initialize controller
    hello = Controller(period = 1)

    # add a Printer as a sink
    hello.add_sink('message',
                   Printer(message = 'Hello World @ {:3.1f} s'),
                   ['clock'],
                   enable=True)

    # print controller info
    print(hello.info('all'))
    
    try:
        # run the controller
        print('> Run the controller.')

        print('> Do nothing for 5 s with the controller on...')
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)

        print('> Do nothing for 2 s with the controller off...')
        time.sleep(2)
        
        print('> Do nothing for 5 s with the controller on...')
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)
            
        print('> Done with the controller.')

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    
    main()
