import struct
import numpy

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
            (d,) = struct.unpack('<d', buffer)
            return ('D', d)

        elif btype == b'V':
            # Read type (char)
            buffer = stream.read(1)
            (vtype,) = struct.unpack('c', buffer)
            # Read length (int)
            buffer = stream.read(4)
            (vlen,) = struct.unpack('<I', buffer)
            # Read data (blen*)
            if vtype == b'I':
                vector = numpy.zeros(vlen, int)
                for k in range(vlen):
                    buffer = stream.read(4)
                    (vector[k],) = struct.unpack('<i', buffer)
            elif vtype == b'F':
                vector = numpy.zeros(vlen, float)
                for k in range(vlen):
                    buffer = stream.read(4)
                    (vector[k],) = struct.unpack('<f', buffer)
            elif vtype == b'D':
                vector = numpy.zeros(vlen, float)
                for k in range(vlen):
                    buffer = stream.read(8)
                    (vector[k],) = struct.unpack('<d', buffer)
            else:
                # error
                pass

            # return vector
            return ('V', vector)

        elif btype == b'M':
            # Read row size (int)
            buffer = stream.read(4)
            (rsize,) = struct.unpack('<I', buffer)
            # read vector
            (vtype, vector) = Packet.unpack_stream(stream)
            # resize vector as matrix
            vector = numpy.resize(vector, (rsize, vector.size/rsize)).transpose()
            # return vector
            return ('M', vector)

        else:
            raise NameError('Unknown type')

    def pack_vector(type, content):
        buffer = b''
        type = '<' + type
        if len(content.shape) > 1:
            # matrix
            for k in range(content.shape[1]):
                for value in content[:,k]:
                    buffer += struct.pack(type, value)
        else:
            # vector
            for value in content:
                buffer += struct.pack(type, value)
        return buffer
        
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

        #vector
        elif type == 'V':
            vlen = content.size
            if numpy.issubsctype(content, numpy.int):
                return ( struct.pack('<ccI', b'V', b'I', vlen) +
                         Packet.pack_vector('i', content) )
            elif numpy.issubsctype(content, numpy.float32):
                return ( struct.pack('<ccI', b'V', b'F', vlen) +
                         Packet.pack_vector('f', content) )
            elif numpy.issubsctype(content, numpy.float):
                return ( struct.pack('<ccI', b'V', b'D', vlen) +
                         Packet.pack_vector('d', content) )
            else:
                # error
                pass

        #matrix
        elif type == 'M':
            rsize = content.shape[0]
            return ( struct.pack('<cI', b'M', rsize) +
                     Packet.pack('V', content) )

        else:
            raise NameError('Unknown type')

    # def unpack(buffer):

    #     (btype,), buffer = struct.unpack('c', buffer[:1]), buffer[1:]

    #     if btype == b'A':
    #         (command,) = struct.unpack('c', buffer[:1])
    #         return ('A', str(command, 'utf-8'))

    #     elif btype == b'C':
    #         (command,) = struct.unpack('c', buffer[:1])
    #         return ('C', str(command, 'utf-8'))

    #     elif btype == b'S':
    #         (blen,), buffer = struct.unpack('<I', buffer[:4]), buffer[4:]
    #         (bmessage,) = struct.unpack('%ds' % (blen,), buffer)
    #         return ('S', str(bmessage, 'utf-8'))

    #     elif btype == b'I':
    #         (i,) = struct.unpack('<i', buffer[:4])
    #         return ('I', i)

    #     elif btype == b'F':
    #         (f,) = struct.unpack('<f', buffer[:4])
    #         return ('F', f)

    #     elif btype == b'D':
    #         (f,) = struct.unpack('<d', buffer[:8])
    #         return ('D', d)

    #     elif btype == b'V':
    #         (blen,), buffer = struct.unpack('<I', buffer[:4]), buffer[4:]
    #         (bmessage,) = struct.unpack('%ds' % (blen,), buffer)
    #         return ('V', str(bmessage, 'utf-8'))

    #     elif btype == b'M':
    #         (blen,), buffer = struct.unpack('<I', buffer[:4]), buffer[4:]
    #         (bmessage,) = struct.unpack('%ds' % (blen,), buffer)
    #         return ('M', str(bmessage, 'utf-8'))

    #     else:
    #         raise NameError('Unknown type')
