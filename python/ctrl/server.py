import socketserver

from . import packet
import ctrl

verbose_level = 0
controller = ctrl.Controller()
commands = {}

def verbose(value = 1):
    global verbose_level
    verbose_level = value

def version():
    return '1.0'

def help(value):

    global commands
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
        'M': ('I',  '', controller.set_reference1_mode,
              'Set reference mode'),
        'P': ('D', '',  controller.set_encoder1,
              'Set encoder position'),

        'C': ('P', '',  controller.set_controller1,
              'Set controller'),
        
        's': ('',  '',  controller.start,
              'Start control loop'),
        't': ('',  '',  controller.stop,
              'Stop control loop'),
        
        'l': ('',  'M', controller.get_log,
              'Get log'),

        'p': ('',  'D', controller.get_period,
              'Get period'),
        'e': ('',  'P', controller.get_encoder1,
              'Get encoder'),

    }

# Initialize default controller
set_controller(controller)

class Handler(socketserver.StreamRequestHandler):

    #def __init__(self, request, client_address, server):
    #    super().__init__(request, client_address, server)

    def handle(self):
        
        global verbose_level, controller, commands

        if verbose_level > 0:
            print('> Connected to {}'.format(self.client_address))

        # Read command
        while True:
            
            try:
                (type, code) = packet.unpack_stream(self.rfile)
            except NameError as e:
                # TODO: Differentiate closed socket from error
                if verbose_level > 0:
                    print('> Closed connection to {}'.format(self.client_address))
                break
            
            if type == 'C':

                if verbose_level > 1:
                    print(">> Got '{}'".format(code))

                (argument_type, output_type, function,
                 short_help) = commands.get(code, ('', '', None, ''))
                
                if verbose_level > 2:
                    print(">>> Will execute '{}({})'".format(code, argument_type))
                
                # Handle input arguments
                if argument_type == '':
                    argument = tuple()
                else:
                    (type, argument) = packet.unpack_stream(self.rfile)
                    argument = (argument,)

                if verbose_level > 2:
                    print('>>> Argument = {}'.format(argument))

                # Call function
                message = function(*argument)

                # Wrap outupt 
                if output_type == '':
                    message = None
                else:
                    message = (output_type, message)

                if verbose_level > 2:
                    print('>>> Message = {}'.format(message))

            else:
                message = ('S', 
                           "Command expected, '{}' received".format(type))

            if message is not None:
                # Send message back
                if verbose_level > 2:
                    print('>>> Sending message = ', *message)
                    if verbose_level > 3:
                        print('>>>> Message content = ', packet.pack(*message))
                self.wfile.write(packet.pack(*message))

            message = ('A', code)
            if verbose_level > 2:
                print(">>> Acknowledge '{}'\n".format(code))
            self.wfile.write(packet.pack(*message))
