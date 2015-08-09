import warnings
import socket

from . import packet
import ctrl

class WrapSocket:

    def __init__(self, socket):
        self.socket = socket

    def read(self, bufsize = 1):
        buffer = b''
        while bufsize:
            temp = self.socket.recv(bufsize)
            bufsize -= len(temp)
            buffer += temp
        return buffer

class Controller(ctrl.Controller):

    def __init__(self, *vargs, **kwargs):

        # parameters
        self.host = kwargs.pop('host', 'localhost')
        self.port = kwargs.pop('port', 9999)

        self.socket = None
        self.debug = 1

        # Initialize controller
        super().__init__(*vargs, **kwargs)

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
            
    def send(self, command, *vargs):

        # Make sure vargs is in pairs
        n = len(vargs)
        assert n % 2 == 0

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

        # Send arguments to server
        for (argtype, argvalue) in (vargs[i:i+2] for i in range(0, n, 2)):
            if self.debug > 0:
                print("> Will send argument '{}({})'"
                      .format(argtype, argvalue))
            self.socket.send(packet.pack(argtype, argvalue))

        # Wait for response
        if self.debug > 0:
            print("> Waiting for stream...")
        (type, value) = packet.unpack_stream(WrapSocket(self.socket))

        if type == 'A':

            if self.debug > 0:
                print("> Received Acknowledgment '{}'\n".format(value))
            value = None

        else: # if type != 'A':

            if self.debug > 0:
                print("> Received type = '{}', value = '{}'"
                      .format(type, value))

            if self.debug > 0:
                print("> Waiting for acknowledgment...")
            (type, value_) = packet.unpack_stream(WrapSocket(self.socket))

            if type == 'A':

                if self.debug > 0:
                    print("> Received Acknowledgment '{}'\n".format(value))

            else: # if type != 'A':

                warnings.warn('Failed to receive acknowledgment')

        # Close socket
        if auto_close:
            self.close()

        return value

    # Controller methods
    def help(self, value = ''):
        return self.send('h', 'S', value)

    def info(self, options = 'summary'):
        return self.send('i', 'S', options)

    # signals
    def add_signal(self, label):
        self.send('G', 'S', label)

    def set_signal(self, label, values):
        self.send('A', 'S', label, 'P', values)

    def remove_signal(self, label):
        self.send('L', 'S', label)

    # sinks
    def add_sink(self, label, sink, signals):
        self.send('S', 'S', label, 'P', sink, 'P', signals)

    def set_sink(self, label, key, values = None):
        self.send('I', 'S', label, 'S', key, 'P', values)

    def read_sink(self, label):
        return self.send('N', 'S', label)

    def remove_sink(self, label):
        return self.send('K', 'S', label)

    # sources
    def add_source(self, label, source, signals):
        self.send('O', 'S', label, 'P', source, 'P', signals)

    def set_source(self, label, key, values = None):
        self.send('U', 'S', label, 'S', key, 'P', values)

    def remove_source(self, label):
        return self.send('R', 'S', label)

    # filters
    def add_filter(self, label, filter_, input_signals, output_signals):
        self.send('F', 'S', label, 'P', filter_, 
                  'P', input_signals, 'P', output_signals)

    def set_filter(self, label, key, values = None):
        self.send('T', 'S', label, 'S', key, 'P', values)

    def remove_filter(self, label):
        return self.send('E', 'S', label)

    def start(self):
        self.send('s')

    def stop(self):
        self.send('t')

    # def set_echo(self, value):
    #     self.send('E', 'I', value)

    # def set_logger(self, duration):
    #     self.send('L', 'D', duration)

    # def reset_logger(self):
    #     self.send('T')

    # def set_reference1(self, value):
    #     self.send('R', 'D', value)

    # def set_reference1_mode(self, value):
    #     self.send('M', 'I', value)

    # def set_encoder1(self, value):
    #     self.send('P', 'D', value)

    # def set_controller1(self, controller):
    #     self.send('C', 'P', controller)
    
    # def get_log(self):
    #     return self.send('l')[0][1]

    # def get_period(self):
    #     return self.send('p')[0][1]

    # def get_encoder1(self):
    #     return self.send('e')[0][1]


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
