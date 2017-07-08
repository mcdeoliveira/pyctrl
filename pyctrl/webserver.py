from flask import Flask, request, render_template, jsonify
from functools import wraps
import re

import pyctrl
import pyctrl.util.json as pyctrljson
import warnings
import importlib

encoder = pyctrljson.JSONEncoder(sort_keys = True, indent = 4)
decoder = pyctrljson.JSONDecoder()

# decorators

# encode_label
def wrap_label(f):
    
    @wraps(f)
    def wrapper(label, *args, **kwargs):
        return {label: f(label, *args, **kwargs)}

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
        try:
            kwargs.update({k: decoder.decode(v) for k,v in request.args.items()})
        except:
            raise Exception("Arguments '{}' are not json compatible".format(request.args))
        print('>>> kwargs = {}'.format(kwargs))
        return f(*args, **kwargs)

    return wrapper

# json_response
def json_response(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            retval = f(*args, **kwargs)
            if retval is None:
                retval = { 'status': 'success' }
        except KeyError as e:
            retvar = { 'status': 'error',
                       'message': 'KeyError: {} is not known'.format(e) }
        except Exception as e:
            retval = { 'status': 'error', 'message': repr(e) }

        return jsonify(retval)
        
    return wrapper

# Server class

class Server(Flask):

    def __init__(self, *args, **kwargs):

        self.controller = None
        self.base_url = ''

        # call super
        super().__init__(*args, **kwargs)

        # change json_encoder
        self.json_encoder = pyctrljson.JSONEncoder

        # set api entry points
            
        # index, info and scope
        self.add_url_rule(self.base_url + '/',
                          view_func = self.index)
        self.add_url_rule(self.base_url + '/info',
                          view_func = self.info)
        self.add_url_rule(self.base_url + '/scope',
                          view_func = self.scope)

        # reset
        self.add_url_rule(self.base_url + '/reset',
                          view_func = self.reset)

        # set controller
        self.add_url_rule(self.base_url + '/set/controller/<module>/<pyctrl_class>',
                          view_func = self.reset_controller)
        
        # start and stop
        self.add_url_rule(self.base_url + '/start',
                         view_func = self.start)
        self.add_url_rule(self.base_url + '/stop',
                         view_func = self.stop)
        
        # signals
        self.add_url_rule(self.base_url + '/add/signal/<path:label>',
                         view_func = self.add_signal)
        self.add_url_rule(self.base_url + '/remove/signal/<path:label>',
                         view_func = self.remove_signal)
        self.add_url_rule(self.base_url + '/get/signal/<path:label>',
                         view_func = self.get_signal)
        self.add_url_rule(self.base_url + '/set/signal/<path:label>/<value>',
                         view_func = self.set_signal)
        self.add_url_rule(self.base_url + '/list/signals',
                         view_func = self.list_signals)

        # sources
        self.add_url_rule(self.base_url + '/add/source/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_source)
        self.add_url_rule(self.base_url + '/remove/source/<path:label>',
                         view_func = self.remove_source)
        self.add_url_rule(self.base_url + '/get/source/<path:label>',
                         view_func = self.get_source)
        self.add_url_rule(self.base_url + '/set/source/<path:label>',
                         view_func = self.set_source)
        
        # filters
        self.add_url_rule(self.base_url + '/add/filter/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_filter)
        self.add_url_rule(self.base_url + '/remove/filter/<path:label>',
                         view_func = self.remove_filter)
        self.add_url_rule(self.base_url + '/get/filter/<path:label>',
                         view_func = self.get_filter)
        self.add_url_rule(self.base_url + '/set/filter/<path:label>',
                         view_func = self.set_filter)

        # sinks
        self.add_url_rule(self.base_url + '/add/sink/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_sink)
        self.add_url_rule(self.base_url + '/remove/sink/<path:label>',
                         view_func = self.remove_sink)
        self.add_url_rule(self.base_url + '/get/sink/<path:label>',
                         view_func = self.get_sink)
        self.add_url_rule(self.base_url + '/set/sink/<path:label>',
                         view_func = self.set_sink)
        
        # timers
        self.add_url_rule(self.base_url + '/add/timer/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_timer)
        self.add_url_rule(self.base_url + '/remove/timer/<path:label>',
                         view_func = self.remove_timer)
        self.add_url_rule(self.base_url + '/get/timer/<path:label>',
                         view_func = self.get_timer)
        self.add_url_rule(self.base_url + '/set/timer/<path:label>',
                         view_func = self.set_timer)

        
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

    # auxiliary

    def get_keys(self, method, type_name,
                 label, **kwargs):

        # get keys
        keys = kwargs.get('keys', '')
        if keys and not isinstance(keys, (list,tuple)):
            keys = [keys]
        print('keys = {}'.format(keys))
                
        # get container
        (container,label) = self.controller.resolve_label(label)
                
        if keys:
            # return attributes
            if len(keys) > 1:
                return method(label, *keys)
            else:
                return {keys[0]: method(label, *keys)}
        else:
            # return container
            return {label:
                    getattr(container, type_name)[label]['block']}

    
    # handlers
        
    def index(self):
        
        return render_template('index.html',
                               baseurl = self.base_url,
                               class_name = self.controller.info('class'),
                               signals = sorted(self.controller.list_signals()),
                               sources = self.controller.list_sources(),
                               filters = self.controller.list_filters(),
                               sinks = self.controller.list_sinks(),
                               timers = self.controller.list_timers())

    def info(self):

        return self.controller.html()
        
    def scope(self):
        
        return render_template('scope.html',
                               baseurl = self.base_url,
                               signals = sorted(self.controller.list_signals()))

    @json_response
    @decode_kwargs
    def reset(self, **kwargs):
        
        return self.controller.reset(**kwargs)


    @json_response
    @decode_kwargs
    def reset_controller(self, **kwargs):

        return self.set_controller(**kwargs)

    @json_response
    def start(self):
        
        return self.controller.start()
    
    @json_response
    def stop(self):
        
        return self.controller.stop()

    @json_response
    def add_signal(self, *args, **kwargs):
        
        return self.controller.add_signal(*args, **kwargs)
    
    @json_response
    def remove_signal(self, *args, **kwargs):
        
        return self.controller.remove_signal(*args, **kwargs)
                      
    @json_response
    @wrap_label
    def get_signal(self, *args, **kwargs):

        return self.controller.get_signal(*args, **kwargs)
    
    @json_response
    @decode_value
    def set_signal(self, *args, **kwargs):

        return self.controller.set_signal(*args, **kwargs)
    
    @json_response
    def list_signals(self):
        return self.controller.list_signals()

    # sources
    @json_response
    @decode_kwargs
    def add_source(self, label, module_name, class_name, **kwargs):

        return self.controller.add_source(label, (module_name, class_name),
                                          **kwargs)
    
    @json_response
    def remove_source(self, *args, **kwargs):
        return self.controller.remove_source(*args, **kwargs)
    
    @json_response
    @decode_kwargs
    def get_source(self, label, *args, **kwargs):
        return self.get_keys(self.controller.get_source, 'sources',
                             label, *args, **kwargs)
    
    @json_response
    @decode_kwargs
    def set_source(self, *args, **kwargs):
        return self.controller.set_source(*args, **kwargs)

    # filters
    @json_response
    @decode_kwargs
    def add_filter(self, label, module_name, class_name, **kwargs):

        return self.controller.add_filter(label, (module_name, class_name),
                                          **kwargs)
    
    @json_response
    def remove_filter(self, *args, **kwargs):
        return self.controller.remove_filter(*args, **kwargs)
    
    @json_response
    @decode_kwargs
    def get_filter(self, label, *args, **kwargs):
        return self.get_keys(self.controller.get_filter, 'filters',
                             label, *args, **kwargs)
    
    @json_response
    @decode_kwargs
    def set_filter(self, *args, **kwargs):
        return self.controller.set_filter(*args, **kwargs)
    
    # sinks
    @json_response
    @decode_kwargs
    def add_sink(self, label, module_name, class_name, **kwargs):

        return self.controller.add_sink(label, (module_name, class_name),
                                          **kwargs)
    
    @json_response
    def remove_sink(self, *args, **kwargs):
        return self.controller.remove_sink(*args, **kwargs)
    
    @json_response
    @decode_kwargs
    def get_sink(self, label, *args, **kwargs):
        return self.get_keys(self.controller.get_sink, 'sinks',
                             label, *args, **kwargs)
    
    @json_response
    @decode_kwargs
    def set_sink(self, *args, **kwargs):
        return self.controller.set_sink(*args, **kwargs)
    
    # timers
    @json_response
    @decode_kwargs
    def add_timer(self, label, module_name, class_name, **kwargs):
        
        return self.controller.add_timer(label, (module_name, class_name),
                                         **kwargs)
    
    @json_response
    def remove_timer(self, *args, **kwargs):
        return self.controller.remove_timer(*args, **kwargs)
    
    @json_response
    @decode_kwargs
    def get_timer(self, label, *args, **kwargs):
        return self.get_keys(self.controller.get_timer, 'timers',
                             label, *args, **kwargs)
    
    @json_response
    @decode_kwargs
    def set_timer(self, *args, **kwargs):
        return self.controller.set_timer(*args, **kwargs)
    
if __name__ == "__main__":

    from pyctrl.timer import Controller
    
    app = Server(__name__)

    # initialize controller
    app.set_controller(controller = Controller(period = 1))

    # run app
    app.run(debug = True)

