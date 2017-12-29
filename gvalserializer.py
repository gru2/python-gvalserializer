import numpy
import struct


class FileBinaryStream:

    def __init__(self):
        self.file = None

    def _read(self, fmt):
        sz = struct.calcsize(fmt)
        return struct.unpack(fmt, self.file.read(sz))

    def _write(self, fmt, x):
        s = struct.pack(fmt, x)
        self.file.write(s)

    def readByte(self):
        return self._read("<B")

    def readInt(self):
        return self._read("<i")

    def readFloat(self):
        return self._read("<f")

    def readDouble(self):
        return self._read("<d")

    def readString(self):
        len = self.readInt()
        return self.file.read(len)

    def writeByte(self, x):
        self._write("<B", x)

    def writeInt(self, x):
        self._write("<i", x)

    def writeFloat(self, x):
        self._write("<f", x)

    def writeDouble(self, x):
        self._write("<d", x)

    def writeString(self, x):
        self.writeInt(len(x))
        self.file.write(x)


class GValSerializer:

    def __init__(self):
        self.binaryStream = None


