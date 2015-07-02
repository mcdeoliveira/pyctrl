import struct
import socketserver
import numpy
import math
from Packet import Packet
from Controller import Controller

class ControllerServer(socketserver.StreamRequestHandler):

    def version():
        return '0.0'
            
    def __init__(self, request, client_address, server, 
                 controller = Controller()):

        # initialize controller
        self.controller = controller

        # simulate data
        #self.controller.simulate_data(10)
        #print('current = {}'.format(self.controller.current))
        #print('data = {}'.format(self.controller.data))

        # simulate data
        #self.controller.simulate_data(10)
        #print('current = {}'.format(self.controller.current))
        #print('data = {}'.format(self.controller.data))

        self.commands = { 'h': ('',  'S', self.help),

                          'E': ('I', '',  self.controller.set_echo),
                          'S': ('D', '',  self.controller.set_sleep),
                          'R': ('D', '',  self.controller.set_reference1),
                          
                          's': ('',  '',  self.controller.start),
                          't': ('',  '',  self.controller.stop),

                          'l': ('',  'M',  self.controller.get_log)
        }

        super().__init__(request, client_address, server)

    def help(self):
        return """
Controller Server, version {}
Available commands:

h\t- Help

E(I)\t- Set echo 
S(F)\t- Set sleep
R(F)\t- Set reference 1

s\t- Start controller
t\t- Stop controller

l\t- Get log
""".format(ControllerServer.version())
        
    def handle(self):
        
        # Read command
        while True:
            
            print('Listening...')

            try:
                (type, code) = Packet.unpack_stream(self.rfile)
            except NameError as e:
                # TODO: Differentiate closed socket from error
                print('> Socket closed')
                break
            
            if type == 'C':
                (argument_type, output_type, function) = self.commands.get(code, '')
                
                print("> Will execute '{}({})'".format(code, argument_type))
                
                # Handle input arguments
                if argument_type == '':
                    argument = tuple()
                else:
                    (type, argument) = Packet.unpack_stream(self.rfile)
                    argument = (argument,)

                print('> Argument = {}'.format(argument))

                # Call function
                message = function(*argument)

                # Wrap outupt 
                if output_type == '':
                    message = None
                else:
                    message = (output_type, message)

                print('> message = {}'.format(message))

            else:
                message = ('S', 
                           "Command expected, '{}' received".format(type))

            if message is not None:
                # Send message back
                print('> Sending message = ', *message)
                self.wfile.write(Packet.pack(*message))

            message = ('A', code)
            print("> Acknowledge '{}'\n".format(code))
            self.wfile.write(Packet.pack(*message))


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), 
                                    ControllerServer)

    try:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print('Controller Server, version {}'.format(
            ControllerServer.version()))
        server.serve_forever()

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        print('Exiting...')
        server.shutdown();
