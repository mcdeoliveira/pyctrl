import socket
import sys
from Packet8 import Packet

HOST, PORT = "localhost", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(Packet.pack('C', 'X'))

finally:
    sock.close()

