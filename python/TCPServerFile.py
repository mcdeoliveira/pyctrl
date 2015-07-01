import struct
import socketserver
import numpy
import math
from Packet import Packet
from Controller import Controller

class MyTCPHandler(socketserver.StreamRequestHandler):
            
    def __init__(self, request, client_address, server):
        self.controller = Controller()

        # simulate data
        #self.controller.simulate_data(10)
        #print('current = {}'.format(self.controller.current))
        #print('data = {}'.format(self.controller.data))

        # simulate data
        #self.controller.simulate_data(10)
        #print('current = {}'.format(self.controller.current))
        #print('data = {}'.format(self.controller.data))

        self.commands = { 'e': ('S', self.controller.echo),
                          'H': ('', self.controller.help),
                          's': ('', self.controller.get_status),
                          'R': ('', self.controller.read_sensor),
                          'Z': ('', self.controller.set_encoder1),
                          'P': ('I', self.controller.set_period),
                          'E': ('I', self.controller.set_echo_divisor),
                          'L': ('', self.controller.get_log),
                          'G': ('I', self.controller.set_motor_gain),
                          'V': ('', self.controller.reverse_motor_direction),
                          'F': ('I', self.controller.set_PWM_frequency),
                          'Q': ('I', self.controller.set_motor_curve),
                          'M': ('', self.controller.start_stop_motor),
                          'T': ('I', self.controller.set_target),
                          'B': ('I', self.controller.set_target_zero),
                          'O': ('', self.controller.read_target_potentiometer),
                          'D': ('I', self.controller.set_target_mode),
                          'K': ('F', self.controller.set_proportional_gain),
                          'I': ('F', self.controller.set_integral_gain),
                          'N': ('F', self.controller.set_derivative_gain),
                          'Y': ('I', self.controller.control_mode),
                          'C': ('', self.controller.start_stop_controller),
                          'r': ('', self.controller.read_values),
                          'X': ('', self.finish),
                          'u': ('S', self.controller.array),
                          'w': ('V', self.controller.vector),
                          'W': ('M', self.controller.matrix)}
        super().__init__(request, client_address, server)
        
    def handle(self):
        
        # Read command
        while True:
            
            print('> Ready to handle')
            try:
                (type, code) = Packet.unpack_stream(self.rfile)
                print('type = {}'.format(type))
                print('code = {}'.format(code))
            except NameError as e:
                # TODO: Differentiate closed socket from error
                print('> Socket closed')
                break
            
            if type == 'C':
                (argument_type, function) = self.commands.get(code, '')
                if argument_type == '':
                    argument = tuple()
                else:
                    (type, argument) = Packet.unpack_stream(self.rfile)
                    argument = (argument,)

                print('command = {}'.format(code))
                print('argument = {}'.format(argument))

                # Call function
                message = function(*argument)

            else:
                message = ('S', 
                           "Command expected, '{}' received".format(type))

            if message is not None:
                # Send message back
                print('message = ', *message)
                self.wfile.write(Packet.pack(*message))

            message = ('A', code)
            print("> Acknowledge '{}'\n".format(code))
            self.wfile.write(Packet.pack(*message))

            if code == 'u':
                text = format(argument)
                text = [text[i] for i in range(len(text))]
                j = 0
                array = numpy.zeros(len(text))
                for i in range(0,len(text)):
                    if str.isnumeric(text[i]):
                        array[j] = text[i]
                        print('Array({}) = {}'.format(j, array[j]))
                        j += 1
                print('\n')

            if code == 'w':
                text = format(argument)
                text = [text[i] for i in range(len(text))]
                j = 0
                array = numpy.zeros(math.floor((len(text)-5)/2 + 1))
                for i in range(2,len(text)-3):
                    if i%2 == 0:
                        array[j] = text[i]
                        #print('Vector({}) = {}'.format(j, array[j]))
                        j += 1
                print(array)
                print('\n')

            if code == 'W':
                text = format(argument)
                text = [text[i] for i in range(len(text))]
                j = 0
                array = numpy.zeros(len(text))
                for i in range(0,len(text)):
                    if str.isnumeric(text[i]):
                        array[j] = text[i]
                        print('Matrix({}) = {}'.format(j, array[j]))
                        j += 1
                print('\n')

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    try:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

    finally:
        server.shutdown();
