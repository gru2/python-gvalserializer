import numpy as np
import struct


class FileBinaryStream:

    def __init__(self):
        self.file = None

    def open(self, fileName, mode):
        self.file = open(fileName, mode)

    def close(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def _read(self, fmt):
        sz = struct.calcsize(fmt)
        return struct.unpack(fmt, self.file.read(sz))[0]

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
        return self.file.read(len).decode("ascii")

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
        self.file.write(x.encode("ascii"))


GVT_NULL = 0
GVT_BOOL = 1
GVT_INT = 2
GVT_LONG = 3
GVT_FLOAT = 4
GVT_DOUBLE = 5
GVT_STRING = 6
GVT_MULTI_ARRAY = 7
GVT_MAP = 8
GVT_GENERIC = 9


class GValSerializer:

    def __init__(self):
        self.binaryStream = None

    def write(self, x):
        if x is None:
            self.binaryStream.writeInt(GVT_NULL)
            return
        if type(x) is bool:
            self.binaryStream.writeInt(GVT_BOOL)
            self.binaryStream.writeByte(int(x))
            return
        if type(x) is int:
            self.binaryStream.writeInt(GVT_INT)
            self.binaryStream.writeInt(x)
            return
        if type(x) is float:
            self.binaryStream.writeInt(GVT_DOUBLE)
            self.binaryStream.writeDouble(x)
            return
        if type(x) is str:
            self.binaryStream.writeInt(GVT_STRING)
            self.binaryStream.writeString(x)
            return
        if type(x) is list:
            self.binaryStream.writeInt(GVT_MULTI_ARRAY)
            self.binaryStream.writeInt(GVT_GENERIC)
            self.binaryStream.writeInt(1)
            self.binaryStream.writeInt(len(x))
            for y in x:
                self.write(y)
            return
        if type(x) is dict:
            self.binaryStream.writeInt(GVT_MAP)
            self.binaryStream.writeInt(len(x))
            for k in x:
                self.write(k)
                self.write(x[k])
            return
        if type(x) == np.ndarray:
            self.binaryStream.writeInt(GVT_MULTI_ARRAY)
            nDims = len(x.shape)
            nElems = x.size
            xt = x.reshape(nElems)
            if x.dtype == np.float64:
                self.binaryStream.writeInt(GVT_DOUBLE)
                self.binaryStream.writeInt(nDims)
                for dim in x.shape:
                    self.binaryStream.writeInt(dim)
                for i in range(nElems):
                    self.binaryStream.writeDouble(xt[i])
                return
            if x.dtype == np.float32:
                self.binaryStream.writeInt(GVT_FLOAT)
                self.binaryStream.writeInt(nDims)
                for dim in x.shape:
                    self.binaryStream.writeInt(dim)
                for i in range(nElems):
                    self.binaryStream.writeFloat(xt[i])
                return
            if x.dtype == np.int32:
                self.binaryStream.writeInt(GVT_INT)
                self.binaryStream.writeInt(nDims)
                for dim in x.shape:
                    self.binaryStream.writeInt(dim)
                for i in range(nElems):
                    self.binaryStream.writeInt(xt[i])
                return
        self.error("uanble to wirte object")

    def read(self):
        t = self.binaryStream.readInt()
        if t == GVT_NULL:
            return None
        if t == GVT_BOOL:
            return bool(self.binaryStream.readByte())
        if t == GVT_INT:
            return self.binaryStream.readInt()
        if t == GVT_FLOAT:
            return self.binaryStream.readFloat()
        if t == GVT_DOUBLE:
            return self.binaryStream.readDouble()
        if t == GVT_STRING:
            return self.binaryStream.readString()
        if t == GVT_MULTI_ARRAY:
            et = self.binaryStream.readInt()
            nDims = self.binaryStream.readInt()
            if et == GVT_GENERIC:
                if nDims != 1:
                    self.error("unable to load multidimensional Generic.")
                    return None
                nElems = self.binaryStream.readInt()
                x = []
                for i in range(nElems):
                    x.append(self.read())
                return x
            shape = []
            for i in range(nDims):
                shape.append(self.binaryStream.readInt())
            nElems = 1
            for i in shape:
                nElems *= i
            if et == GVT_DOUBLE:
                x = np.zeros(nElems, np.float64)
                for i in range(nElems):
                    x[i] = self.binaryStream.readDouble()
                return x.reshape(shape)
            if et == GVT_FLOAT:
                x = np.zeros(nElems, np.float32)
                for i in range(nElems):
                    x[i] = self.binaryStream.readFloat()
                return x.reshape(shape)
            if et == GVT_INT:
                x = np.zeros(nElems, np.int32)
                for i in range(nElems):
                    x[i] = self.binaryStream.readInt()
                return x.reshape(shape)
            self.error("unable to read multiarray")
            return None
        if t == GVT_MAP:
            nElems = self.binaryStream.readInt()
            x = {}
            for i in range(nElems):
                k = self.read()
                v = self.read()
                x[k] = v
            return x
        self.error("uanble to read object")
        return None

    def error(self, msg):
        print("error:", msg)
        exit(1)
