from flask import Flask, request
from functools import wraps
import re

import json
import pyctrl
import pyctrl.util.json as pyctrljson

encoder = pyctrljson.JSONEncoder(sort_keys = True, indent = 4)
decoder = pyctrljson.JSONDecoder()

# decorators

# get_block_or_attribute
def get_block_or_attribute(controller, method, type_name):

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

# Server class

class Server(Flask):

    def __init__(self, *args, **kwargs):

        self.controller = None
        self.base_url = ''

        # call super
        super().__init__(*args, **kwargs)

    def reset(self, **kwargs):
        """
        Reset controller
        
        :param str module: name of the controller module (default = 'pyctrl')
        :param str pyctrl_class: name of the controller class (default = 'Controller')
        :param kwargs kwargs: other key-value pairs of attributes
        """
    
        if self.controller:
            # reset controller
            self.controller.reset()
    
    def set_controller(self, **kwargs):

        # Create new controller?
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
                controller = obj_class(**ckwargs)

                # print('obj_class = {}'.format(obj_class))
                # print('_controller = {}'.format(_controller))
            
                # Make sure it is an instance of pyctrl.Controller
                if not isinstance(controller, pyctrl.Controller):
                    raise Exception("Object '{}.{}' is not and instance of pyctrl.Controller".format(module, pyctrl_class))

                self.controller = controller

            except Exception as e:

                raise Exception("Error resetting controller: {}".format(e))

        elif 'controller' in kwargs:

            controller = kwargs.pop('controller')

            # Make sure it is an instance of pyctrl.Controller
            if not isinstance(controller, pyctrl.Controller):
                raise Exception("Object '{}.{}' is not and instance of pyctrl.Controller".format(module, pyctrl_class))
                
            
            self.controller = controller

        # set api entry points
            
        # info
        app.add_url_rule(self.base_url + '/',
                         view_func = self.controller.html)
        app.add_url_rule(self.base_url + '/info',
                         view_func = self.controller.html)

        # reset
        app.add_url_rule(self.base_url + '/reset',
                         view_func = json_response(decode_kwargs(self.reset)))

        app.add_url_rule(self.base_url + '/set/controller/<module_name>/<class_name>',
                         endpoint = 'reset_module',
                         view_func = json_response(decode_kwargs(self.set_controller)))

        # signals
        app.add_url_rule(self.base_url + '/add/signal/<path:label>',
                         view_func = json_response(self.controller.add_signal))
        app.add_url_rule(self.base_url + '/remove/signal/<path:label>',
                         view_func = json_response(self.controller.remove_signal))
        app.add_url_rule(self.base_url + '/get/signal/<path:label>',
                         view_func = json_response(encode_label(self.controller.get_signal)))
        app.add_url_rule(self.base_url + '/set/signal/<path:label>/<value>',
                         view_func = json_response(decode_value(self.controller.set_signal)))

        # sources
        app.add_url_rule(self.base_url + '/add/source/<path:label>/<module_name>/<class_name>',
                         view_func = json_response(decode_kwargs(add_block(self.controller.add_source))))
        app.add_url_rule(self.base_url + '/remove/source/<path:label>',
                         view_func = json_response(self.controller.remove_source))
        app.add_url_rule(self.base_url + '/get/source/<path:label>',
                         view_func = json_response(encode(decode_kwargs(get_block_or_attribute(self.controller, 'get_source', 'sources')))))
        app.add_url_rule(self.base_url + '/set/source/<path:label>',
                         view_func = json_response(decode_kwargs(self.controller.set_source)))

        # filters
        app.add_url_rule(self.base_url + '/add/filter/<path:label>/<module_name>/<class_name>',
                         view_func = json_response(decode_kwargs(add_block(self.controller.add_filter))))
        app.add_url_rule(self.base_url + '/remove/filter/<path:label>',
                         view_func = json_response(self.controller.remove_filter))
        app.add_url_rule(self.base_url + '/get/filter/<path:label>',
                         endpoint = 'get_filter',
                         view_func = json_response(encode(decode_kwargs(get_block_or_attribute(self.controller, 'get_filter', 'filters')))))
        app.add_url_rule(self.base_url + '/set/filter/<path:label>',
                         view_func = json_response(decode_kwargs(self.controller.set_filter)))

        # sinks
        app.add_url_rule(self.base_url + '/add/sink/<path:label>/<module_name>/<class_name>',
                         view_func = json_response(decode_kwargs(add_block(self.controller.add_sink))))
        app.add_url_rule(self.base_url + '/remove/sink/<path:label>',
                         view_func = json_response(self.controller.remove_sink))
        app.add_url_rule(self.base_url + '/get/sink/<path:label>',
                         endpoint = 'get_sink',
                         view_func = json_response(encode(decode_kwargs(get_block_or_attribute(self.controller, 'get_sink', 'sinks')))))
        app.add_url_rule(self.base_url + '/set/sink/<path:label>',
                         view_func = json_response(decode_kwargs(self.controller.set_sink)))

        # timers
        app.add_url_rule(self.base_url + '/add/timer/<path:label>/<module_name>/<class_name>',
                         view_func = json_response(decode_kwargs(add_block(self.controller.add_timer))))
        app.add_url_rule(self.base_url + '/remove/timer/<path:label>',
                         view_func = json_response(self.controller.remove_timer))
        app.add_url_rule(self.base_url + '/get/timer/<path:label>',
                         endpoint = 'get_timer',
                         view_func = json_response(encode(decode_kwargs(get_block_or_attribute(self.controller, 'get_timer', 'timers')))))
        app.add_url_rule(self.base_url + '/set/timer/<path:label>',
                         view_func = json_response(decode_kwargs(self.controller.set_timer)))


if __name__ == "__main__":

    from pyctrl import Controller
    
    app = Server(__name__)

    # initialize controller
    app.set_controller(controller = Controller())

    # run app
    app.run(debug = True)

