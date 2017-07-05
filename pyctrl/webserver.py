from flask import Flask, request
from functools import wraps
import re

import json
import pyctrl
import pyctrl.util.json as pyctrljson

app = Flask(__name__)
controller = pyctrl.Controller()
encoder = pyctrljson.JSONEncoder(sort_keys = True, indent = 4)
decoder = pyctrljson.JSONDecoder()

# decorators

# get_block_or_attribute
def get_block_or_attribute(method, type_name):

    @wraps(method, type_name)
    def wrapper(label, **kwargs):
        # get keys
        keys = kwargs.get('keys', '')
        if keys and not isinstance(keys, (list,tuple)):
            keys = [keys]
        # print('keys = {}'.format(keys))
            
        # get container
        (container,label) = controller.resolve_label(label)

        if keys:
            # return attributes
            return {k: getattr(container, method)(label, k)
                    for k in keys}
        else:
            # return container
            return {label:
                    getattr(container, type_name)[label]['block']}

    return wrapper

# encode
def encode(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        return encoder.encode(f(*args, **kwargs))

    return wrapper

# encode_label
def encode_label(f):
    
    @wraps(f)
    def wrapper(label, *args, **kwargs):
        return encoder.encode({label: f(label, *args, **kwargs)})

    return wrapper

# decode
def decode_value(f):
    
    @wraps(f)
    def wrapper(label, value, *args, **kwargs):
        return f(label, decoder.decode(value), *args, **kwargs)

    return wrapper

# decode_kwargs
def decode_kwargs(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        # print('request.args = {}'.format(request.args.get('keys','')))
        try:
            kwargs.update({k: decoder.decode(v) for k,v in request.args.items()})
        except:
            raise Exception("Arguments '{}' are not json compatible".format(request.args))
        # print('kwargs = {}'.format(kwargs))
        return f(*args, **kwargs)

    return wrapper

# add_block
def add_block(f):
    
    @wraps(f)
    def wrapper(label, module_name, class_name, **kwargs):
        return f(label, (module_name,class_name),
                 **kwargs)

    return wrapper

# json_response
def json_response(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            retval = f(*args, **kwargs)
            if retval is None:
                return json.dumps({ 'status': 'success' })
            else:
                return retval
        except KeyError as e:
            return json.dumps({ 'status': 'error',
                                'message': 'KeyError: {} is not known'.format(e) }, sort_keys = True)
        except Exception as e:
            return json.dumps({ 'status': 'error',
                                'message': repr(e) }, sort_keys = True)

    return wrapper

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
        ckwargs = kwargs.pop('kwargs', {})

        if len(kwargs) > 0:
            raise Exception("webserver.reset():: Unknown parameter(s) '{}'".format(', '.join(str(k) for k in kwargs.keys())))
        
        try:

            if True:
                warnings.warn("> Installing new instance of '{}.{}({})' as controller".format(module, pyctrl_class, ckwargs))
                
            obj_class = getattr(importlib.import_module(module),
                                pyctrl_class)
            _controller = obj_class(**ckwargs)

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
        controller.reset()
    
# set_controller
def set_controller(_controller):

    # initialize controller
    global controller, commands
    controller = _controller

    # info
    app.add_url_rule('/',
                     view_func = controller.html)
    app.add_url_rule('/info',
                     view_func = controller.html)
    
    # reset
    app.add_url_rule('/reset',
                     view_func = json_response(decode_kwargs(reset)))

    app.add_url_rule('/reset/<module_name>/<class_name>',
                     endpoint = 'reset_module',
                     view_func = json_response(decode_kwargs(reset)))
    
    # signals
    app.add_url_rule('/add/signal/<path:label>',
                     view_func = json_response(controller.add_signal))
    app.add_url_rule('/remove/signal/<path:label>',
                     view_func = json_response(controller.remove_signal))
    app.add_url_rule('/get/signal/<path:label>',
                     view_func = json_response(encode_label(controller.get_signal)))
    app.add_url_rule('/set/signal/<path:label>/<value>',
                     view_func = json_response(decode_value(controller.set_signal)))

    # sources
    app.add_url_rule('/add/source/<path:label>/<module_name>/<class_name>',
                     view_func = json_response(decode_kwargs(add_block(controller.add_source))))
    app.add_url_rule('/remove/source/<path:label>',
                     view_func = json_response(controller.remove_source))
    app.add_url_rule('/get/source/<path:label>',
                     view_func = json_response(encode(decode_kwargs(get_block_or_attribute('get_source', 'sources')))))
    app.add_url_rule('/set/source/<path:label>',
                     view_func = json_response(decode_kwargs(controller.set_source)))
    
    # filters
    app.add_url_rule('/add/filter/<path:label>/<module_name>/<class_name>',
                     view_func = json_response(decode_kwargs(add_block(controller.add_filter))))
    app.add_url_rule('/remove/filter/<path:label>',
                     view_func = json_response(controller.remove_filter))
    app.add_url_rule('/get/filter/<path:label>',
                     endpoint = 'get_filter',
                     view_func = json_response(encode(decode_kwargs(get_block_or_attribute('get_filter', 'filters')))))
    app.add_url_rule('/set/filter/<path:label>',
                     view_func = json_response(decode_kwargs(controller.set_filter)))
    
    # sinks
    app.add_url_rule('/add/sink/<path:label>/<module_name>/<class_name>',
                     view_func = json_response(decode_kwargs(add_block(controller.add_sink))))
    app.add_url_rule('/remove/sink/<path:label>',
                     view_func = json_response(controller.remove_sink))
    app.add_url_rule('/get/sink/<path:label>',
                     endpoint = 'get_sink',
                     view_func = json_response(encode(decode_kwargs(get_block_or_attribute('get_sink', 'sinks')))))
    app.add_url_rule('/set/sink/<path:label>',
                     view_func = json_response(decode_kwargs(controller.set_sink)))

    # timers
    app.add_url_rule('/add/timer/<path:label>/<module_name>/<class_name>',
                     view_func = json_response(decode_kwargs(add_block(controller.add_timer))))
    app.add_url_rule('/remove/timer/<path:label>',
                     view_func = json_response(controller.remove_timer))
    app.add_url_rule('/get/timer/<path:label>',
                     endpoint = 'get_timer',
                     view_func = json_response(encode(decode_kwargs(get_block_or_attribute('get_timer', 'timers')))))
    app.add_url_rule('/set/timer/<path:label>',
                     view_func = json_response(decode_kwargs(controller.set_timer)))

# initialize controller
set_controller(controller)

if __name__ == "__main__":

    app.run(debug = True)
    
