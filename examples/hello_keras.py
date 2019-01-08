def main():
    import time

    from pyctrl.timer import Controller
    from pyctrl.block.keras import Keras
    from pyctrl.block import Printer

    # initialize controller
    Ts = 1/20
    hello = Controller(period = Ts)
    
    try:

        print(hello.info('all'))
        
        # run the controller
        with hello:
            # do nothing for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        print('Done')

if __name__ == "__main__":
    
    main()