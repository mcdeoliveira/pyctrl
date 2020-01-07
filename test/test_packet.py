import unittest

import struct
import numpy
import io
import pickle
import pyctrl.packet as packet


class TestUnittestAssertions(unittest.TestCase):

    def testA(self):
        # test A
        self.assertEqual(packet.pack('A', 'C'), b'AC')
        self.assertEqual(packet.pack('A', 'B'), b'AB')
        self.assertNotEqual(packet.pack('A', 'C'), b'AB')

        self.assertEqual(packet.unpack_stream(io.BytesIO(b'AC')), ('A', 'C'))
        self.assertEqual(packet.unpack_stream(io.BytesIO(b'AB')), ('A', 'B'))
        self.assertNotEqual(packet.unpack_stream(io.BytesIO(b'AB')), ('A', 'C'))

    def testC(self):
        # test C
        self.assertEqual(packet.pack('C', 'C'), b'CC')
        self.assertEqual(packet.pack('C', 'B'), b'CB')
        self.assertNotEqual(packet.pack('C', 'C'), b'CB')

        self.assertEqual(packet.unpack_stream(io.BytesIO(b'CC')), ('C', 'C'))
        self.assertEqual(packet.unpack_stream(io.BytesIO(b'CB')), ('C', 'B'))
        self.assertNotEqual(packet.unpack_stream(io.BytesIO(b'CB')), ('C', 'C'))

    def testS(self):
        # test S
        self.assertEqual(packet.pack('S', 'abc'), struct.pack('<1sI3s', b'S', 3, b'abc'))
        self.assertNotEqual(packet.pack('S', 'abcd'), struct.pack('<1sI3s', b'S', 3, b'abc'))

        self.assertEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1sI3s', b'S', 3, b'abc'))), ('S', 'abc'))
        self.assertNotEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1sI3s', b'S', 3, b'abc'))), ('S', 'abcd'))

    def testIFD(self):
        # test I
        self.assertEqual(packet.pack('I', 3), struct.pack('<1si', b'I', 3))
        self.assertNotEqual(packet.pack('I', 3), struct.pack('<1si', b'I', 4))

        self.assertEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1si', b'I', 3))), ('I', 3))
        self.assertNotEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1si', b'I', 4))), ('I', 3))

        # test F
        self.assertEqual(packet.pack('F', 3.3), struct.pack('<1sf', b'F', 3.3))
        self.assertNotEqual(packet.pack('F', 3.3), struct.pack('<1sf', b'F', 4.3))

        ff, = struct.unpack('f', struct.pack('f', 3.3))
        self.assertEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1sf', b'F', ff))), ('F', ff))
        self.assertNotEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1sf', b'F', ff + 1))), ('F', ff))

        # test D
        self.assertEqual(packet.pack('D', 3.3), struct.pack('<1sd', b'D', 3.3))
        self.assertNotEqual(packet.pack('D', 3.3), struct.pack('<1sd', b'D', 4.3))

        dd, = struct.unpack('d', struct.pack('d', 3.3))
        self.assertEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1sd', b'D', 3.3))), ('D', dd))
        self.assertNotEqual(packet.unpack_stream(io.BytesIO(struct.pack('<1sd', b'D', 4.3))), ('D', dd))

    def testV(self):
        # test VH
        vector = numpy.array((1, 2, 3), dtype=numpy.int16)
        self.assertTrue(packet.pack('V', vector) == struct.pack('<2sI3h', b'VH', 3, 1, 2, 3))

        (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<2sI3h', b'VH', 3, 1, 2, 3)))
        self.assertTrue(type == 'V')
        self.assertTrue(numpy.array_equal(rvector, vector))

        vector = numpy.array((1, -2, 3), dtype=numpy.int16)
        self.assertTrue(packet.pack('V', vector) == struct.pack('<2sI3h', b'VH', 3, 1, -2, 3))

        (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<2sI3h', b'VH', 3, 1, -2, 3)))
        self.assertTrue(type == 'V')
        self.assertTrue(numpy.array_equal(rvector, vector))

        # test VI
        try:
            vector = numpy.array((1, 2, 3), dtype=numpy.int32)
            self.assertTrue(packet.pack('V', vector) == struct.pack('<2sI3i', b'VI', 3, 1, 2, 3))

            (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<2sI3i', b'VI', 3, 1, 2, 3)))
            self.assertTrue(type == 'V')
            self.assertTrue(numpy.array_equal(rvector, vector))

            vector = numpy.array((1, -2, 3), dtype=numpy.int32)
            self.assertTrue(packet.pack('V', vector) == struct.pack('<2sI3i', b'VI', 3, 1, -2, 3))

            (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<2sI3i', b'VI', 3, 1, -2, 3)))
            self.assertTrue(type == 'V')
            self.assertTrue(numpy.array_equal(rvector, vector))
        except TypeError:
            print('** INT32 is not supported **')

        # test VF
        try:
            vector = numpy.array((1.3, -2, 3), dtype=numpy.float32)
            self.assertTrue(packet.pack('V', vector) == struct.pack('<2sI3f', b'VF', 3, 1.3, -2, 3))

            (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<2sI3f', b'VF', 3, 1.3, -2, 3)))
            self.assertTrue(type == 'V')
            self.assertTrue(numpy.array_equal(rvector, vector))

        except TypeError:
            print('** FLOAT32 is not supported **')

        # test VD
        try:
            vector = numpy.array((1.3, -2, 3), dtype=numpy.float64)
            self.assertTrue(packet.pack('V', vector) == struct.pack('<2sI3d', b'VD', 3, 1.3, -2, 3))

            (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<2sI3d', b'VD', 3, 1.3, -2, 3)))
            self.assertTrue(type == 'V')
            self.assertTrue(numpy.array_equal(rvector, vector))
        except TypeError:
            print('** FLOAT64 is not supported **')

    def testM(self):

        # test MH
        vector = numpy.array(((1, 2, 3), (3, 4, 5)), dtype=numpy.int16)
        self.assertTrue(packet.pack('M', vector) == struct.pack('<1sI2sI6h', b'M', 2, b'VH', 6, 1, 2, 3, 3, 4, 5))

        (type, rvector) = packet.unpack_stream(io.BytesIO(struct.pack('<1sI2sI6h', b'M', 2, b'VH', 6, 1, 2, 3, 3, 4, 5)))
        self.assertTrue(type == 'M')
        self.assertTrue(numpy.array_equal(rvector, vector))

        vector = numpy.array(((1, -2, 3), (3, 4, -5)), dtype=numpy.int16)
        self.assertTrue(packet.pack('M', vector) == struct.pack('<1sI2sI6h', b'M', 2, b'VH', 6, 1, -2, 3, 3, 4, -5))

        (type, rvector) = packet.unpack_stream(
            io.BytesIO(struct.pack('<1sI2sI6h', b'M', 2, b'VH', 6, 1, -2, 3, 3, 4, -5)))
        self.assertTrue(type == 'M')
        self.assertTrue(numpy.array_equal(rvector, vector))

        # test MI
        try:
            vector = numpy.array(((1, 2, 3), (3, 4, 5)), dtype=numpy.int32)
            self.assertTrue(packet.pack('M', vector) == struct.pack('<1sI2sI6i', b'M', 2, b'VI', 6, 1, 2, 3, 3, 4, 5))

            (type, rvector) = packet.unpack_stream(
                io.BytesIO(struct.pack('<1sI2sI6i', b'M', 2, b'VI', 6, 1, 2, 3, 3, 4, 5)))
            self.assertTrue(type == 'M')
            self.assertTrue(numpy.array_equal(rvector, vector))

            vector = numpy.array(((1, -2, 3), (3, 4, -5)), dtype=numpy.int32)
            self.assertTrue(packet.pack('M', vector) == struct.pack('<1sI2sI6i', b'M', 2, b'VI', 6, 1, -2, 3, 3, 4, -5))

            (type, rvector) = packet.unpack_stream(
                io.BytesIO(struct.pack('<1sI2sI6i', b'M', 2, b'VI', 6, 1, -2, 3, 3, 4, -5)))
            self.assertTrue(type == 'M')
            self.assertTrue(numpy.array_equal(rvector, vector))
        except TypeError:
            print('** INT32 is not supported **')

        # test MF
        try:
            vector = numpy.array(((1.3, -2, 3), (0, -1, 2.5)), dtype=numpy.float32)
            self.assertTrue(packet.pack('M', vector) == struct.pack('<1sI2sI6f', b'M', 2, b'VF', 6, 1.3, -2, 3, 0, -1, 2.5))

            (type, rvector) = packet.unpack_stream(
                io.BytesIO(struct.pack('<1sI2sI6f', b'M', 2, b'VF', 6, 1.3, -2, 3, 0, -1, 2.5)))
            self.assertTrue(type == 'M')
            self.assertTrue(numpy.array_equal(rvector, vector))
        except TypeError:
            print('** FLOAT32 is not supported **')

        # test MD
        try:
            vector = numpy.array(((1.3, -2, 3), (0, -1, 2.5)), dtype=numpy.float64)
            self.assertTrue(packet.pack('M', vector) == struct.pack('<1sI2sI6d', b'M', 2, b'VD', 6, 1.3, -2, 3, 0, -1, 2.5))

            (type, rvector) = packet.unpack_stream(
                io.BytesIO(struct.pack('<1sI2sI6d', b'M', 2, b'VD', 6, 1.3, -2, 3, 0, -1, 2.5)))
            self.assertTrue(type == 'M')
            self.assertTrue(numpy.array_equal(rvector, vector))
        except TypeError:
            print('** FLOAT64 is not supported **')

    def testP(self):
        vector = numpy.array(((1.3, -2, 3), (0, -1, 2.5)), numpy.float64)
        string = packet.pack('P', vector)
        (type, rvector) = packet.unpack_stream(io.BytesIO(string))
        self.assertTrue(type == 'P')
        self.assertTrue(numpy.array_equal(rvector, vector))

    def testKR(self):
        args = {'a': 1, 'b': 2}
        string = packet.pack('K', args)
        (type, rargs) = packet.unpack_stream(io.BytesIO(string))
        self.assertTrue(type == 'K')
        self.assertTrue(args == rargs)

        args = ('a', 1, 'b', 2)
        string = packet.pack('R', args)
        (type, rargs) = packet.unpack_stream(io.BytesIO(string))
        self.assertTrue(type == 'R')
        self.assertTrue(args == rargs)


if __name__ == "__main__":
    unittest.main()
