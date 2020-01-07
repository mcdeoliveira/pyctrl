import struct
import numpy
import pickle

debug_level = 3


def unpack_stream(stream):
    if debug_level > 0:
        print('> packet: waiting for next character')
    buffer = stream.read(1)
    if not buffer:
        raise NameError('read failed')
    (btype,) = struct.unpack('1s', buffer)

    if debug_level > 0:
        print("> packet: got '{}'".format(btype))

    if btype == b'A' or btype == b'C':
        # Read next character
        buffer = stream.read(1)
        (command,) = struct.unpack('1s', buffer)
        return str(btype, 'utf-8'), str(command, 'utf-8')

    elif btype == b'S':
        # Read length (int)
        buffer = stream.read(4)
        (blen,) = struct.unpack('<I', buffer)
        # Read string (blen*char)
        buffer = stream.read(blen)
        (bmessage,) = struct.unpack('%ds' % (blen,), buffer)
        return 'S', str(bmessage, 'utf-8')

    elif btype == b'I':
        # Read int
        buffer = stream.read(4)
        (i,) = struct.unpack('<i', buffer)
        return 'I', i

    elif btype == b'F':
        # Read float
        buffer = stream.read(4)
        (f,) = struct.unpack('<f', buffer)
        return 'F', f

    elif btype == b'D':
        # Read double
        buffer = stream.read(8)
        (d,) = struct.unpack('<d', buffer)
        return 'D', d

    elif btype == b'V':
        # Read type (char)
        buffer = stream.read(1)
        (vtype,) = struct.unpack('1s', buffer)
        # Read length (int)
        buffer = stream.read(4)
        (vlen,) = struct.unpack('<I', buffer)
        # Read data (blen*)
        if debug_level > 0:
            print("> packet::vector: '{}[{}]'".format(vtype, vlen))
        if vtype == b'H':
            vector = numpy.array(struct.unpack('<%dh' % (vlen, ), stream.read(2 * vlen)), dtype=numpy.int16)
        elif vtype == b'I':
            vector = numpy.array(struct.unpack('<%di' % (vlen, ), stream.read(4 * vlen)), dtype=numpy.int32)
        elif vtype == b'F':
            vector = numpy.array(struct.unpack('<%df' % (vlen, ), stream.read(4 * vlen)), dtype=numpy.float32)
        elif vtype == b'D':
            vector = numpy.array(struct.unpack('<%dd' % (vlen, ), stream.read(8 * vlen)), dtype=numpy.float64)
        else:
            # error
            raise Exception("Unkown vector type")

        # return vector
        return 'V', vector

    elif btype == b'M':
        # Read row size (int)
        buffer = stream.read(4)
        (rsize,) = struct.unpack('<I', buffer)
        # read vector
        (vtype, vector) = unpack_stream(stream)
        # reshape vector as matrix
        vector = vector.reshape((rsize, int(numpy.size(vector) / rsize)))
        # return vector
        return 'M', vector

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
            return 'P', object
        elif btype == b'E':
            return 'E', object
        elif btype == b'K':
            return 'K', object
        else:  # btype == b'R':
            return 'R', object

    else:
        raise NameError('Unknown type')


def pack_vector(type, content):
    buffer = b''
    type = '<' + type
    shape = numpy.shape(content)
    if len(shape) > 1:
        # matrix
        for k in range(shape[0]):
            for value in content[k, :]:
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
        return struct.pack('2s', b'A' + bmessage)

    elif type == 'C':
        bmessage = bytes(content[0], 'utf-8')
        return struct.pack('2s', b'C' + bmessage)

    # message
    elif type == 'S':
        bmessage = bytes(content, 'utf-8')
        blen = len(bmessage)
        return struct.pack('<1sI%ds' % (blen,),
                           b'S',
                           blen,
                           bmessage)

    # integer
    elif type == 'I':
        return struct.pack('<1si', b'I', content)

    # float
    elif type == 'F':
        return struct.pack('<1sf', b'F', content)

    # double
    elif type == 'D':
        return struct.pack('<1sd', b'D', content)

    # vector
    elif type == 'V':
        vlen = numpy.size(content)
        if numpy.issubsctype(content, numpy.int16):
            return (struct.pack('<2sI', b'VH', vlen) +
                    pack_vector('h', content))
        elif numpy.issubsctype(content, numpy.int32):
            return (struct.pack('<2sI', b'VI', vlen) +
                    pack_vector('i', content))
        elif numpy.issubsctype(content, numpy.float32):
            return (struct.pack('<2sI', b'VF', vlen) +
                    pack_vector('f', content))
        elif numpy.issubsctype(content, numpy.float64):
            return (struct.pack('<2sI', b'VD', vlen) +
                    pack_vector('d', content))
        else:
            # error
            raise Exception("Unkown vector type")

    # matrix
    elif type == 'M':
        rsize, _ = numpy.shape(content)
        return (struct.pack('<1sI', b'M', rsize) +
                pack('V', content))

    # pickle
    elif type == 'P':
        # print('content = {}'.format(content))
        try:
            bmessage = pickle.dumps(content)
        except pickle.PicklingError:
            # try wrapping in list
            bmessage = pickle.dumps(list(content))
        except:
            print('*** PACKET FAILED TO PICKLE ***')
            print('content = {}'.format(content))
            bmessage = pickle.dumps()
        return struct.pack('<1sI', b'P', len(bmessage)) + bmessage

    # pickle (Exception)
    elif type == 'E':
        try:
            bmessage = pickle.dumps(content)
        except:
            print('*** PACKET FAILED TO PICKLE ***')
            print('content = {}'.format(content))
        return struct.pack('<1sI', b'E', len(bmessage)) + bmessage

    # pickle (kwargs)
    elif type == 'K':
        try:
            bmessage = pickle.dumps(content)
        except:
            print('*** PACKET FAILED TO PICKLE ***')
            print('content = {}'.format(content))
            bmessage = pickle.dumps({})
        return struct.pack('<1sI', b'K', len(bmessage)) + bmessage

    # pickle (vargs)
    elif type == 'R':
        bmessage = pickle.dumps(content)
        return struct.pack('<1sI', b'R', len(bmessage)) + bmessage

    else:
        raise NameError('Unknown type')
