import warnings
import socketserver
import threading
import time
import importlib

from . import packet
import pyctrl

verbose_level = 0
controller = pyctrl.Controller()
commands = {}

def verbose(value = 1):
    """
    Set verbose level

    :param value: verbose level (default = 1)
    """
    global verbose_level
    verbose_level = value

def version():
    """
    Return server version

    :return: server version
    :retype: str
    """
    return '1.0'

def help(key):
    """
    Return help on available commands

    :param key: command key
    """
    global commands
    help_str = ''

    if key:
        function = commands.get(key, ('', '', None, ''))[2]
        if not function:
            help_str += "Error: '{}' is not a command\n".format(key)
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

# log decorator
def log(message, func):
    def func_wrapper(*vargs, **kwargs):
        if verbose_level > 1:
            print(message)
        return func(*vargs, **kwargs)
    return func_wrapper

# reset controller
def reset(**kwargs):
    """
    Reset controller

    :param str module: name of the controller module (default = 'pyctrl')
    :param str pyctrl_class: name of the controller class (default = 'Controller')
    :param kwargs kwargs: other key-value pairs of attributes
    """
    
    global controller
    
    # Create new controller
    if 'module' in kwargs or 'pyctrl_class' in kwargs:

        module = kwargs.pop('module', 'pyctrl')
        pyctrl_class = kwargs.pop('pyctrl_class', 'Controller')
        
        try:

            if verbose_level > 0:
                warnings.warn("> Installing new instance of '{}.{}({})' as controller".format(module, pyctrl_class, kwargs))
                
            obj_class = getattr(importlib.import_module(module),
                                pyctrl_class)
            _controller = obj_class(**kwargs)

            # print('obj_class = {}'.format(obj_class))
            # print('_controller = {}'.format(_controller))
            
            # Make sure it is an instance of pyctrl.Controller
            if not isinstance(_controller, pyctrl.Controller):
                raise Exception("Object '{}.{}' is not and instance of pyctrl.Controller".format(module, pyctrl_class))

            controller = _controller
            set_controller(controller)

        except Exception as e:

            raise Exception("Error resetting controller: {}".format(e))

    else:
        
        # reset controller
        return controller.reset()

def set_controller(_controller = pyctrl.Controller(noclock = True)):
    """
    Set controller commands
    
    :param _controller: an instance of :py:class:`pyctrl.Controller`
    """

    # initialize controller
    global controller, commands
    controller = _controller
        
    # TODO: Complete public controller methods
    commands = { 
        'A': ('S',  'S', help,
              'Help'),

        'B': ('R', 'S', controller.info,
              'Controller info'),
        'Z': ('K',  '', reset,
              'Reset controller'),

        'C': ('S', '', controller.add_signal,
              'Add signal'),
        'D': ('SD', '', controller.set_signal,
              'Set signal'),
        'E': ('S', 'D', controller.get_signal,
              'Get signal'),
        'e': ('R', 'R', controller.get_signals,
              'Get signal'),
        'F': ('', 'P', controller.list_signals,
              'List signals'),
        'G': ('S', '', controller.remove_signal,
              'Remove signal'),

        'H': ('SPPI', '', controller.add_source,
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

        'N': ('SPPI', '', controller.add_sink,
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

        'T': ('SPPPI', '', controller.add_filter,
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

        'z': ('SSSK', '', controller.add_device,
              'Add device'),

        't': ('SPPPDI', '', controller.add_timer,
              'Add timer'),
        'f': ('SK', '', controller.set_timer,
              'Set timer'),
        'g': ('SR', 'K', controller.get_timer,
              'Get timer'),
        'v': ('S', '', controller.remove_timer,
              'Remove timer'),
        'w': ('', 'P', controller.list_timers,
              'List timers'),
        'x': ('SP', '', controller.write_timer,
              'Write timer'),
        'y': ('S', 'P', controller.read_timer,
              'Read timer'),
        
        'c': ('',  '',  log('*> Starting loop', controller.start),
              'Start control loop'),

        'd': ('',  '',  log('*< Stoping loop', controller.stop),
              'Stop control loop'),

        'j': ('',  '',  controller.join,
              'Waif for control loop'),
        
        # '0': ('', '', server_shutdown, 'Shutdown server')
        
    }

# Initialize default controller
set_controller(controller)

# exit flag
exiting = False

class Handler(socketserver.StreamRequestHandler):
    """
    Handles socket controller requests

    """

    #def __init__(self, request, client_address, server):
        #super().__init__(request, client_address, server)
    
    def handle(self):
        
        global verbose_level, controller, commands, exiting

        if verbose_level > 1:
            print('> Connected to {}'.format(self.client_address))

        # Read command
        while controller.get_state() != pyctrl.EXITING:
            
            if verbose_level > 4:
                print('>>> server::Handler::handle loop')
                print('>>> controller state = {}'.format(controller.get_state()))
           
                
            try:
                (type, code) = packet.unpack_stream(self.rfile)
                
            except NameError as e:
                # TODO: Differentiate closed socket from error
                if verbose_level > 1:
                    print('> Closed connection to {}'.format(self.client_address))
                break
            
            if type == 'C':

                if verbose_level > 2:
                    print(">> Got '{}'".format(code))

                (argument_type, output_type, function,
                 short_help) = commands.get(code, ('', '', None, ''))
                
                if verbose_level > 3:
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

                if verbose_level > 3:
                    print('>>> vargs = {}'.format(vargs))
                    print('>>> kwargs = {}'.format(kwargs))

                # shutdown?
                if code == '0':
                    print('> Be patient, shutting down server...')
                    # set exit flag
                    controller.set_state(pyctrl.EXITING)
                    # clear message
                    message = None
                    # start thread to shutdown server
                    # from http://stackoverflow.com/questions/10085996/shutdown-socketserver-serve-forever-in-one-thread-python-application
                    def kill_me_please(server):
                        time.sleep(.5)
                        server.shutdown()
                    threading.Thread(target=kill_me_please,
                                     args=(self.server,)).start()
                    
                else:
                    
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

                    if verbose_level > 3:
                        print('>>> Message = {}'.format(message))

            else:
                message = ('S', 
                           "Command expected, '{}' received".format(type))

            if message is not None:
                # Send message back
                if verbose_level > 3:
                    print('>>> Sending message = ', *message)
                    if verbose_level > 4:
                        print('>>>> Message content = ', packet.pack(*message))
                self.wfile.write(packet.pack(*message))

            message = ('A', code)
            if verbose_level > 3:
                print(">>> Acknowledge '{}'\n".format(code))
            self.wfile.write(packet.pack(*message))

        if verbose_level > 4:
            print('>>> Exiting server::handle loop')
            print('>>> controller state = {}'.format(controller.get_state()))
           
