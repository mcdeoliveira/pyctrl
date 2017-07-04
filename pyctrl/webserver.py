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

# auxiliary

# parse_list
def parse_list(l):
    if l:
        return re.split(',', l)
    else:
        return []
    
# get_container
def get_container(label, *args, **kwargs):
    (container,label) = controller.resolve_label(label)
    print('label = {}'.format(label))
    print('args = {}'.format(args))
    print('kwargs = {}'.format(kwargs))
    return container

# get_block_or_attribute
def get_block_or_attribute(method, type_name):

    @wraps(method, type_name)
    def wrapper(label, **kwargs):
        # get keys
        keys = kwargs.get('keys', '')
        if keys and not isinstance(keys, (list,tuple)):
            keys = [keys]
        print('keys = {}'.format(keys))
            
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

# get_method_key
def get_method_key(method):

    @wraps(method)
    def wrapper(label, key):
        (container,label) = controller.resolve_label(label)
        return {key:
                getattr(container, method)(label, key)}

    return wrapper

# decorators

# encode
def encode(f):
    
    @wraps(f)
    def wrapper(label, *args, **kwargs):
        return encoder.encode(f(label, *args, **kwargs))

    return wrapper

# encode_label
def encode_label(f):
    
    @wraps(f)
    def wrapper(label, *args, **kwargs):
        return encoder.encode({label: f(label, *args, **kwargs)})

    return wrapper

# decode
def decode(f):
    
    @wraps(f)
    def wrapper(label, value, *args, **kwargs):
        return f(label, decoder.decode(value), *args, **kwargs)

    return wrapper

# decode_kwargs
def decode_kwargs(f):
    
    @wraps(f)
    def wrapper(label, *args, **kwargs):
        print('request.args = {}'.format(request.args.get('keys','')))
        try:
            kwargs.update({k: decoder.decode(v) for k,v in request.args.items()})
        except:
            raise Exception("Arguments '{}' are not json compatible".format(request.args))
        print('kwargs = {}'.format(kwargs))
        return f(label, *args, **kwargs)

    return wrapper

# add_block
def add_block(f):
    
    @wraps(f)
    def wrapper(label, module_name, class_name, **kwargs):
        return f(label, (module_name,class_name),
                 **kwargs)

    return wrapper

# inputs_and_outputs
def inputs_and_outputs(f):
    
    @wraps(f)
    def wrapper(label, module_name, class_name):
        kwargs = request.args.to_dict(flat = True)

        inputs = parse_list(kwargs.pop('inputs', []))
        outputs = parse_list(kwargs.pop('outputs', []))
        kwargs = {k: decoder.decode(v) for k,v in kwargs.items()}
        
        return f(label, (module_name,class_name),
                 inputs = inputs, outputs = outputs,
                 **kwargs)

    return wrapper

# inputs
def inputs(f):
    
    @wraps(f)
    def wrapper(label, module_name, class_name):
        kwargs = request.args.to_dict(flat = True)

        inputs = parse_list(kwargs.pop('inputs', []))
        kwargs = {k: decoder.decode(v) for k,v in kwargs.items()}
        
        return f(label, (module_name,class_name),
                 inputs = inputs,
                 **kwargs)

    return wrapper

# outputs
def outputs(f):
    
    @wraps(f)
    def wrapper(label, module_name, class_name):
        kwargs = request.args.to_dict(flat = True)

        outputs = parse_list(kwargs.pop('outputs', []))
        kwargs = {k: decoder.decode(v) for k,v in kwargs.items()}
        
        return f(label, (module_name,class_name),
                 outputs = outputs,
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
    
    # signals
    app.add_url_rule('/add/signal/<path:label>',
                     view_func = json_response(controller.add_signal))
    app.add_url_rule('/remove/signal/<path:label>',
                     view_func = json_response(controller.remove_signal))
    app.add_url_rule('/get/signal/<path:label>',
                     view_func = json_response(encode_label(controller.get_signal)))
    app.add_url_rule('/set/signal/<path:label>/<value>',
                     view_func = json_response(decode(controller.set_signal)))

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
    
