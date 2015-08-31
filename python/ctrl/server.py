import warnings
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
            help_str += "Error: '{}' is not a command\n".format(value)
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
        'A': ('S',  'S', help,
              'Help'),

        'B': ('S',  'S', controller.info,
              'Controller info'),
        'Z': ('',  '', controller.reset,
              'Reset controller'),

        'C': ('S', '', controller.add_signal,
              'Add signal'),
        'D': ('SD', '', controller.set_signal,
              'Set signal'),
        'E': ('S', 'D', controller.get_signal,
              'Get signal'),
        'F': ('', 'P', controller.list_signals,
              'List signals'),
        'G': ('S', '', controller.remove_signal,
              'Remove signal'),

        'H': ('SPP', '', controller.add_source,
              'Add source'),
        'I': ('SK', '', controller.set_source,
              'Set source'),
        'i': ('SR', 'K', controller.get_source,
              'Get source'),
        'J': ('S', '', controller.remove_source,
              'Remove source'),
        'K': ('', 'P', controller.list_sources,
              'List sources'),
        'L': ('SP', '', controller.write_source,
              'Write source'),
        'M': ('S', 'P', controller.read_source,
              'Read source'),

        'N': ('SPP', '', controller.add_sink,
              'Add sink'),
        'O': ('SK', '', controller.set_sink,
              'Set sink'),
        'o': ('SR', 'K', controller.get_sink,
              'Get sink'),
        'P': ('S', '', controller.remove_sink,
              'Remove sink'),
        'Q': ('', 'P', controller.list_sinks,
              'List sinks'),
        'R': ('SP', '', controller.write_sink,
              'Write sink'),
        'S': ('S', 'P', controller.read_sink,
              'Read sink'),

        'T': ('SPPP', '', controller.add_filter,
              'Add filter'),
        'U': ('SK', '', controller.set_filter,
              'Set filter'),
        'u': ('SR', 'K', controller.get_filter,
              'Get filter'),
        'V': ('S', '', controller.remove_filter,
              'Remove filter'),
        'W': ('', 'P', controller.list_filters,
              'List filters'),
        'X': ('SP', '', controller.write_filter,
              'Write filter'),
        'Y': ('S', 'P', controller.read_filter,
              'Read filter'),

        'a': ('D',  '', controller.set_period,
              'Set period'),

        'b': ('',  'D', controller.get_period,
              'Get period'),

        'c': ('',  '',  controller.start,
              'Start control loop'),

        'd': ('',  '',  controller.stop,
              'Stop control loop'),
        

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
                vargs = []
                kwargs = {}
                for letter in argument_type:
                    (type, arg) = packet.unpack_stream(self.rfile)
                    if type == 'K':
                        kwargs = arg
                    elif type == 'R':
                        vargs.extend(arg)
                    else:
                        vargs.append(arg)

                if verbose_level > 2:
                    print('>>> vargs = {}'.format(vargs))
                    print('>>> kwargs = {}'.format(kwargs))

                try:

                    # Call function
                    message = function(*vargs, **kwargs)

                except Exception as inst:
                    
                    # Something bad happen
                    message = inst
                    output_type = 'E'
                    if verbose_level > 1:
                        print('> **Exception**: ', inst)

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
