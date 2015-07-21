import warnings
import socket

from . import packet
import ctrl

class WrapSocket:

    def __init__(self, socket):
        self.socket = socket

    def read(self, bufsize = 1):
        return self.socket.recv(bufsize, 0x40)

class Controller(ctrl.Controller):

    def __init__(self, host = "localhost", port = 9999):
        self.host = host
        self.port = port
        self.socket = None
        self.debug = 0

    def __enter__(self):
        if self.debug > 0:
            print('> Opening socket')
        self.open()
        super().__enter__()
        return self

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)
        if self.debug > 0:
            print('> Closing socket')
        self.close()

    def open(self):
        # Open a socket
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        else:
            warnings.warn("Socket already open")

    def close(self):
        if self.socket is None:
            warnings.warn("Socket is not open")
        else:
            self.socket.close()
            self.socket = None
            
    def send(self, command, argtype = None, argvalue = None):

        # Open socket if closed
        auto_close = False
        if self.socket is None:
            self.open()
            auto_close = True

        # Send command to server
        if self.debug > 0:
            print("> Will request command '{}'"
                  .format(command))
        self.socket.send(packet.pack('C', command))
        if argtype is not None:
            if self.debug > 0:
                print("> Will send argument '{}({})'"
                      .format(argtype, argvalue))
            self.socket.send(packet.pack(argtype, argvalue))

        values = []
        while True:

            if self.debug > 0:
                print("> Waiting for stream...")
            (type, _value) = packet.unpack_stream(WrapSocket(self.socket))
            if type == 'A':
                if self.debug > 0:
                    print("> Received Acknowledgment '{}'\n".format(_value))
                break

            # append to return values
            values.append((type, _value))

            if self.debug > 0:
                print("> Received type = '{}', value = '{}'"
                      .format(type, _value))

        # Close socket
        if auto_close:
            self.close()

        return values

    # Controller methods
    def help(self, value = ''):
        return self.send('h', 'S', value)[0][1]

    def get_log(self):
        return self.send('l')[0][1]

    def set_echo(self, value):
        self.send('E', 'I', value)

    def set_logger(self, duration):
        self.send('L', 'D', duration)

    def reset_logger(self):
        self.send('T')

    def set_encoder1(self, value):
        self.send('P', 'D', value)

    def set_reference1(self, value):
        self.send('R', 'D', value)

    def set_controller1(self, controller):
        self.send('C', 'P', controller)

    def start(self):
        self.send('s')

    def stop(self):
        self.send('t')

    def get_period(self):
        return self.send('l')[0][1]


if __name__ == "__main__":

    import time
    import numpy
    from ControlAlgorithm import ProportionalController

    HOST, PORT = "localhost", 9999
    
    with ControllerClient(HOST, PORT) as controller:

        print(controller.help())

        print(controller.help('s'))
        print(controller.help('S'))

        controller.set_echo(0)

        controller.reset_logger()

        controller.start()
        time.sleep(1)
        controller.set_reference1(100)
        time.sleep(1)
        controller.set_reference1(-50)
        time.sleep(1)
        controller.set_reference1(0)
        time.sleep(1)
        controller.stop()

        print(controller.get_log())

        controller.set_logger(2)

        controller.start()
        time.sleep(1)
        controller.set_reference1(100)
        time.sleep(1)
        controller.set_reference1(-100)
        time.sleep(1)
        controller.stop()

        print(controller.get_log())

        controller.set_controller1(ProportionalController(1, 1))
