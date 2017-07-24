from flask import Flask, request
from flask_restful import Resource, Api
from functools import wraps
import json
import re

from pyctrl.json import JSONEncoder, JSONDecoder

app = Flask(__name__)
api = Api(app)

import pyctrl

jsonEncoder = JSONEncoder(sort_keys = True, indent = 4)
jsonDecoder = JSONDecoder()

controller = pyctrl.Controller()

# execute
def execute(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return json.dumps({ 'status': 'error', 'message': str(e) })

    return wrapper

# execute_with_success
def execute_with_success(f):
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        try:
            f(*args, **kwargs)
            return json.dumps({ 'status': 'success', 'message': None })
        except Exception as e:
            return json.dumps({ 'status': 'error', 'message': str(e) })

    return wrapper

# parse_list
def parse_list(l):
    if isinstance(l, (list, tuple)):
        l = ','.join(l)
    if l:
        return re.split(',', l)
    else:
        return []

# index
@app.route('/')
def index():
    return 'Hello, World!'

# info
@app.route('/info')
def info():
    return controller.html()


# sources
@app.route('/add/source/<path:label>/<module>/<device_class>',
           methods=['GET'])
@execute_with_success
def add_sources(label, module, device_class):
    kwargs = dict(request.args)
    outputs = parse_list(kwargs.pop('outputs', []))
    
    controller.add_device(label,
                          (module, device_class),
                          outputs,
                          **kwargs)

@app.route('/get/source/<path:label>',
           methods=['GET'])
@execute
def get_source(label):
    kwargs = dict(request.args)
    keys = parse_list(kwargs.pop('keys', []))
    
    return jsonEncoder.encode(controller.get_source(label, *keys))

# filters
@app.route('/add/filter/<path:label>/<module>/<device_class>',
           methods=['GET'])
@execute_with_success
def add_filters(label, module, device_class):
    kwargs = dict(request.args)
    inputs = parse_list(kwargs.pop('inputs', []))
    outputs = parse_list(kwargs.pop('outputs', []))
    
    controller.add_filter(label,
                          (module, device_class),
                          inputs, outputs,
                          **kwargs)

@app.route('/get/filter/<path:label>',
           methods=['GET'])
@execute
def get_filter(label):
    kwargs = dict(request.args)
    keys = parse_list(kwargs.pop('keys', []))
    
    return jsonEncoder.encode(controller.get_filter(label, *keys))

# sinks
@app.route('/add/sink/<path:label>/<module>/<device_class>',
           methods=['GET'])
@execute_with_success
def add_sinks(label, module, device_class):
    kwargs = dict(request.args)
    inputs = parse_list(kwargs.pop('inputs', []))
    
    controller.add_sink(label,
                        (module, device_class),
                        inputs,
                        **kwargs)
    
@app.route('/get/sink/<path:label>')
@execute
def get_sink(label):
    (container, label) = controller.resolve_label(label)
    return jsonEncoder.encode(container.sinks[label]['block'])

@app.route('/get/sink_property/<path:label>/<key>')
@execute
def get_sink_property(label, key):
    if key == '*':
        return jsonEncoder.encode(controller.get_sink(label))
    else:
        return jsonEncoder.encode({key: controller.get_sink(label, key)})

# timers
@app.route('/add/timer/<path:label>/<module>/<device_class>',
           methods=['GET'])
@execute_with_success
def add_timers(label, module, device_class):
    kwargs = dict(request.args)
    inputs = parse_list(kwargs.pop('inputs', []))
    outputs = parse_list(kwargs.pop('outputs', []))
    
    controller.add_timer(label,
                         (module, device_class),
                         inputs, outputs,
                         **kwargs)
    
@app.route('/get/timer/<path:label>',
           methods=['GET'])
@execute
def get_timer(label):
    kwargs = dict(request.args)
    keys = parse_list(kwargs.pop('keys', []))
    
    return jsonEncoder.encode(controller.get_timer(label, *keys))

class Test():

    @app.route('/test/<label>')
    def test(self, label):
        return label

if __name__ == '__main__':
    app.run(debug=True)
