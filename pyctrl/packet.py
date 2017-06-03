import struct
import numpy
import pickle

debug_level = 0

def unpack_stream(stream):

    if debug_level > 0:
        print('> packet: waiting for next character')
    buffer = stream.read(1)
    if not buffer:
        raise NameError('read failed')
    (btype,) = struct.unpack('c', buffer)

    if debug_level > 0:
        print("> packet: got '{}'".format(btype))

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
        if debug_level > 0:
            print("> packet::vector: '{}[{}]'".format(vtype, vlen))
        if vtype == b'I':
            vector = numpy.zeros(vlen, int)
            buffer = stream.read(4 * vlen)
            for k in range(vlen):
                (vector[k],) = struct.unpack('<i', buffer[k*4:(k+1)*4])
        elif vtype == b'F':
            vector = numpy.zeros(vlen, float)
            buffer = stream.read(4 * vlen)
            for k in range(vlen):
                (vector[k],) = struct.unpack('<f', buffer[k*4:(k+1)*4])
        elif vtype == b'D':
            vector = numpy.zeros(vlen, float)
            buffer = stream.read(8 * vlen)
            for k in range(vlen):
                (vector[k],) = struct.unpack('<d', buffer[k*8:(k+1)*8])
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
        (vtype, vector) = unpack_stream(stream)
        # resize vector as matrix
        vector = numpy.resize(vector, (rsize, int(vector.size/rsize)))
        # return vector
        return ('M', vector)

    elif btype == b'P' or btype == b'E' or btype == b'K' or btype == b'R':
        # Read object size (int)
        buffer = stream.read(4)
        (bsize,) = struct.unpack('<I', buffer)
        # read object
        buffer = stream.read(bsize)
        # unpickle
        object = pickle.loads(buffer)
        # return object
        if btype == b'P':
            return ('P', object)
        elif btype == b'E':
            return ('E', object)
        elif btype == b'K':
            return ('K', object)
        else: # btype == b'R':
            return ('R', object)

    else:
        raise NameError('Unknown type')

def pack_vector(type, content):
    buffer = b''
    type = '<' + type
    if len(content.shape) > 1:
        # matrix
        for k in range(content.shape[0]):
            for value in content[k,:]:
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
                     pack_vector('i', content) )
        elif numpy.issubsctype(content, numpy.float32):
            return ( struct.pack('<ccI', b'V', b'F', vlen) +
                     pack_vector('f', content) )
        elif numpy.issubsctype(content, numpy.float):
            return ( struct.pack('<ccI', b'V', b'D', vlen) +
                     pack_vector('d', content) )
        else:
            # error
            pass

    #matrix
    elif type == 'M':
        rsize = content.shape[0]
        return ( struct.pack('<cI', b'M', rsize) +
                 pack('V', content) )

    # pickle
    elif type == 'P':
        #print('content = {}'.format(content))
        try:
            bmessage = pickle.dumps(content)
        except pickle.PicklingError:
            # try wrapping in list
            bmessage = pickle.dumps(list(content))
        return struct.pack('<cI', b'P', len(bmessage)) + bmessage

    # pickle (Exception)
    elif type == 'E':
        bmessage = pickle.dumps(content)
        return struct.pack('<cI', b'E', len(bmessage)) + bmessage

    # pickle (kwargs)
    elif type == 'K':
        bmessage = pickle.dumps(content)
        return struct.pack('<cI', b'K', len(bmessage)) + bmessage

    # pickle (vargs)
    elif type == 'R':
        bmessage = pickle.dumps(content)
        return struct.pack('<cI', b'R', len(bmessage)) + bmessage

    else:
        raise NameError('Unknown type')
