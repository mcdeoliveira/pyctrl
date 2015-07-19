import socketserver

import ctrl.server
import ctrl.sim

# Setup simulated controller

import ctrl.sim as sim
import math
import numpy
controller = sim.Controller()

Ts = 0.01              # s
a = 17                 # 1/s
k = 0.11               # cycles/s duty
c = math.exp(-a * Ts)  # adimensional

controller.set_period(Ts)
controller.set_model1( numpy.array((0, (k*Ts)*(1-c)/2, (k*Ts)*(1-c)/2)), 
                       numpy.array((1, -(1 + c), c)),
                       numpy.array((0,0)) )

# HOST AND PORT
HOST, PORT = "localhost", 9999

# Create the server, binding to HOST and PORT
server = socketserver.TCPServer((HOST, PORT), 
                                ctrl.server.Handler)

# Initiate server
try:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print('Controller Server\nVersion {}'.format(ctrl.server.version()))
    server.serve_forever()

except (KeyboardInterrupt, SystemExit):
    pass

finally:
    print('Exiting...')
    server.shutdown()
