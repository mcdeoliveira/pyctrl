import struct
import numpy
import io
import pickle

import pyctrl.packet as packet

def testA():

    # test A
    assert packet.pack('A','C') == b'AC'
    assert packet.pack('A','B') == b'AB'
    assert packet.pack('A','C') != b'AB'

    assert packet.unpack_stream(io.BytesIO(b'AC')) == ('A', 'C')
    assert packet.unpack_stream(io.BytesIO(b'AB')) == ('A', 'B')
    assert packet.unpack_stream(io.BytesIO(b'AB')) != ('A', 'C')

def testC():

    # test C
    assert packet.pack('C','C') == b'CC'
    assert packet.pack('C','B') == b'CB'
    assert packet.pack('C','C') != b'CB'

    assert packet.unpack_stream(io.BytesIO(b'CC')) == ('C', 'C')
    assert packet.unpack_stream(io.BytesIO(b'CB')) == ('C', 'B')
    assert packet.unpack_stream(io.BytesIO(b'CB')) != ('C', 'C')

def testS():

    # test S
    assert packet.pack('S','abc') == struct.pack('<cI3s', b'S', 3, b'abc')
    assert packet.pack('S','abcd') != struct.pack('<cI3s', b'S', 3, b'abc')

    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<cI3s', b'S', 3, b'abc'))) == ('S', 'abc')

    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<cI3s', b'S', 3, b'abc'))) != ('S', 'abcd')

def testIFD():

    # test I
    assert packet.pack('I',3) == struct.pack('<ci', b'I', 3)
    assert packet.pack('I',3) != struct.pack('<ci', b'I', 4)

    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<ci', b'I', 3))) == ('I', 3)
    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<ci', b'I', 4))) != ('I', 3)

    # test F
    assert packet.pack('F',3.3) == struct.pack('<cf', b'F', 3.3)
    assert packet.pack('F',3.3) != struct.pack('<cf', b'F', 4.3)

    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<cf', b'F', numpy.float32(3.3)))) == ('F', numpy.float32(3.3))
    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<cf', b'F', 4.3))) != ('F', 3.3)

    # test D
    assert packet.pack('D',3.3) == struct.pack('<cd', b'D', 3.3)
    assert packet.pack('D',3.3) != struct.pack('<cd', b'D', 4.3)

    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<cd', b'D', 3.3))) == ('D', 3.3)
    assert packet.unpack_stream(
        io.BytesIO(struct.pack('<cd', b'D', 4.3))) != ('D', 3.3)

def testV():

    # test VI
    vector = numpy.array((1,2,3), int)
    assert packet.pack('V',vector) == struct.pack('<ccIiii', b'V', b'I', 3, 1, 2, 3)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIiii', b'V', b'I', 3, 1, 2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

    vector = numpy.array((1,-2,3), int)
    assert packet.pack('V',vector) == struct.pack('<ccIiii', b'V', b'I', 3, 1, -2, 3)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIiii', b'V', b'I', 3, 1, -2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

    # test VF
    vector = numpy.array((1.3,-2,3), numpy.float32)
    assert packet.pack('V',vector) == struct.pack('<ccIfff', b'V', b'F', 3, 1.3, -2, 3)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIfff', b'V', b'F', 3, 1.3, -2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

    # test VD
    vector = numpy.array((1.3,-2,3), float)
    assert packet.pack('V',vector) == struct.pack('<ccIddd', b'V', b'D', 3, 1.3, -2, 3)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIddd', b'V', b'D', 3, 1.3, -2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

def testM():

    # test MI
    vector = numpy.array(((1,2,3), (3,4,5)), int)
    assert packet.pack('M',vector) == struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, 2, 3, 3, 4, 5)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, 2, 3, 3, 4, 5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

    vector = numpy.array(((1,-2,3), (3,4,-5)), int)
    assert packet.pack('M',vector) == struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, -2, 3, 3, 4, -5)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, -2, 3, 3, 4, -5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

    # test MF
    vector = numpy.array(((1.3,-2,3), (0,-1,2.5)), numpy.float32)
    assert packet.pack('M',vector) == struct.pack('<cIccIffffff', b'M', 2, b'V', b'F', 6, 1.3, -2, 3, 0, -1, 2.5)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIffffff', b'M', 2, b'V', b'F', 6, 1.3, -2, 3, 0, -1, 2.5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

    # test MD
    vector = numpy.array(((1.3,-2,3), (0,-1,2.5)), numpy.float)
    assert packet.pack('M',vector) == struct.pack('<cIccIdddddd', b'M', 2, b'V', b'D', 6, 1.3, -2, 3, 0, -1, 2.5)

    (type, rvector) = packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIdddddd', b'M', 2, b'V', b'D', 6, 1.3, -2, 3, 0, -1, 2.5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

def testP():

    vector = numpy.array(((1.3,-2,3), (0,-1,2.5)), numpy.float)
    string = packet.pack('P', vector)
    (type, rvector) = packet.unpack_stream(io.BytesIO(string))
    assert type == 'P'
    assert numpy.all(rvector == vector)

def testKR():

    args = { 'a': 1, 'b': 2 }
    string = packet.pack('K', args)
    (type, rargs) = packet.unpack_stream(io.BytesIO(string))
    assert type == 'K'
    assert (args == rargs)

    args = ('a', 1, 'b', 2)
    string = packet.pack('R', args)
    (type, rargs) = packet.unpack_stream(io.BytesIO(string))
    assert type == 'R'
    assert (args == rargs)

if __name__ == "__main__":

    testA()
    testC()
    testS()
    testIFD()
    testV()
    testM()
    testP()
    testKR()

