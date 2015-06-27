import struct
import warnings
import socket
from Packet import Packet
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

        print("> Received Acknowledgment '{}'".format(_value))

        return values

    def echo(self, value = 0):
        retval = self.send('e', 'S', str(value))
        print('Return values = {}'.format(retval))

    def help(self):
        self.send('H')

    def get_status(self):
        self.send('s')

    def read_sensor(self):
        self.send('R')

    def set_encoder(self):
        self.send('Z')

    def set_period(self, value = 0):
        retval = self.send('P', 'I', value)
        print('Return values = {}'.format(retval))

    def set_echo_divisor(self, value = 0):
        retval = self.send('E', 'I', value)
        print('Return values = {}'.format(retval))

    def run_loop(self, value = 0):
        retval = self.send('L', 'I', value)
        print('Return values = {}'.format(retval))

    def set_motor_gain(self, value = 0):
        retval = self.send('G', 'I', value)
        print('Return values = {}'.format(retval))

    def reverse_motor_direction(self):
        self.send('V')

    def set_PWM_frequency(self, value = 0):
        retval = self.send('F', 'I', value)
        print('Return values = {}'.format(retval))

    def set_motor_curve(self, value = 0):
        retval = self.send('Q', 'I', value)
        print('Return values = {}'.format(retval))

    def start_stop_motor(self):
        self.send('M')

    def set_target(self, value = 0):
        retval = self.send('T', 'I', value)
        print('Return values = {}'.format(retval))

    def set_target_zero(self, value = 0):
        retval = self.send('B', 'I', value)
        print('Return values = {}'.format(retval))

    def read_target_potentiometer(self):
        self.send('O')

    def set_target_mode(self, value = 0):
        retval = self.send('D', 'I', value)
        print('Return values = {}'.format(retval))

    def set_proportional_gain(self, value = 0):
        retval = self.send('K', 'F', value)
        print('Return values = {}'.format(retval))

    def set_integral_gain(self, value = 0):
        retval = self.send('I', 'F', value)
        print('Return values = {}'.format(retval))

    def set_derivative_gain(self, value = 0):
        retval = self.send('N', 'F', value)
        print('Return values = {}'.format(retval))

    def control_mode(self, value = 0):
        retval = self.send('Y', 'I', value)
        print('Return values = {}'.format(retval))

    def start_stop_controller(self):
        self.send('C')

    def read_values(self):
        self.send('r')

    
