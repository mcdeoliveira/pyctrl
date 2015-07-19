import socketserver

from .. import packet
import ctrl

debug = 0
controller = ctrl.Controller()
commands = {}

def version():
    return '1.0'

def help(value):
    help_str = ''

    if value:
        function = commands.get(value, ('', '', None, ''))[2]
        if not function:
            help_str += "Error: '{}' not a command\n".format(value)
        if function.__doc__:
            return function.__doc__
        else:
            return 'Help not available'

    # else:
    help_str += "\n".join([' ' + k + ': ' + v[3] 
                           for (k,v) in 
                           zip(commands.keys(), commands.values())])
    help_str = """
Controller Server, version {}
Available commands:
""".format(version()) + help_str

    return help_str
        
def set_controller(_controller = ctrl.Controller()):

    # initialize controller
    global controller, commands
    controller = _controller
        
    # TODO: Complete public controller methods
    commands = { 
        'h': ('S',  'S', help,
              'Help'),
        
        'E': ('I', '',  controller.set_echo,
              'Set echo'),
        'L': ('D', '',  controller.set_logger,
              'Set logger'),
        'T': ('',  '',  controller.reset_logger,
              'Reset logger'),
        
        'R': ('D', '',  controller.set_reference1,
              'Set reference'),
        'C': ('P', '',  controller.set_controller1,
              'Set controller'),
        
        's': ('',  '',  controller.start,
              'Start control loop'),
        't': ('',  '',  controller.stop,
              'Stop control loop'),
        
        'l': ('',  'M', controller.get_log,
              'Get log')
    }

# Initialize default controller
set_controller(controller)

class Handler(socketserver.StreamRequestHandler):

    #def __init__(self, request, client_address, server):
    #    super().__init__(request, client_address, server)

    def handle(self):
        
        global debug, controller, commands

        # Read command
        while True:
            
            print('Ready... ', end='')

            try:
                (type, code) = packet.unpack_stream(self.rfile)
            except NameError as e:
                # TODO: Differentiate closed socket from error
                print('closing socket')
                break
            
            if type == 'C':

                print("Got '{}'".format(code))

                (argument_type, output_type, function,
                 short_help) = commands.get(code, ('', '', None, ''))
                
                if debug > 0:
                    print("> Will execute '{}({})'".format(code, argument_type))
                
                # Handle input arguments
                if argument_type == '':
                    argument = tuple()
                else:
                    (type, argument) = packet.unpack_stream(self.rfile)
                    argument = (argument,)

                if debug > 0:
                    print('> Argument = {}'.format(argument))

                # Call function
                message = function(*argument)

                # Wrap outupt 
                if output_type == '':
                    message = None
                else:
                    message = (output_type, message)

                if debug > 0:
                    print('> Message = {}'.format(message))

            else:
                message = ('S', 
                           "Command expected, '{}' received".format(type))

            if message is not None:
                # Send message back
                if debug > 0:
                    print('> Sending message = ', *message)
                self.wfile.write(packet.pack(*message))

            message = ('A', code)
            if debug > 0:
                print("> Acknowledge '{}'\n".format(code))
            self.wfile.write(packet.pack(*message))
