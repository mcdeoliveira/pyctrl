import socket
import sys
from Packet import Packet

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(Packet.pack('C', data))

    # Receive data from the server and shut down
    buffer = sock.recv(1024)
finally:
    sock.close()

print("Sent:     {}".format(data))
print("Received: {}".format(str(buffer)))

(type, contents) = Packet.unpack(buffer)
if type == 'M':
    print(contents)

print("\n")
