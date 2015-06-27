import struct

class Packet:

    def unpack_stream(stream):

        buffer = stream.read(1)
        if not buffer:
            raise NameError('read failed')
        (btype,) = struct.unpack('c', buffer)

        if btype == b'A' or btype == b'C':
            # Read next character
            buffer = stream.read(1)
            (command,) = struct.unpack('c', buffer)
            return (str(btype, 'utf-8'), str(command, 'utf-8'))

        elif btype == b'S':
            # Read length (int)
            buffer = stream.read(4)
            (blen,) = struct.unpack('<I', buffer)
            # Read string (blen*char)
            buffer = stream.read(blen)
            (bmessage,) = struct.unpack('%ds' % (blen,), buffer)
            return ('S', str(bmessage, 'utf-8'))

        elif btype == b'I':
            # Read int
            buffer = stream.read(4)
            (i,) = struct.unpack('<i', buffer)
            return ('I', i)

        elif btype == b'F':
            # Read float
            buffer = stream.read(4)
            (f,) = struct.unpack('<f', buffer)
            return ('F', f)

        elif btype == b'D':
            # Read double
            buffer = stream.read(8)
            (f,) = struct.unpack('<d', buffer)
            return ('D', d)

        else:
            raise NameError('Unknown type')

    def unpack(buffer):

        (btype,), buffer = struct.unpack('c', buffer[:1]), buffer[1:]

        if btype == b'A':
            (command,) = struct.unpack('c', buffer[:1])
            return ('A', str(command, 'utf-8'))

        elif btype == b'C':
            (command,) = struct.unpack('c', buffer[:1])
            return ('C', str(command, 'utf-8'))

        elif btype == b'S':
            (blen,), buffer = struct.unpack('<I', buffer[:4]), buffer[4:]
            (bmessage,) = struct.unpack('%ds' % (blen,), buffer)
            return ('S', str(bmessage, 'utf-8'))

        elif btype == b'I':
            (i,) = struct.unpack('<i', buffer[:4])
            return ('I', i)

        elif btype == b'F':
            (f,) = struct.unpack('<f', buffer[:4])
            return ('F', f)

        elif btype == b'D':
            (f,) = struct.unpack('<d', buffer[:8])
            return ('D', d)

        else:
            raise NameError('Unknown type')

    def pack(type, content):

        # command
        if type == 'A':
            bmessage = bytes(content[0], 'utf-8')
            return struct.pack('cc', b'A', bmessage)

        elif type == 'C':
            bmessage = bytes(content[0], 'utf-8')
            return struct.pack('cc', b'C', bmessage)
          
        # message
        elif type == 'S':
            bmessage = bytes(content, 'utf-8')
            blen = len(bmessage)
            return struct.pack('<cI%ds' % (blen,),
                               b'S', 
                               blen,
                               bmessage)

        # integer
        elif type == 'I':
            return struct.pack('<ci', b'I', content)

        # float
        elif type == 'F':
            return struct.pack('<cf', b'F', content)

        # double
        elif type == 'D':
            return struct.pack('<cd', b'D', content)

        else:
            raise NameError('Unknown type')
