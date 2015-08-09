import time
import numpy

import ctrl.client
import ctrl.logger as logger

HOST, PORT = "192.168.10.107", 9999
HOST, PORT = "localhost", 9999

controller = ctrl.client.Controller(host = HOST, port = PORT)
print(controller.help())

print(controller.help('s'))
print(controller.help('S'))

controller.add_sink('logger', logger.Logger(),
                    ['clock'])

print(controller.info('all'))

controller.set_sink('logger', 'reset')

with controller:
    time.sleep(.1)

print(controller.read_sink('logger'))

controller.remove_sink('logger')
    
