import warnings
import socketserver
import platform
import getopt, sys
import importlib

import ctrl.server

def one_line_warning(message, category, filename, lineno, line=None):
    return " {}:{}: {}:{}\n".format(filename, lineno, category.__name__, message)

def brief_warning(message, category, filename, lineno, line=None):
    return "*{}\n".format(message)

def usage():
    print('Controller Server (version {})'.format(ctrl.server.version()))
    print("""usage: python server [option] ...
Options are:
-c     : skip simulated controller calibration
-C arg : controller class             (default 'Controller')
-h     : print this help message and exit
-H arg : set hostname                 (default 'localhost')
-l arg : set log size in seconds      (default 120s)
-m arg : controller module            (default 'ctrl.bbb')
-p arg : set port                     (default 9999)
-t arg : set sampling rate in second  (default 0.01s)
-v arg : set verbose level            (default 1)""")

def main():

    # Parse command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cC:fhH:l:m:p:t:v:", ["help"])

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

    # calibrate
    calibrate = 1

    # default module
    module = 'ctrl.bbb'
    ctrl_class = 'Controller'

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
        elif o == "-c":
            calibrate = 0
        elif o == "-m":
            module = a
        elif o == "-C":
            ctrl_class = a
        else:
            assert False, "Unhandled option"

    # Modify warnings
    if verbose_level > 2:
        pass # standard formating
    elif verbose_level > 1:
        # one liner
        warnings.formatwarning = one_line_warning
    else:
        # brief
        warnings.formatwarning = brief_warning

    # Create controller
    obj_class = getattr(importlib.import_module(module),
                        ctrl_class)
    controller = obj_class(period = Ts)
    controller.set_period(Ts)
    controller.reset()
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
            print('    Sampling rate : {}s'.format(controller.get_period()))
            print('    Log size      : {}s'.format(log_size))
            print('    Verbose level : {}'.format(verbose_level))
            print(controller.info('all'))
            print('> Server started...')
        server.serve_forever()

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        print('Exiting...')
        server.shutdown()

if __name__ == "__main__":
    main()
