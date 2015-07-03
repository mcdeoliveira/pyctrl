import struct
import warnings
import socket
import numpy
import math
import Packet
from Controller import Controller

class WrapSocket:

    def __init__(self, socket):
        self.socket = socket

    def read(self, bufsize = 1):
        return self.socket.recv(bufsize)

class ControllerClient(Controller):

    def __init__(self, host = "localhost", port = 9999):
        self.host = host
        self.port = port
        self.socket = None

    def __enter__(self):
        print('> Opening socket')
        self.open()
        return self

    def __exit__(self, type, value, traceback):
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
        # Send command to server
        self.socket.send(Packet.pack('C', command))
        if argtype is not None:
            self.socket.send(Packet.pack(argtype, argvalue))

        values = []
        while True:

            (type, _value) = Packet.unpack_stream(WrapSocket(self.socket))
            if type == 'A':
                break

            # append to return values
            values.append((type, _value))

            print("> Received type = '{}', value = '{}'".format(type, _value))

        print("> Received Acknowledgment '{}'\n".format(_value))

        return values

    # Controller methods
    def help(self):
        return self.send('h')[0][1]

    def set_echo(self, value):
        self.send('E', 'I', value)

    def set_sleep(self, value):
        self.send('S', 'D', value)

    def set_logger(self, duration):
        self.send('L', 'D', duration)

    def reset_logger(self):
        self.send('T')

    def set_reference1(self, value):
        self.send('R', 'D', value)

    def set_controller1(self, controller):
        self.send('C', 'P', controller)

    def start(self):
        self.send('s')

    def stop(self):
        self.send('t')

    def get_log(self):
        self.send('l')

if __name__ == "__main__":

    import time
    import numpy
    from ControlAlgorithm import ProportionalController

    HOST, PORT = "localhost", 9999
    
    with ControllerClient(HOST, PORT) as controller:

        print(controller.help())

        controller.set_echo(0)
        controller.set_sleep(.5)

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
