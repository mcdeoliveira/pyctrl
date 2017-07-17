import flask.json as json

import pyctrl
import pyctrl.block
import importlib

# json

class JSONEncoder(json.JSONEncoder):
    
    def default(self, obj):
        # Convert objects to a dictionary of their representation
        d = { '__class__': obj.__class__.__name__, 
              '__module__': type(obj).__module__ }
        if isinstance(obj, pyctrl.block.Block):
            d.update(obj.get())
        elif d['__module__'] == 'numpy':
            d.update({
                '__class__': 'array',
                'object': obj.tolist()
            })
        else:
            d.update(obj.__dict__)
        return d

class JSONDecoder(json.JSONDecoder):
    
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            kwargs = dict( (key, value)
                           for key, value in d.items() )

            #print('class_name = {}'.format(class_name))
            #print('module_name = {}'.format(module_name))
            #print('kwargs = {}'.format(kwargs))

            try:
                
                # try to call constructor first
                inst = getattr(importlib.import_module(module_name), 
                               class_name)(**kwargs)

            except pyctrl.block.BlockException:

                # construct first then update
                inst = getattr(importlib.import_module(module_name), 
                               class_name)()
                
                inst.__dict__.update(kwargs)
                
        else:
            inst = d
        return inst
