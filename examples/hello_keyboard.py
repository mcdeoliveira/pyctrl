#!/usr/bin/env python3


def main():

    # import python's standard time module
    import time

    # import Controller and other blocks from modules
    from pyctrl.timer import Controller
    from pyctrl.block import Printer
    from pyctrl.block.keyboard import Keyboard

    # initialize controller
    hello = Controller(period=1)

    # add a Keyboard a source
    hello.add_source('keyboard',
                     Keyboard(),
                     ['keys'],
                     enable=False)
    
    try:
        # run the controller
        with hello:
            # do nothing
            pass

    except KeyboardInterrupt:
        pass

    finally:

        #hello.set_source('keyboard', enabled=False)
        print('Done')
    

if __name__ == "__main__":
    
    main()
