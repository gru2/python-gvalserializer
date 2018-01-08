import gvalserializer
import unittest
import numpy as np

class TestFileBinaryStream(unittest.TestCase):

    def testOpenClose(self):
        s = gvalserializer.FileBinaryStream()
        s.open("pera.bin", "wb")
        s.close()
        s.open("pera.bin", "rb")
        s.close()

    def testWriteRead(self):
        s = gvalserializer.FileBinaryStream()
        s.open("pera.bin", "wb")
        s.writeByte(255)
        s.writeInt(-1)
        s.writeFloat(1.5)
        s.writeDouble(-2.25)
        s.writeString("foobar")
        s.close()
        s.open("pera.bin", "rb")
        self.assertEqual(s.readByte(), 255)
        self.assertEqual(s.readInt(), -1)
        self.assertEqual(s.readFloat(), 1.5)
        self.assertEqual(s.readDouble(), -2.25)
        self.assertEqual(s.readString(), "foobar")
        s.close()


class TestGValSerializer(unittest.TestCase):

    def testGValSerializer(self):
        a0 = np.array([1.0, 2.5, -4.25])
        a1 = np.array([[1.0, 2.5, 1.5], [2.0, 3.0, -5.5]], dtype=np.float32)
        fbs = gvalserializer.FileBinaryStream()
        fbs.open("pera.bin", "wb")
        gvs = gvalserializer.GValSerializer()
        gvs.binaryStream = fbs
        gvs.write(None)
        gvs.write(True)
        gvs.write(False)
        gvs.write(34)
        gvs.write(23.25)
        gvs.write("foobar")
        gvs.write([100, 301, "Pera"])
        gvs.write({"foo": 4, "bar": "baz"})
        gvs.write(a0)
        gvs.write(a1)
        fbs.close()
        fbs.open("pera.bin", "rb")
        self.assertEqual(gvs.read(), None)
        self.assertEqual(gvs.read(), True)
        self.assertEqual(gvs.read(), False)
        self.assertEqual(gvs.read(), 34)
        self.assertEqual(gvs.read(), 23.25)
        self.assertEqual(gvs.read(), "foobar")
        self.assertEqual(gvs.read(), [100, 301, "Pera"])
        self.assertEqual(gvs.read(), {"foo": 4, "bar": "baz"})
        self.assertTrue(np.array_equal(gvs.read(), a0))
        self.assertTrue(np.array_equal(gvs.read(), a1))
        fbs.close()


if __name__ == '__main__':
    unittest.main()
