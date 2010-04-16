#
# Copyright (c) 2002, 2004 Art Haas
#
# This file is part of PythonCAD.
# 
# PythonCAD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# PythonCAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# handle possibly compressed files
#

import time
import struct
import zlib
import sys
import os

class CompFile(file):
    """A class for transparently handling compressed files.

The CompFile class is a wrapper around the file object. It
is similar to Python's GzipFile class in gzip.py, but the
implementation takes advantage of features found in Python 2.2.

A CompFile object has the attributes and methods of a file
object, except a CompFile object cannot truncate a compressed
file.

It may be possible to add zipfile reading/writing capabilities
to the CompFile class in the future.
    """
    def __init__(self, filename, mode="r", buffering=0, truename=None):
        if sys.platform == 'win32' and 'b' not in mode:
            mode += 'b'
        super(CompFile, self).__init__(filename, mode, buffering)
        self.__size = 0
        self.__crc = zlib.crc32('')
        self.__compobj = None
        self.__offset = 0L
        self.__buffer = ''
        if mode == "r" or mode == "rb":
            magic = super(CompFile, self).read(2)
            if magic == '\037\213': # gzip/zlib file
                method = ord(super(CompFile, self).read(1))
                if method != 8:
                    raise IOError, "Unknown compression method"
                flags = ord(super(CompFile, self).read(1))
                data = super(CompFile, self).read(6) # skip mod time, extra flags, os
                if flags & 2: # file has FHCRC
                    self.__compobj = zlib.decompressobj()
                else:
                    self.__compobj = zlib.decompressobj(-zlib.MAX_WBITS)
                if flags & 4: # FEXTRA
                    xlen = ord(super(CompFile, self).read(1))
                    xlen = xlen + 256*ord(super(CompFile, self).read(1))
                    data = super(CompFile, self).read(xlen)
                if flags & 8: # FNAME
                    while 1:
                        data = super(CompFile, self).read(1)
                        if not data or data == '\000':
                            break
                if flags & 16: # FCOMMENT
                    while 1:
                        data = super(CompFile, self).read(1)
                        if not data or data == '\000':
                            break
            else:
                super(CompFile, self).seek(0, 0)
        elif mode == "w" or mode == "wb":
            #
            # the following generates files that aren't
            # compatible with current gzip ...
            #
            # self.__compobj = zlib.compressobj()
            #
            # create a gzip-compatible compressobj ...
            self.__compobj = zlib.compressobj(6,
                                              zlib.DEFLATED,
                                              -zlib.MAX_WBITS,
                                              zlib.DEF_MEM_LEVEL,
                                              0)
            super(CompFile, self).write('\037\213\010')
            super(CompFile, self).write(chr(8)) # flags FNAME - no FHCRC for gzip compat.
            super(CompFile, self).write(struct.pack("<L", long(time.time())))
            super(CompFile, self).write('\000\377') # extra flags and unknown OS flag
            if truename is not None:
                _fname = truename
            else:
                _fname = os.path.basename(filename)
                if _fname.endswith('.gz'):
                    _fname = _fname[:-3]
            super(CompFile, self).write(_fname + '\000')

    def __del__(self):
        super(CompFile, self).close()
        
    def read(self, size=-1):
        if self.__compobj is None:
            data = super(CompFile, self).read(size)
        elif size < 0:
            buf = super(CompFile, self).read(size)
            self.__crc = zlib.crc32(buf, self.__crc)
            data = self.__buffer + self.__compobj.decompress(buf)
            data = data + self.__compobj.flush()
            self.__buffer = ''
        elif size < len(self.__buffer):
            data = self.__buffer[:size]
            self.__buffer = self.__buffer[size:]
        else:
            buf = super(CompFile, self).read(size)
            while buf != '':
                self.__crc = zlib.crc32(buf, self.__crc)
                new_data = self.__compobj.decompress(buf)
                self.__buffer = self.__buffer + new_data
                if len(self.__buffer) > size:
                    break
                buf = super(CompFile, self).read(size)
            self.__offset = len(self.__buffer)
            if self.__offset > size:
                data = self.__buffer[:size]
                self.__buffer = self.__buffer[size:]
            else:
                data = self.__buffer[:]
                self.__buffer = ''
        return data

    def readline(self, size=-1):
        if size > 0:
            data = self.read(size)
        elif self.__compobj is None:
            data = super(CompFile, self).readline(size)
        elif self.__buffer.find("\n") != -1:
            idx = self.__buffer.find("\n") + 1
            data = self.__buffer[:idx]
            self.__buffer = self.__buffer[idx:]
        else:
            buf = self.read(100)
            offset = buf.find("\n")
            while offset < 0:
                new_buf = self.read(100)
                if new_buf == '': # EOF
                    break
                buf = buf + new_buf
                offset = buf.find("\n")
            if offset != -1:
                offset = offset + 1 # add in the newline character
                data = buf[:offset]
                self.__buffer = buf[offset:] + self.__buffer
            else:
                data = buf[:]
                self.__buffer = ''
        return data

    def readlines(self, size=0):
        if size <= 0:
            size = sys.maxint
        lines = []
        while size > 0:
            line = self.readline()
            if line == '':
                break
            lines.append(line)
            size = size - len(line)
        return lines
    
    def write(self, data):
        if len(data):
            self.__crc = zlib.crc32(data, self.__crc)
            self.__size = self.__size + len(data)
            super(CompFile, self).write(self.__compobj.compress(data))

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        if self.__compobj is not None:
            super(CompFile, self).write(self.__compobj.flush())
        super(CompFile, self).flush()
        
    def close(self):
        mode = self.mode
        if mode == "w" or mode == "wb":
            super(CompFile, self).write(self.__compobj.flush())
            super(CompFile, self).write(struct.pack("<l", self.__crc))
            super(CompFile, self).write(struct.pack("<l", self.__size))
        super(CompFile, self).close()

    def seek(self, offset, whence=0):
        if self.__compobj is None:
            super(CompFile, self).seek(offset, whence)        
        elif self.mode == "r" or self.mode == "rb":
            if whence == 0: # from start
                super(CompFile, self).seek(0, 0)
                self.__buffer = ''
                magic = super(CompFile, self).read(2)
                if magic != '\037\213':
                    raise ValueError, "Invalid gzip file magic value!"
                method = ord(super(CompFile, self).read(1))
                if method != 8:
                    raise IOError, "Unknown compression method"
                flags = ord(super(CompFile, self).read(1))
                data = super(CompFile, self).read(6) # skip mod time, extra flags, os
                if flags & 2: # file has FHCRC
                    self.__compobj = zlib.decompressobj()
                else:
                    self.__compobj = zlib.decompressobj(-zlib.MAX_WBITS)
                if flags & 4: # FEXTRA
                    xlen = ord(super(CompFile, self).read(1))
                    xlen = xlen + 256*ord(super(CompFile, self).read(1))
                    data = super(CompFile, self).read(xlen)
                if flags & 8: # FNAME
                    while 1:
                        data = super(CompFile, self).read(1)
                        if not data or data == '\000':
                            break
                if flags & 16: # FCOMMENT
                    while 1:
                        data = super(CompFile, self).read(1)
                        if not data or data == '\000':
                            break
                if offset > 0:
                    data = self.read(offset)
            elif whence == 1: # current position
                if offset < 0:
                    self.seek(0,0)
                    new_offset = self.__offset + offset
                    if new_offset > 0:
                        self.read(new_offset)
                elif offset > 0:
                    self.read(offset)
            elif whence == 2: # from end
                buf = ''
                self.seek(0,0)
                data = self.read(4096)
                while data != '':
                    buf = buf + data
                    if len(buf) > offset:
                        idx = 1 - offset
                        buf = buf[-idx:]
                    data = self.read(4096)
                if len(buf) > offset:
                    self.__buffer = buf[offset:]
                else:
                    raise ValueError, "Offset %d larger than filesize" % offset
            else:
                raise ValueError, "Invalid seek position: %d" % whence
        else:
            raise IOError, "Unable to seek on writing."

    def truncate(self, size=None):
        if self.__compobj is not None:
            raise StandardError, "Cannot truncate compressed files."
        if size is None:
            size = super(CompFile, self).tell()
        super(CompFile, self).truncate(size)
