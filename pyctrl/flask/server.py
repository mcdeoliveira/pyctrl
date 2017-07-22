from flask import Flask, request, render_template, jsonify, make_response, redirect, flash, url_for
from functools import wraps
import re

import pyctrl
from pyctrl.block import Logger
import warnings
import importlib
import traceback, sys, io

from pyctrl.flask import JSONEncoder, JSONDecoder

encoder = JSONEncoder(sort_keys = True, indent = 4)
decoder = JSONDecoder()

# decorators

# decode
def decode_value(f):
    
    @wraps(f)
    def wrapper(label, value, *args, **kwargs):
        return f(label, decoder.decode(value), *args, **kwargs)

    return wrapper

# decode_kwargs_aux
def decode_kwargs_aux(e):
    if len(e) == 1:
        return decoder.decode(e[0])
    elif len(e) > 1:
        return [decoder.decode(v) for v in e]
    else:
        return None
    
# decode_kwargs
def decode_kwargs(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            kwargs.update({k: decode_kwargs_aux(request.args.getlist(k))
                           for k in request.args.keys()})
        except:
            raise Exception("Arguments '{}' are not json compatible".format(request.args))
        #print('>>> kwargs = {}'.format(kwargs))
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
        except Exception as e:
            message = io.StringIO()
            traceback.print_exc(file=message)
            retval = { 'status': 'error',
                       'message': message.getvalue() }
            
        next = request.args.get('next', None)
        if next:
            if 'status' in retval and retval['status'] == 'error':
                flash(retval['message'])
            return redirect(url_for(next))
        else:
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
        self.json_encoder = JSONEncoder

        # set api entry points
            
        # index, info and scope
        self.add_url_rule(self.base_url + '/',
                          view_func = self.index)
        self.add_url_rule(self.base_url + '/info',
                          view_func = self.info)
        self.add_url_rule(self.base_url + '/scope/<path:label>',
                          view_func = self.scope)
        
        # download controller
        self.add_url_rule(self.base_url + '/download',
                          view_func = self.download)
        
        # upload controller
        self.add_url_rule(self.base_url + '/upload',
                          methods=['GET', 'POST'],
                          view_func = self.upload)
        
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
        self.add_url_rule(self.base_url + '/html/source/<path:label>',
                         view_func = self.html_source)
        
        # filters
        self.add_url_rule(self.base_url + '/add/filter/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_filter)
        self.add_url_rule(self.base_url + '/remove/filter/<path:label>',
                         view_func = self.remove_filter)
        self.add_url_rule(self.base_url + '/get/filter/<path:label>',
                         view_func = self.get_filter)
        self.add_url_rule(self.base_url + '/set/filter/<path:label>',
                         view_func = self.set_filter)
        self.add_url_rule(self.base_url + '/html/filter/<path:label>',
                         view_func = self.html_filter)

        # sinks
        self.add_url_rule(self.base_url + '/add/sink/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_sink)
        self.add_url_rule(self.base_url + '/remove/sink/<path:label>',
                         view_func = self.remove_sink)
        self.add_url_rule(self.base_url + '/get/sink/<path:label>',
                         view_func = self.get_sink)
        self.add_url_rule(self.base_url + '/set/sink/<path:label>',
                         view_func = self.set_sink)
        self.add_url_rule(self.base_url + '/html/sink/<path:label>',
                         view_func = self.html_sink)
        
        # timers
        self.add_url_rule(self.base_url + '/add/timer/<path:label>/<module_name>/<class_name>',
                         view_func = self.add_timer)
        self.add_url_rule(self.base_url + '/remove/timer/<path:label>',
                         view_func = self.remove_timer)
        self.add_url_rule(self.base_url + '/get/timer/<path:label>',
                         view_func = self.get_timer)
        self.add_url_rule(self.base_url + '/set/timer/<path:label>',
                         view_func = self.set_timer)
        self.add_url_rule(self.base_url + '/html/timer/<path:label>',
                         view_func = self.html_timer)

        
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
        
        sinks = [ {'label': k, 'is_logger': isinstance(v['block'], Logger)}
                  for (k,v) in self.controller.sinks.items() ]
        
        return render_template('index.html',
                               baseurl = self.base_url,
                               class_name = self.controller.info('class'),
                               signals = sorted(self.controller.list_signals()),
                               sources = self.controller.list_sources(),
                               filters = self.controller.list_filters(),
                               sinks = sinks,
                               timers = self.controller.list_timers(),
                               is_running = self.controller.get_signal('is_running'))

    def info(self):

        return self.controller.html()

    def scope(self, label, *args, **kwargs):

        return render_template('scope.html',
                               baseurl = self.base_url,
                               logger = label)

    def download(self):
        response = make_response(jsonify(self.controller))
        response.headers["Content-Disposition"] \
            = "attachment; filename=controller.json"
        return response

    def upload(self, **kwargs):

        # post?
        if request.method == 'POST':
            
            # check if the post request has the file part
            if 'file' not in request.files:
                flash("Form has no field 'part'")

            else:

                # has file
                file = request.files['file']

                # empty filename?
                if not file or file.filename == '':
                    flash('No file selected')

                else:

                    # there is a file
                    try:
                        controller = decoder.decode(file.read().decode('utf-8'))
                        # print('controller = {}'.format(controller))
                        self.set_controller(controller = controller)
                        flash('New controller succesfully loaded.')
                        
                    except Exception as e:
                        message = io.StringIO()
                        traceback.print_exc(file=message)
                        flash('Could not load controller.')
                        flash(message.getvalue())
                    
        return redirect(self.base_url + '/')
        
    @json_response
    @decode_kwargs
    def reset(self, **kwargs):
        
        return self.controller.reset(**kwargs)


    @decode_kwargs
    def reset_controller(self, **kwargs):

        # set new controller
        self.set_controller(**kwargs)

        # redirect to base
        return redirect(self.base_url + '/')

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
    def get_signal(self, label, *args, **kwargs):
        return {label: self.controller.get_signal(label, *args, **kwargs)}
    
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

    @decode_kwargs
    def html_source(self, label, *args, **kwargs):
        # get container
        (container,label) = self.controller.resolve_label(label)
        return self.controller.sources[label]['block'].html();
    
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
    
    @decode_kwargs
    def html_filter(self, label, *args, **kwargs):
        # get container
        (container,label) = self.controller.resolve_label(label)
        return self.controller.filters[label]['block'].html();
    
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
    
    @decode_kwargs
    def html_sink(self, label, *args, **kwargs):
        # get container
        (container,label) = self.controller.resolve_label(label)
        return self.controller.sinks[label]['block'].html();
    
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

    @decode_kwargs
    def html_timer(self, label, *args, **kwargs):
        # get container
        (container,label) = self.controller.resolve_label(label)
        return self.controller.timers[label]['block'].html();

if __name__ == "__main__":

    try:
        import os
        os.environ['RCPY_NO_HANDLERS'] = 't'

        from pyctrl.rc import Controller
        debug = False
        RCPY = True

    except:
        from pyctrl.timer import Controller
        debug = True
        RCPY = False

    try:
        
        app = Server(__name__)
        app.config['SECRET_KEY'] = 'secret!'
        
        # initialize controller
        app.set_controller(controller = Controller(period = .01))
        
        # run app
        app.run(host='0.0.0.0',
                debug = debug)

    except:
        pass

    finally:
        sys.exit(0)
