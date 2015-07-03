import sys
sys.path.append('..')

import struct
import numpy
import io
import pickle

import Packet

def testA():

    # test A
    assert Packet.pack('A','C') == b'AC'
    assert Packet.pack('A','B') == b'AB'
    assert Packet.pack('A','C') != b'AB'

    assert Packet.unpack_stream(io.BytesIO(b'AC')) == ('A', 'C')
    assert Packet.unpack_stream(io.BytesIO(b'AB')) == ('A', 'B')
    assert Packet.unpack_stream(io.BytesIO(b'AB')) != ('A', 'C')

def testC():

    # test C
    assert Packet.pack('C','C') == b'CC'
    assert Packet.pack('C','B') == b'CB'
    assert Packet.pack('C','C') != b'CB'

    assert Packet.unpack_stream(io.BytesIO(b'CC')) == ('C', 'C')
    assert Packet.unpack_stream(io.BytesIO(b'CB')) == ('C', 'B')
    assert Packet.unpack_stream(io.BytesIO(b'CB')) != ('C', 'C')

def testS():

    # test S
    assert Packet.pack('S','abc') == struct.pack('<cI3s', b'S', 3, b'abc')
    assert Packet.pack('S','abcd') != struct.pack('<cI3s', b'S', 3, b'abc')

    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<cI3s', b'S', 3, b'abc'))) == ('S', 'abc')

    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<cI3s', b'S', 3, b'abc'))) != ('S', 'abcd')

def testIFD():

    # test I
    assert Packet.pack('I',3) == struct.pack('<ci', b'I', 3)
    assert Packet.pack('I',3) != struct.pack('<ci', b'I', 4)

    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<ci', b'I', 3))) == ('I', 3)
    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<ci', b'I', 4))) != ('I', 3)

    # test F
    assert Packet.pack('F',3.3) == struct.pack('<cf', b'F', 3.3)
    assert Packet.pack('F',3.3) != struct.pack('<cf', b'F', 4.3)

    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<cf', b'F', numpy.float32(3.3)))) == ('F', numpy.float32(3.3))
    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<cf', b'F', 4.3))) != ('F', 3.3)

    # test D
    assert Packet.pack('D',3.3) == struct.pack('<cd', b'D', 3.3)
    assert Packet.pack('D',3.3) != struct.pack('<cd', b'D', 4.3)

    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<cd', b'D', 3.3))) == ('D', 3.3)
    assert Packet.unpack_stream(
        io.BytesIO(struct.pack('<cd', b'D', 4.3))) != ('D', 3.3)

def testV():

    # test VI
    vector = numpy.array((1,2,3), int)
    assert Packet.pack('V',vector) == struct.pack('<ccIiii', b'V', b'I', 3, 1, 2, 3)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIiii', b'V', b'I', 3, 1, 2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

    vector = numpy.array((1,-2,3), int)
    assert Packet.pack('V',vector) == struct.pack('<ccIiii', b'V', b'I', 3, 1, -2, 3)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIiii', b'V', b'I', 3, 1, -2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

    # test VF
    vector = numpy.array((1.3,-2,3), numpy.float32)
    assert Packet.pack('V',vector) == struct.pack('<ccIfff', b'V', b'F', 3, 1.3, -2, 3)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIfff', b'V', b'F', 3, 1.3, -2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

    # test VD
    vector = numpy.array((1.3,-2,3), float)
    assert Packet.pack('V',vector) == struct.pack('<ccIddd', b'V', b'D', 3, 1.3, -2, 3)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<ccIddd', b'V', b'D', 3, 1.3, -2, 3)))
    assert type == 'V'
    assert numpy.all(rvector == vector)

def testM():

    # test MI
    vector = numpy.array(((1,2,3), (3,4,5)), int)
    assert Packet.pack('M',vector) == struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, 2, 3, 3, 4, 5)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, 2, 3, 3, 4, 5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

    vector = numpy.array(((1,-2,3), (3,4,-5)), int)
    assert Packet.pack('M',vector) == struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, -2, 3, 3, 4, -5)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIiiiiii', b'M', 2, b'V', b'I', 6, 1, -2, 3, 3, 4, -5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

    # test MF
    vector = numpy.array(((1.3,-2,3), (0,-1,2.5)), numpy.float32)
    assert Packet.pack('M',vector) == struct.pack('<cIccIffffff', b'M', 2, b'V', b'F', 6, 1.3, -2, 3, 0, -1, 2.5)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIffffff', b'M', 2, b'V', b'F', 6, 1.3, -2, 3, 0, -1, 2.5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

    # test MD
    vector = numpy.array(((1.3,-2,3), (0,-1,2.5)), numpy.float)
    assert Packet.pack('M',vector) == struct.pack('<cIccIdddddd', b'M', 2, b'V', b'D', 6, 1.3, -2, 3, 0, -1, 2.5)

    (type, rvector) = Packet.unpack_stream(
        io.BytesIO(struct.pack('<cIccIdddddd', b'M', 2, b'V', b'D', 6, 1.3, -2, 3, 0, -1, 2.5)))
    assert type == 'M'
    assert numpy.all(rvector == vector)

def testP():

    vector = numpy.array(((1.3,-2,3), (0,-1,2.5)), numpy.float)
    string = Packet.pack('P', vector)
    (type, rvector) = Packet.unpack_stream(io.BytesIO(string))
    assert type == 'P'
    assert numpy.all(rvector == vector)

if __name__ == "__main__":

    testP()

