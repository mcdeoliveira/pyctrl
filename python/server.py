import socketserver
import platform
import warnings
import getopt, sys

import ctrl.server
import math
import numpy

def usage():
    print('Controller Server (version {})'.format(ctrl.server.version()))
    print("""usage: python server [option] ...
Options are:
-c     : skip simulated controller calibration
-f     : force simulated controller
-h     : print this help message and exit
-H arg : set hostname                 (default 'localhost')
-l arg : set log size in seconds      (default 120s)
-p arg : set port                     (default 9999)
-t arg : set sampling rate in second  (default 0.01s)
-v arg : set verbose level            (default 1)""")

def main():

    # Parse command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cfhH:l:p:t:v:", ["help"])

    except getopt.GetoptError as err:
        # print help information and exit:
        print('server: illegal option {}'.format(sys.argv[1:]))
        usage()
        sys.exit(2)

    # Sampling period and log size (s)
    Ts, log_size = 0.01, 120

    # HOST AND PORT
    HOST, PORT = "localhost", 9999

    # verbose_level
    verbose_level = 1

    # simulate, calibrate
    simulate, calibrate = 0, 1

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-H":
            HOST = a
        elif o in "-l":
            log_size = float(a)
        elif o in "-p":
            PORT = int(a)
        elif o in "-t":
            Ts = float(a)
        elif o in "-v":
            verbose_level = int(a)
        elif o == "-f":
            simulate = 1
        elif o == "-c":
            calibrate = 0
        else:
            assert False, "unhandled option"

    # Setup controller
    if 'bone' in platform.uname()[2]:

        if simulate:

            warnings.warn('Forcing simulated controller on the BBB')
            
        else:

            # We're on the beaglebone, run the real thing
            import ctrl.bbb as bbb
            controller = bbb.Controller(Ts)

    else:

        simulate = 1

    if simulate:

        # We're not on the beaglebone, simulate
        warnings.warn('Not on the BBB. Simulating controller')

        # Setup simulated controller

        import ctrl.sim as sim
        controller = sim.Controller(Ts)

        # a = 17                 # 1/s
        # k = 0.11               # cycles/s duty
        # c = math.exp(-a * Ts)  # adimensional

        # controller.set_model1( numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
        #                        numpy.array((1, -(1 + c), c)),
        #                        numpy.array((0,0)) )

        # # Calibrate
        # if calibrate:
        #     controller.calibrate()
        # else:
        #     warnings.warn('> Skipping calibration')

    # Finish setup
    #controller.set_logger(log_size)
    ctrl.server.set_controller(controller)
    ctrl.server.verbose(verbose_level)

    # Start server

    # Create the server, binding to HOST and PORT
    server = socketserver.TCPServer((HOST, PORT), 
                                    ctrl.server.Handler)

    # Initiate server
    try:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print('Controller Server (version {})'.format(ctrl.server.version()))
        if verbose_level > 0:
            print('> Options:')
            print('    Hostname[port]: {}[{}]'.format(HOST, PORT))
            print('    Sampling rate : {}s'.format(Ts))
            print('    Log size      : {}s'.format(log_size))
            print('    Verbose level : {}'.format(verbose_level))
            print('> Server started...')
        server.serve_forever()

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        print('Exiting...')
        server.shutdown()

if __name__ == "__main__":
    main()
