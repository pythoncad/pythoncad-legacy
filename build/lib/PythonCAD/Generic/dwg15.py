#
# Copyright (c) 2003 Art Haas
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
# read in an AutoCAD R15 DWG file
#

import struct
import array

from PythonCAD.Generic import dwgbase
from PythonCAD.Generic import dwgutil

def initialize_dwg(dwg):
    _handle = dwg.getHandle()
    _handle.seek(0, 0)
    _buf = _handle.read(6)
    if _buf != 'AC1015':
        raise ValueError, "File not R15 DWG format"
    _handle.seek(7, 1) # padding and a revisionbyte
    _offset = struct.unpack('<l', _handle.read(4))[0]
    if _offset != 0:
        dwg.setOffset('IMAGES', (_offset, None))
    _handle.seek(2, 1) # two unknown bytes
    _codepage, _count = struct.unpack('<hl', _handle.read(6))
    for _i in range(_count):
        _rec, _seek, _size = struct.unpack('<Bll', _handle.read(9))
        if _rec == 0: # header
            dwg.setOffset('HEADERS', (_seek, _size))
        elif _rec == 1: # class
            dwg.setOffset('CLASSES', (_seek, _size))
        elif _rec == 2: # object map
            dwg.setOffset('OBJECTS', (_seek, _size))
        elif _rec == 3: # unknown
            dwg.setOffset('UNKNOWN', (_seek, _size))
        elif _rec == 4: # r14 where there may be data stored
            dwg.setOffset('R14DATA', (_seek, _size))
        elif _rec == 5: # occasionally exists
            dwg.setOffset('R14REC5', (_seek, _size))
        else:
            raise ValueError, "Unexpected record number %d" % _rec
    _crc = struct.unpack('<h', _handle.read(2))[0]
    _s = array.array('B')
    _s.fromfile(_handle, 16)
    if _s[0] != 0x95: raise ValueError, "_s[0] != 0x95"
    if _s[1] != 0xa0: raise ValueError, "_s[1] != 0xa0"
    if _s[2] != 0x4e: raise ValueError, "_s[2] != 0x4e"
    if _s[3] != 0x28: raise ValueError, "_s[3] != 0x28"
    if _s[4] != 0x99: raise ValueError, "_s[4] != 0x99"
    if _s[5] != 0x82: raise ValueError, "_s[5] != 0x82"
    if _s[6] != 0x1a: raise ValueError, "_s[6] != 0x1a"
    if _s[7] != 0xe5: raise ValueError, "_s[7] != 0xe5"
    if _s[8] != 0x5e: raise ValueError, "_s[8] != 0x5e"
    if _s[9] != 0x41: raise ValueError, "_s[9] != 0x41"
    if _s[10] != 0xe0: raise ValueError, "_s[10] != 0xe0"
    if _s[11] != 0x5f: raise ValueError, "_s[11] != 0x5f"
    if _s[12] != 0x9d: raise ValueError, "_s[12] != 0x9d"
    if _s[13] != 0x3a: raise ValueError, "_s[13] != 0x3a"
    if _s[14] != 0x4d: raise ValueError, "_s[14] != 0x4d"
    if _s[15] != 0x00: raise ValueError, "_s[15] != 0x00"
    #
    # set the data reading functions
    #
    dwg.setReader('IMAGES', get_images)
    dwg.setReader('HEADERS', get_headers)
    dwg.setReader('CLASSES', get_classes)
    dwg.setReader('OBJECTS', get_objects)
    dwg.setReader('OFFSETS', get_offsets)
    dwg.setReader('OBJECT', get_object)

def get_images(dwg):
    _handle = dwg.getHandle()
    _offset, _size = dwg.getOffset('IMAGES') # size is None
    _handle.seek(_offset, 0)
    _s = array.array('B')
    _s.fromfile(_handle, 16)
    if _s[0] != 0x1f: raise ValueError, "_s[0] != 0x1f"
    if _s[1] != 0x25: raise ValueError, "_s[1] != 0x25"
    if _s[2] != 0x6d: raise ValueError, "_s[2] != 0x6d"
    if _s[3] != 0x07: raise ValueError, "_s[3] != 0x07"
    if _s[4] != 0xd4: raise ValueError, "_s[4] != 0xd4"
    if _s[5] != 0x36: raise ValueError, "_s[5] != 0x36"
    if _s[6] != 0x28: raise ValueError, "_s[6] != 0x28"
    if _s[7] != 0x28: raise ValueError, "_s[7] != 0x28"
    if _s[8] != 0x9d: raise ValueError, "_s[8] != 0x9d"
    if _s[9] != 0x57: raise ValueError, "_s[9] != 0x57"
    if _s[10] != 0xca: raise ValueError, "_s[10] != 0xca"
    if _s[11] != 0x3f: raise ValueError, "_s[11] != 0x3f"
    if _s[12] != 0x9d: raise ValueError, "_s[12] != 0x9d"
    if _s[13] != 0x44: raise ValueError, "_s[13] != 0x44"
    if _s[14] != 0x10: raise ValueError, "_s[14] != 0x10"
    if _s[15] != 0x2b: raise ValueError, "_s[15] != 0x2b"
    _size, _count = struct.unpack('<lB', _handle.read(5))
    _headerstart = _headersize = None
    _headerdata = array.array('B')
    _bmpstart = _bmpsize = None
    _bmpdata = array.array('B')
    _wmfstart = _wmfsize = None
    _wmfdata = array.array('B')
    for _i in range(_count):
        _code, _start, _imgsize = struct.unpack('<Bll', _handle.read(9))
        if _code == 1: # header
            _headerstart = _start
            _headersize = _imgsize
        elif _code == 2: # bmp
            _bmpstart = _start
            _bmpsize = _imgsize
        elif _code == 3: # wmf
            _wmfstart = _start
            _wmfsize = _imgsize
        else:
            raise ValueError, "Unexpected code: %#x" % _code
    if _headerstart is not None and _headersize is not None:
        _handle.seek(_headerstart, 0)
        _headerdata.fromfile(_handle, _headersize) # what to do with this ???
    if _bmpstart is not None and _bmpsize is not None:
        _handle.seek(_bmpstart, 0)
        _bmpdata.fromfile(_handle, _bmpsize)
    if _wmfstart is not None and _wmfsize is not None:
        _handle.seek(_wmfstart, 0)
        _wmfdata.fromfile(_handle, _wmfsize)
    _s.fromfile(_handle, 16)
    if _s[16] != 0xe0: raise ValueError, "_s[16] != 0xe0"
    if _s[17] != 0xda: raise ValueError, "_s[17] != 0xda"
    if _s[18] != 0x92: raise ValueError, "_s[18] != 0x92"
    if _s[19] != 0xf8: raise ValueError, "_s[19] != 0xf8"
    if _s[20] != 0x2b: raise ValueError, "_s[20] != 0x29"
    if _s[21] != 0xc9: raise ValueError, "_s[21] != 0xc9"
    if _s[22] != 0xd7: raise ValueError, "_s[22] != 0xd7"
    if _s[23] != 0xd7: raise ValueError, "_s[23] != 0xd7"
    if _s[24] != 0x62: raise ValueError, "_s[24] != 0x62"
    if _s[25] != 0xa8: raise ValueError, "_s[25] != 0xa8"
    if _s[26] != 0x35: raise ValueError, "_s[26] != 0x35"
    if _s[27] != 0xc0: raise ValueError, "_s[27] != 0xc0"
    if _s[28] != 0x62: raise ValueError, "_s[28] != 0x62"
    if _s[29] != 0xbb: raise ValueError, "_s[29] != 0xbb"
    if _s[30] != 0xef: raise ValueError, "_s[30] != 0xef"
    if _s[31] != 0xd4: raise ValueError, "_s[31] != 0xd4"
    if _bmpdata is not None:
        dwg.setImage('BMP', _bmpdata)
    if _wmfdata is not None:
        dwg.setImage('WMF', _wmfdata)

def get_headers(dwg):
    _handle = dwg.getHandle()
    _offset, _size = dwg.getOffset('HEADERS')
    _handle.seek(_offset, 0)
    _s = array.array('B')
    _s.fromfile(_handle, 16)
    if _s[0] != 0xcf: raise ValueError, "_s[0] != 0xcf"
    if _s[1] != 0x7b: raise ValueError, "_s[1] != 0x7b"
    if _s[2] != 0x1f: raise ValueError, "_s[2] != 0x1f"
    if _s[3] != 0x23: raise ValueError, "_s[3] != 0x23"
    if _s[4] != 0xfd: raise ValueError, "_s[4] != 0xfd"
    if _s[5] != 0xde: raise ValueError, "_s[5] != 0xde"
    if _s[6] != 0x38: raise ValueError, "_s[6] != 0x38"
    if _s[7] != 0xa9: raise ValueError, "_s[7] != 0xa9"
    if _s[8] != 0x5f: raise ValueError, "_s[8] != 0x5f"
    if _s[9] != 0x7c: raise ValueError, "_s[9] != 0x7c"
    if _s[10] != 0x68: raise ValueError, "_s[10] != 0x68"
    if _s[11] != 0xb8: raise ValueError, "_s[11] != 0xb8"
    if _s[12] != 0x4e: raise ValueError, "_s[12] != 0x4e"
    if _s[13] != 0x6d: raise ValueError, "_s[13] != 0x6d"
    if _s[14] != 0x33: raise ValueError, "_s[14] != 0x33"
    if _s[15] != 0x5f: raise ValueError, "_s[15] != 0x5f"
    _size = struct.unpack('<l', _handle.read(4))[0]
    _data = array.array('B')
    _data.fromfile(_handle, _size)
    _crc = struct.unpack('<h', _handle.read(2))[0]
    _s.fromfile(_handle, 16)
    if _s[16] != 0x30: raise ValueError, "_s[16] != 0x30"
    if _s[17] != 0x84: raise ValueError, "_s[17] != 0x84"
    if _s[18] != 0xe0: raise ValueError, "_s[18] != 0xe0"
    if _s[19] != 0xdc: raise ValueError, "_s[19] != 0xdc"
    if _s[20] != 0x02: raise ValueError, "_s[20] != 0x02"
    if _s[21] != 0x21: raise ValueError, "_s[21] != 0x21"
    if _s[22] != 0xc7: raise ValueError, "_s[22] != 0xc7"
    if _s[23] != 0x56: raise ValueError, "_s[23] != 0x56"
    if _s[24] != 0xa0: raise ValueError, "_s[24] != 0xa0"
    if _s[25] != 0x83: raise ValueError, "_s[25] != 0x83"
    if _s[26] != 0x97: raise ValueError, "_s[26] != 0x97"
    if _s[27] != 0x47: raise ValueError, "_s[27] != 0x47"
    if _s[28] != 0xb1: raise ValueError, "_s[28] != 0xb1"
    if _s[29] != 0x92: raise ValueError, "_s[29] != 0x92"
    if _s[30] != 0xcc: raise ValueError, "_s[30] != 0xcc"
    if _s[31] != 0xa0: raise ValueError, "_s[31] != 0xa0"
    #
    # decode the data
    #
    _bitpos = 0
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL3', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL4', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING1', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING2', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING3', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING4', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('LONG1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('LONG2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('HANDLE1', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMASO', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSHO', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PLINEGEN', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('ORTHOMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('REGENMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('FILLMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('QTEXTMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PSLTSCALE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('LIMCHECK', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('User_timer', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('SKPOLY', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('ANGDIR', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('SPLFRAME', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('MIRRTEXT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('WORLDVIEW', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('TILEMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PLIMCHECK', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('VISRETAIN', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DISPSILH', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PELLISE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('PROXYGRAPH', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('TREEDEPTH', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('LUNITS', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('LUPREC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('AUNITS', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('AUPREC', _val)
    # print "bitpos at attmode: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('ATTMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('PDMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI3', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI4', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI5', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SPLINESEGS', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFU', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFV', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFTYPE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFTAB1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFTAB2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SPLINETYPE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHADEGDE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHADEDIF', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('UNITMODE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('MAXACTVP', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('ISOLINES', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('CMLJUST', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('TEXTQLTY', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('LTSCALE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('TEXTSIZE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('TRACEWID', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('SKETCHINC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('FILLETRAD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('THICKNESS', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('ANGBASE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PDSIZE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PLINEWID', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR3', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR4', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR5', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERA', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERB', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('FACETRES', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CMLSCALE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CELTSCALE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('MENUNAME', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDCREATE_JD', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDCREATE_MS', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDUPDATE_JD', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDUPDATE_MS', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDINDWG_D', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDINDWG_MS', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDUSRTIMER_D', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _long = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDUSRTIMER_MS', _long)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('CECOLOR', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('HANDSEED', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('CLAYER', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('TEXTSTYLE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('CELTYPE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMSTYLE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('CMLSTYLE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSVPSCALE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_INSBASE', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_EXTMIN', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_EXTMAX', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('PSPACE_LIMMIN', (_val1, _val2))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('PSPACE_LIMMAX', (_val1, _val2))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_ELEVATION', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSORG', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSXDIR', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSYDIR', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos,  _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSNAME', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PUCSBASE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('PUCSORTHOVIEW', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PUCSORTHOREF', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PUCSORGTOP', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PUCSORGBOTTOM', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PUCSORGLEFT', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PUCSORGRIGHT', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PUCSORGFRONT', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PUCSORGBACK', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_INSBASE', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_EXTMIN', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_EXTMAX', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('MSPACE_LIMMIN', (_val1, _val2))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('MSPACE_LIMMAX', (_val1, _val2))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_ELEVATION', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSORG', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSXDIR', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSYDIR', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSNAME', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('UCSBASE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('UCSORTHOVIEW', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('UCSORTHOREF', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('UCSORGTOP', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('UCSORGBOTTOM', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('UCSORGLEFT', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('UCSORGRIGHT', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('UCSORGFRONT', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('UCSORGBACK', (_val1, _val2, _val3))
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMPOST', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMAPOST', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMSCALE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMASZ', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMEXO', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMDLI', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMEXE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMAND', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMDLE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTP', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTM', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTOL', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMLIM', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTIH', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTOH', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSE1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSE2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMTAD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMZIN', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMAZIN', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTXT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMCEN', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMSZ', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMALTF', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMLFAC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTVP', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTFAC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMGAP', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMALTRND', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMALT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTOFL', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSAH', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTIX', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSOXD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMCLRD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMCLRE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMCLRT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMADEC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMDEC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMTDEC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTU', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTTD', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMAUNIT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMFRAC', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMLUNIT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMDSEP', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMTMOVE', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMJUST', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSD1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSD2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMTOLJ', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMTZIN', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTZ', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTTZ', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMUPT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMFIT', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMTXTSTY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMLDRBLK', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMBLK', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMBLK1', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMBLK2', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMLWD', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMLWE', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('BLOCK_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('LAYER_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('STYLE_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('LINETYPE_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('VIEW_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('UCS_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('VPORT_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('APPID_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMSTYLE_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('VIEWPORT_ENTITY_HEADER_CONTROL_OBJECT', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('ACAD_GROUP_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('ACAD_MLINE_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('NAMED_OBJECTS_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHORT1', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHORT2', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('HYPERLINKBASE', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STYLESHEET', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('LAYOUTS_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PLOTSETTINGS_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PLOTSTYLES_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('FLAGS', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('INSUNITS', _val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('CEPSNTYPE', _val)
    # print "bitpos: %d" % _bitpos
    if _val == 3:
        _bitpos, _val = dwgutil.get_handle(_data, _bitpos)
        dwg.setHeader('CPSNID', _val)
        # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('FINGERPRINT', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('VERSIONGUID', _string)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PSPACE_BLOCK_RECORD', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('MSPACE_BLOCK_RECORD', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('LTYPE_BYLAYER', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('LTYPE_BYBLOCK', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('LTYPE_CONTINUOUS', _handle)
    # print "bitpos: %d" % _bitpos
    # print "bitpos after LTYPE (CONTINUOUS): %d" % _bitpos
    # print "byte: %d" % (_bitpos/8)
    # print "offset: %d" % (_bitpos % 8)
    #
    # remaing bits are unknown, and they end with possible
    # padding bits so that 16-bit CRC value after the data
    # is on a byte boundary - ignore them for now ...
    #

def get_classes(dwg):
    _handle = dwg.getHandle()
    _offset, _size = dwg.getOffset('CLASSES') # size is ignored
    _handle.seek(_offset, 0)
    _s = array.array('B')
    _s.fromfile(_handle, 16)
    if _s[0] != 0x8d: raise ValueError, "_s[0] != 0x8d"
    if _s[1] != 0xa1: raise ValueError, "_s[1] != 0xa1"
    if _s[2] != 0xc4: raise ValueError, "_s[2] != 0xc4"
    if _s[3] != 0xb8: raise ValueError, "_s[3] != 0xb8"
    if _s[4] != 0xc4: raise ValueError, "_s[4] != 0xc4"
    if _s[5] != 0xa9: raise ValueError, "_s[5] != 0xa9"
    if _s[6] != 0xf8: raise ValueError, "_s[6] != 0xf8"
    if _s[7] != 0xc5: raise ValueError, "_s[7] != 0xc5"
    if _s[8] != 0xc0: raise ValueError, "_s[8] != 0xc0"
    if _s[9] != 0xdc: raise ValueError, "_s[9] != 0xdc"
    if _s[10] != 0xf4: raise ValueError, "_s[10] != 0xf4"
    if _s[11] != 0x5f: raise ValueError, "_s[11] != 0x5f"
    if _s[12] != 0xe7: raise ValueError, "_s[12] != 0xe7"
    if _s[13] != 0xcf: raise ValueError, "_s[13] != 0xcf"
    if _s[14] != 0xb6: raise ValueError, "_s[14] != 0xb6"
    if _s[15] != 0x8a: raise ValueError, "_s[15] != 0x8a"
    _size = struct.unpack('<l', _handle.read(4))[0]
    _data = array.array('B')
    _data.fromfile(_handle, _size)
    _crc = struct.unpack('<h', _handle.read(2))[0]
    _s.fromfile(_handle, 16)
    if _s[16] != 0x72: raise ValueError, "_s[16] != 0x72"
    if _s[17] != 0x5e: raise ValueError, "_s[17] != 0x5e"
    if _s[18] != 0x3b: raise ValueError, "_s[18] != 0x3b"
    if _s[19] != 0x47: raise ValueError, "_s[19] != 0x47"
    if _s[20] != 0x3b: raise ValueError, "_s[20] != 0x3b"
    if _s[21] != 0x56: raise ValueError, "_s[21] != 0x56"
    if _s[22] != 0x07: raise ValueError, "_s[22] != 0x07"
    if _s[23] != 0x3a: raise ValueError, "_s[23] != 0x3a"
    if _s[24] != 0x3f: raise ValueError, "_s[24] != 0x3f"
    if _s[25] != 0x23: raise ValueError, "_s[25] != 0x23"
    if _s[26] != 0x0b: raise ValueError, "_s[26] != 0x0b"
    if _s[27] != 0xa0: raise ValueError, "_s[27] != 0xa0"
    if _s[28] != 0x18: raise ValueError, "_s[28] != 0x18"
    if _s[29] != 0x30: raise ValueError, "_s[29] != 0x30"
    if _s[30] != 0x49: raise ValueError, "_s[30] != 0x49"
    if _s[31] != 0x75: raise ValueError, "_s[31] != 0x75"
    #
    # get the class info from the data array
    #
    _maxbit = _size * 8
    _bitpos = 0
    while (_bitpos + 8) < _maxbit: # watch out for padding bits ...
        _bitpos, _classnum = dwgutil.get_bit_short(_data, _bitpos)
        _bitpos, _ver = dwgutil.get_bit_short(_data, _bitpos)
        _bitpos, _appname = dwgutil.get_text_string(_data, _bitpos)
        _bitpos, _cppcn = dwgutil.get_text_string(_data, _bitpos)
        _bitpos, _dxfname = dwgutil.get_text_string(_data, _bitpos)
        _bitpos, _zombie = dwgutil.test_bit(_data, _bitpos)
        _bitpos, _id = dwgutil.get_bit_short(_data, _bitpos)
        dwg.setDxfName(_classnum, _dxfname)
        dwg.setClass(_classnum, (_ver, _appname, _cppcn, _zombie, _id))
    
def get_objects(dwg):
    for _offset in dwg.getEntityOffset():
        _obj = get_object(dwg, _offset)
        dwg.setObject(_obj)

def get_offsets(dwg):
    _handle = dwg.getHandle()
    _offset, _size = dwg.getOffset('OBJECTS') # size is ignored
    _handle.seek(_offset, 0)
    while True:
        _data = array.array('B')
        _size = struct.unpack('>h', _handle.read(2))[0] # big-endian size
        if _size == 2: # section is just CRC
            break
        _data.fromfile(_handle, _size)
        #
        # the spec says 'last_handle' and 'last_loc' are initialized outside
        # the outer for loop - postings on OpenDWG forum say these variables
        # must be initialized for each section
        #
        _last_handle = 0
        _last_loc = 0
        _bitpos = 0
        _bitmax = (_size - 2) * 8 # remove two bytes for section CRC
        #
        # there should be something done with the CRC for section ...
        #
        while  _bitpos < _bitmax:
            _bitpos, _hoffset = dwgutil.get_modular_char(_data, _bitpos)
            _last_handle = _last_handle + _hoffset
            _bitpos, _foffset = dwgutil.get_modular_char(_data, _bitpos)
            _last_loc = _last_loc + _foffset
            dwg.addEntityOffset(_last_handle, _last_loc)
#
# read the common parts at the start of many entities
#

def header_read(ent, data, offset):
    _bitpos = offset
    _mode = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    ent.setMode(_mode)
    _bitpos, _rnum = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_rnum)
    _bitpos, _nolinks = dwgutil.test_bit(data, _bitpos)
    ent.setNoLinks(_nolinks)
    _bitpos, _color = dwgutil.get_bit_short(data, _bitpos)
    ent.setColor(_color)
    _bitpos, _ltscale = dwgutil.get_bit_double(data, _bitpos)
    ent.setLinetypeScale(_ltscale)
    _ltflag = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    ent.setLinetypeFlags(_ltflag)
    _psflag = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    ent.setPlotstyleFlags(_psflag)
    _bitpos, _invis = dwgutil.get_bit_short(data, _bitpos)
    ent.setInvisiblity(_invis)
    _bitpos, _weight = dwgutil.get_raw_char(data, _bitpos)
    ent.setLineweight(_weight)
    return _bitpos
#
# read the common parts ant the end of many entities
#

def tail_read(ent, data, offset):
    _bitpos = offset
    _sh = None
    if ent.getMode() == 0x0:
        _bitpos, _sh = dwgutil.get_handle(data, _bitpos)
        ent.setSubentity(_sh)
    for _i in range(ent.getNumReactors()):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _xh = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_xh)
    _bitpos, _lh = dwgutil.get_handle(data, _bitpos)
    ent.setLayer(_lh)
    if ent.getNoLinks() is False:
        _bitpos, _prev = dwgutil.get_handle(data, _bitpos)
        ent.setPrevious(_prev)
        _bitpos, _next = dwgutil.get_handle(data, _bitpos)
        ent.setNext(_next)
    if ent.getLinetypeFlags() == 0x3:
        _bitpos, _lth = dwgutil.get_handle(data, _bitpos)
        ent.setLinetype(_lth)
    if ent.getPlotstyleFlags() == 0x3:
        _bitpos, _pth = dwgutil.get_handle(data, _bitpos)
        ent.setPlotstyle(_pth)
    return _bitpos

#
# read the various entities stored in the DWG file
#

def text_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _dflag = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('data_flag', _dflag)
    if not (_dflag & 0x1):
        _bitpos, _elev = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('elevation', _elev)
    _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x1, _y1))
    if not (_dflag & 0x2):
        _bitpos, _x = dwgutil.get_default_double(data, _bitpos, _x1)
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _y1)
        ent.setEntityData('alignment_point', (_x, _y))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _th = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    if not (_dflag & 0x4):
        _bitpos, _oblique = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('oblique_angle', _oblique)
    if not (_dflag & 0x8):
        _bitpos, _rotation = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('rotation_angle', _rotation)
    _bitpos, _height = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('height', _height)
    if not (_dflag & 0x10):
        _bitpos, _width = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('width_factor', _width)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    if not (_dflag & 0x20):
        _bitpos, _gen = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('generation', _gen)
    if not (_dflag & 0x40):
        _bitpos, _halign = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('halign', _halign)
    if not (_dflag & 0x80):
        _bitpos, _valign = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('valign', _valign)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def attrib_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _dflag = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('data_flag', _dflag)
    if not (_dflag & 0x1):
        _bitpos, _elev = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('elevation', _elev)
    _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x1, _y1))
    if not (_dflag & 0x2):
        _bitpos, _x = dwgutil.get_default_double(data, _bitpos, _x1)
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _y1)
        ent.setEntityData('alignment_point', (_x, _y))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _th = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    if not (_dflag & 0x4):
        _bitpos, _oblique = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('oblique_angle', _oblique)
    if not (_dflag & 0x8):
        _bitpos, _rotation = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('rotation_angle', _rotation)
    _bitpos, _height = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('height', _height)
    if not (_dflag & 0x10):
        _bitpos, _width = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('width_factor', _width)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    if not (_dflag & 0x20):
        _bitpos, _gen = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('generation', _gen)
    if not (_dflag & 0x40):
        _bitpos, _halign = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('halign', _halign)
    if not (_dflag & 0x80):
        _bitpos, _valign = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('valign', _valign)
    _bitpos, _tag = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('tag', _tag)
    _bitpos, _fl = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('field_length', _fl)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def attdef_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _dflag = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('data_flag', _dflag)
    if not (_dflag & 0x1):
        _bitpos, _elev = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('elevation', _elev)
    _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x1, _y1))
    if not (_dflag & 0x2):
        _bitpos, _x = dwgutil.get_default_double(data, _bitpos, _x1)
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _y1)
        ent.setEntityData('alignment_point', (_x, _y))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _th = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    if not (_dflag & 0x4):
        _bitpos, _oblique = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('oblique_angle', _oblique)
    if not (_dflag & 0x8):
        _bitpos, _rotation = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('rotation_angle', _rotation)
    _bitpos, _height = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('height', _height)
    if not (_dflag & 0x10):
        _bitpos, _width = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('width_factor', _width)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    if not (_dflag & 0x20):
        _bitpos, _gen = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('generation', _gen)
    if not (_dflag & 0x40):
        _bitpos, _halign = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('halign', _halign)
    if not (_dflag & 0x80):
        _bitpos, _valign = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('valign', _valign)
    _bitpos, _tag = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('tag', _tag)
    _bitpos, _fl = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('field_length', _fl)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _prompt = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('prompt', _prompt)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def block_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos = tail_read(ent, data, _bitpos)

def endblk_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos = tail_read(ent, data, _bitpos)

def seqend_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos = tail_read(ent, data, _bitpos)

def insert_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y, _z))
    _dflag = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    if _dflag == 0x0:
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _x)
        _bitpos, _z = dwgutil.get_default_double(data, _bitpos, _x)
    elif _dflag == 0x1:
        _x = 1.0
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _x)
        _bitpos, _z = dwgutil.get_default_double(data, _bitpos, _x)
    elif _dflag == 0x2:
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _y = _z = _x
    else:
        _x = _y = _z = 1.0
    ent.setEntityData('scale', (_x, _y, _z))
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation',  _rot)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _hasattr = dwgutil.test_bit(data, _bitpos)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('block_header_handle', _handle)
    if _hasattr:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('first_attrib_handle', _handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('last_attrib_handle', _handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('seqend_handle', _handle)

def minsert_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y, _z))
    _dflag = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    if _dflag == 0x0:
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _x)
        _bitpos, _z = dwgutil.get_default_double(data, _bitpos, _x)
    elif _dflag == 0x1:
        _x = 1.0
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _x)
        _bitpos, _z = dwgutil.get_default_double(data, _bitpos, _x)
    elif _dflag == 0x2:
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _y = _z = _x
    else:
        _x = _y = _z = 1.0
    ent.setEntityData('scale', (_x, _y, _z))
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _rot)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _hasattr = dwgutil.test_bit(data, _bitpos)
    _bitpos, _nc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('column_count', _nc)
    _bitpos, _nr = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('row_count', _nr)
    _bitpos, _colsp = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('column_spacing', _colsp)
    _bitpos, _rowsp = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('row_spacing', _rowsp)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('block_header_handle', _handle)
    if _hasattr:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('first_attrib_handle', _handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('last_attrib_handle', _handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('seqend_handle', _handle)

def vertex2d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos, _sw = dwgutil.get_bit_double(data, _bitpos)
    if _sw < 0.0:
        _sw = _ew = abs(_sw)
    else:
        _bitpos, _ew = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_width', _sw)
    ent.setEntityData('end_width', _ew)
    _bitpos, _bulge = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('bulge',  _bulge)
    _bitpos, _tandir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('tangent_dir', _tandir)
    _bitpos = tail_read(ent, data, _bitpos)

def vertex3d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def vertex_mesh_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def vertex_pface_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def vertex_pface_face_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _vi1 = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _vi2 = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _vi3 = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _vi4 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('points', (_vi1, _vi2, _vi3, _vi4))
    _bitpos = tail_read(ent, data, _bitpos)

def polyline2d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flags = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _ctype = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('curve_type', _ctype)
    _bitpos, _sw = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_width', _sw)
    _bitpos, _ew = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_width', _ew)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _ex = _ey = 0.0
        _ez = 1.0
    else:
        _bitpos, _ex = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _ey = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _ez = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_ex, _ey, _ez))
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('first_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('last_vertext_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('seqend_handle', _handle)

def polyline3d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _sflags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('spline_flags', _sflags)
    _bitpos, _cflags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('closed_flags', _cflags)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('first_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('last_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('seqend_handle', _handle)

def arc_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('center', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('radius', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _val = 0.0
    else:
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_angle', _val)
    _bitpos = tail_read(ent, data, _bitpos)

def circle_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('center', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('radius', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _val = 0.0
    else:
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def line_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _zflag = dwgutil.test_bit(data, _bitpos)
    _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _x2 = dwgutil.get_default_double(data, _bitpos, _x1)
    _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y2 = dwgutil.get_default_double(data, _bitpos, _y1)
    if _zflag is False:
        _bitpos, _z1 = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _z2 = dwgutil.get_default_double(data, _bitpos, _z1)
        _p1 = (_x1, _y1, _z1)
        _p2 = (_x2, _y2, _z2)
    else:
        _p1 = (_x1, _y1)
        _p2 = (_x2, _y2)
    ent.setEntityData('p1', _p1)
    ent.setEntityData('p2', _p2)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _ex = _ey = 0.0
        _ez = 1.0
    else:
        _bitpos, _ex = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _ey = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _ez = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_ex, _ey, _ez))
    _bitpos = tail_read(ent, data, _bitpos)

def dimord_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_x, _y, _z))
    _bitpos, _flags2 = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags2',  _flags)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def dimlin_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_x, _y, _z))
    _bitpos, _elr = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_rotation', _elr)
    _bitpos, _dr = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('dimension_rotation', _dr)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def dimalign_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_x, _y, _z))
    _bitpos, _elr = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_rotation', _elr)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def dimang3p_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def dimang2l_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('16-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def dimrad_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_ir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_x, _y, _z))
    _bitpos, _llen = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('leader_length', _llen)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def dimdia_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('text_midpoint', (_x, _y))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _flags = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _rot)
    _bitpos, _hdir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _hdir)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _ir = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _ir)
    _bitpos, _ap = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment_point', _ap)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('linespace_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('linespace_factor', _lsf)
    _bitpos, _am = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('actual_measurement', _am)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_x, _y, _z))
    _bitpos, _llen = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('leader_length', _llen)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('anon_block_handle', _handle)

def point_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _xa = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_axis_angle', _xa)
    _bitpos = tail_read(ent, data, _bitpos)

def face3d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _nf = dwgutil.test_bit(data, _bitpos) # spec says RC, files say otherwise
    _bitpos, _zflag = dwgutil.test_bit(data, _bitpos)
    _bitpos, _cx = dwgutil.get_raw_double(data, _bitpos)
    _dcx = _cx
    _bitpos, _cy = dwgutil.get_raw_double(data, _bitpos)
    _dcy = _cy
    _cz = _dcz = 0.0    
    if _zflag is False:
        _bitpos, _cz = dwgutil.get_raw_double(data, _bitpos)
        _dcz = _cz
    _corner = (_cx, _cy, _cz)
    ent.setEntityData('corner1', _corner)
    _bitpos, _cx = dwgutil.get_default_double(data, _bitpos, _dcx)
    _dcx = _cx
    _bitpos, _cy = dwgutil.get_default_double(data, _bitpos, _dcy)
    _dcy = _cy
    _bitpos, _cz = dwgutil.get_default_double(data, _bitpos, _dcz)
    _dcz = _cz    
    _corner = (_cx, _cy, _cz)
    ent.setEntityData('corner2', _corner)
    _bitpos, _cx = dwgutil.get_default_double(data, _bitpos, _dcx)
    _dcx = _cx
    _bitpos, _cy = dwgutil.get_default_double(data, _bitpos, _dcy)
    _dcy = _cy
    _bitpos, _cz = dwgutil.get_default_double(data, _bitpos, _dcz)
    _dcz = _cz
    _corner = (_cx, _cy, _cz)
    ent.setEntityData('corner3', _corner)
    _bitpos, _cx = dwgutil.get_default_double(data, _bitpos, _dcx)
    _bitpos, _cy = dwgutil.get_default_double(data, _bitpos, _dcy)
    _bitpos, _cz = dwgutil.get_default_double(data, _bitpos, _dcz)
    _corner = (_cx, _cy, _cz)
    ent.setEntityData('corner4', _corner)
    if _nf is False:
        _bitpos, _invis = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('flags', _invis)
    _bitpos = tail_read(ent, data, _bitpos)

def pface_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _nv = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('vertex_count', _nv)
    _bitpos, _nf = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('face_count', _nf)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('first_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('last_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('seqend_handle', _handle)

def mesh_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flags = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _ctype = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('curve_type', _ctype)
    _bitpos, _mvc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('m_vertices', _mvc)
    _bitpos, _nvc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('n_vertices', _nvc)
    _bitpos, _md = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('m_density', _md)
    _bitpos, _nd = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('n_density', _md)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('first_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('last_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('seqend_handle', _handle)

def solid_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner1', (_x, _y, _elev))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner2', (_x, _y, _elev))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner3', (_x, _y, _elev))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner4', (_x, _y, _elev))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def trace_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _th = 0.0
    else:
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner1', (_x, _y, _elev))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner2', (_x, _y, _elev))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner3', (_x, _y, _elev))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('corner4', (_x, _y, _elev))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    if _flag:
        _x = _y = 0.0
        _z = 1.0
    else:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def shape_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y, _z))
    _bitpos, _scale = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale', _scale)
    _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _rot)
    _bitpos, _width = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _width)
    _bitpos, _ob = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique', _ob)
    _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _bitpos, _snum = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('shape_number', _snum)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('shapefile_handle', _handle)

def viewport_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('center', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_target', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_direction', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_twist_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('lens_length', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_clip_z', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_clip_z', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('snap_angle', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('view_center', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('snap_base', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('snap_spacing', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('grid_spacing', (_x, _y))
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('circle_zoom', _val)
    _bitpos, _flc = dwgutil.get_bit_long(data, _bitpos)
    _bitpos, _flags = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('status_flags', _flags)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('stylesheet', _text)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('render_mode', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('ucs_at_origin', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('ucs_per_viewport', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ucs_origin', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ucs_x_axis', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ucs_y_axis', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('ucs_ortho_view', _val)
    _bitpos = tail_read(ent, data, _bitpos)
    if _flc:
        _handles = []
        for _i in range(_flc):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handles)
        ent.setEntityData('frozen_layer_handles', _handles)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('clip_boundary_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('viewport_ent_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('named_ucs_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('base_ucs_handle', _handle)

def ellipse_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('center', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('major_axis_vector', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('axis_ratio', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_angle', _val)
    _bitpos = tail_read(ent, data, _bitpos)

def spline_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _sc = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _deg = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('degree', _deg)
    _nknots = _nctlpts = _nfitpts = 0
    _weight = False
    if _sc == 2:
        _bitpos, _ft = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('fit_tolerance', _ft)
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('begin_tan_vector', (_x, _y, _z))
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('end_tan_vector', (_x, _y, _z))
        _bitpos, _nfitpts = dwgutil.get_bit_short(data, _bitpos)
    elif _sc == 1:
        _bitpos, _rat = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('rational', _rat)
        _bitpos, _closed = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('closed', _closed)
        _bitpos, _per = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('periodic', _per)
        _bitpos, _ktol = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('knot_tolerance', _ktol)
        _bitpos, _ctol = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('control_tolerance', _ctol)
        _bitpos, _nknots = dwgutil.get_bit_long(data, _bitpos)
        _bitpos, _nctlpts = dwgutil.get_bit_long(data, _bitpos)
        _bitpos, _weight = dwgutil.test_bit(data, _bitpos)
    else:
        raise ValueError, "Unexpected scenario: %d" % _sc
    if _nknots:
        _knotpts = []
        for _i in range(_nknots):
            _bitpos, _knot = dwgutil.get_bit_double(data, _bitpos)
            _knotpts.append(_knot)
        ent.setEntityData('knot_points', _knotpts)
    if _nctlpts:
        _ctrlpts = []
        _weights = []
        for _i in range(_nctlpts):
            _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
            _ctrlpts.append((_x, _y, _z))
            if _weight:
                _bitpos, _w = dwgutil.get_bit_double(data, _bitpos)
                _weights.append(_w)
        ent.setEntityData('control_points', _ctrlpts)
        if _weight:
            ent.setEntityData('weights', _weights)
    if _nfitpts:
        _fitpts = []
        for _i in range(_nfitpts):
            _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
            _fitpts.append((_x, _y, _z))
        ent.setEntityData('fit_points', _fitpts)
    _bitpos = tail_read(ent, data, _bitpos)

def rsb_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _itype = dwgutil.get_bit_short(data, _bitpos)
    if (_itype == 64):
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        # print "unknown double: %g" % _val
        _bitpos, _cib = dwgutil.get_bit_long(data, _bitpos)
        _data = []
        while (_cib != 0):
            _chars = []
            for _i in range(_cib):
                _bitpos, _ch = dwgutil.get_raw_char(data, _bitpos)
                if (0x20 < _ch < 0x7e):
                    _sat = 0x9f - _ch
                elif (_ch == ord("\t")):
                    _sat = ord(" ")
                else:
                    _sat = _ch
                _chars.append(_sat)
            _data.append("".join(_chars))
            _bitpos, _cib = dwgutil.get_bit_long(data, _bitpos)
    else:
        raise ValueError, "Unexpected itemtype: %d" % _itype
    #
    # OpenDWG specs say there is stuff here but they haven't
    # figured it out, plus there is the tailing handles
    # skip this for now ...
    # _bitpos = tail_read(ent, data, _bitpos)

def ray_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('vector', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def xline_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('vector', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def dict_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _ni = dwgutil.get_bit_long(data, _bitpos)
    _bitpos, _cflag = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('cloning_flag', _cflag)
    _bitpos, _hoflag = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('hard_owner_flag', _hoflag) # ???
    if _ni:
        _strings = []
        for _i in range(_ni):
            _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
            _strings.append(_text)
        ent.setEntityData('strings', _strings)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ni:
        _items = []
        for _i in range(_ni):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _items.append(_handle)
        ent.setEntityData('items', _items)
        
def mtext_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_axis_direction', (_x, _y, _z))
    _bitpos, _width = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width',  _width)
    _bitpos, _height = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('height', _height)
    _bitpos, _att = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment', _att)
    _bitpos, _dd = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('drawing_dir', _dd) # ???
    _bitpos, _exh = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_height', _exh)
    _bitpos, _exw = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_width', _exw)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _lss = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('line_spacing_style', _lss)
    _bitpos, _lsf = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('line_spacing_factor:', _lsf)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    # print "unknown bit: " + str(_val)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def leader_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _u = dwgutil.test_bit(data, _bitpos)
    # print "unknown bit: " + str(_u)
    _bitpos, _at = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('annotation_type', _at)
    _bitpos, _pt = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('path_type',  _pt)
    _bitpos, _npts = dwgutil.get_bit_short(data, _bitpos)
    _points = []
    for _i in range(_npts):
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _points.append((_x, _y, _z))
    ent.setEntityData('points', _points)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_pt_proj', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_direction', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('offset_block_ins_pt', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    # print "unknown: (%g,%g,%g)" % (_x, _y, _z)
    _bitpos, _bh = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('box_height', _bh)
    _bitpos, _bw = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('box_width', _bw)
    _bitpos, _hook = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('hooklineoxdir', _hook) # ???
    _bitpos, _arrowon = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('arrowhead_on', _arrowon)
    _bitpos, _us = dwgutil.get_bit_short(data, _bitpos)
    # print "unknown short: %d" % _us
    _bitpos, _ub = dwgutil.test_bit(data, _bitpos)
    # print "unknown bit: " + str(_ub)
    _bitpos, _ub = dwgutil.test_bit(data, _bitpos)
    # print "unknown bit: " + str(_ub)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('associated_annotation_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)

def tolerance_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_direction', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _ts = dwgutil.get_bit_short(data, _bitpos) # should this be text_string?
    ent.setEntityData('string', _ts)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)

def mline_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _scale = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale', _scale)
    _bitpos, _just = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('justification', _just)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('base_point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _oc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('open_closed', _oc)
    _bitpos, _lis = dwgutil.get_raw_char(data, _bitpos)
    _bitpos, _nv = dwgutil.get_bit_short(data, _bitpos)
    _points = []
    for _i in range(_nv):
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _vertex = (_x, _y, _z)
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _vertex_dir = (_x, _y, _z)
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _miter_dir = (_x, _y, _z)
        _lines = []
        for _j in range(_lis):
            _bitpos, _ns = dwgutil.get_bit_short(data, _bitpos)
            _segparms = []
            for _k in range(_ns):
                _bitpos, _sp = dwgutil.get_bit_double(data, _bitpos)
                _segparms.append(_sp)
            _bitpos, _na = dwgutil.get_bit_short(data, _bitpos)
            _fillparms = []
            for _k in range(_na):
                _bitpos, _afp = dwgutil.get_bit_double(data, _bitpos)
                _fillparms.append(_afp)
            _lines.append((_segparms, _fillparms))
        _points.append((_vertex, _vertex_dir, _miter_dir, _lines))
    ent.setEntityData('points', _points)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('mline_style_object_handle', _handle)

def block_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _enum = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _enum:
        _handles = []
        for  _i in range(_enum):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('code_2_handles', _handles)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('*model_space_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('*paper_space_handle', _handle)

def block_header_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    # print "bitpos: %d" % _bitpos
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _anon = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('anonymous', _anon)
    # print "bitpos: %d" % _bitpos
    _bitpos, _hasatts = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('has_attrs', _hasatts)
    _bitpos, _bxref = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('blk_is_xref', _bxref)
    _bitpos, _xover = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xrefoverlaid', _xover)
    # print "bitpos: %d" % _bitpos
    _bitpos, _loaded = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('loaded', _loaded)
    _bitpos, _bx = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _by = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _bz = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('base_point', (_bx, _by, _bz))
    # print "bitpos: %d" % _bitpos
    _bitpos, _pname = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('xref_pname', _pname)
    # print "bitpos: %d" % _bitpos
    _icount = 0
    while True:
        _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
        if _val == 0:
            break
        _icount = _icount + 1
    # print "insert count: %#x" % _icount
    # print "bitpos: %d" % _bitpos
    _bitpos, _desc = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('block_description', _desc)
    # print "bitpos: %d" % _bitpos
    _bitpos, _pdsize = dwgutil.get_bit_long(data, _bitpos)
    # print "preview data size: %d" % _pdsize
    # print "bitpos: %d" % _bitpos
    if _pdsize:
        _count = _pdsize * _icount
        _pdata = dwgutil.get_bits(data, _count, _bitpos)
        ent.setEntityData('preview_data', _pdata)
        _bitpos = _bitpos + _count
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('block_control_handle', _handle)
    # print "bitpos: %d" % _bitpos
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('block_entity_handle', _handle)
    if not _bxref and not _xover:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('first_entity_handle', _handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('last_entity_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('endblk_entity_handle', _handle)
    if _icount:
        _handles = []
        for _i in range(_icount):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('insert_handles', _handles)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('layout_handle', _handle)

def layer_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('code_2_handles', _handles)

def layer_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _flags = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _color = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('color', _color)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('layer_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('plotstyle_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('linetype_handle', _handle)

def shapefile_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('shapefile_handles', _handles)

def shapefile_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _vert = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('vertical', _vert)
    _bitpos, _sf = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('shape_file', _sf)
    _bitpos, _fh = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('fixed_height', _fh)
    _bitpos, _fw = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('fixed_width', _fw)
    _bitpos, _ob = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique_angle', _ob)
    _bitpos, _gen = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('generation', _gen)
    _bitpos, _lh = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('last_height', _lh)
    _bitpos, _fn = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('font_name', _fn)
    _bitpos, _bfn = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('big_font_name', _bfn)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('shapefile_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)

def linetype_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('entity_count', _ne)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('handles', _handles)

def linetype_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _desc = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('description', _desc)
    _bitpos, _pl = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('pattern_length', _pl)
    _bitpos, _align = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('alignment', _align)
    _bitpos, _nd = dwgutil.get_raw_char(data, _bitpos)
    if _nd:
        _dashes = []
        for _i in range(_nd):
            _bitpos, _dl = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _cs = dwgutil.get_bit_short(data, _bitpos)
            _bitpos, _xo = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _yo = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _scale = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _rot = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _sf = dwgutil.get_bit_short(data, _bitpos)
            _dashes.append((_dl, _cs, _xo, _yo, _scale, _rot, _sf))
        ent.setEntityData('dashes', _dashes)
    _strings = dwgutil.get_bits(data, 256, _bitpos)
    _bitpos = _bitpos + 256
    ent.setEntityData('strings', _strings)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('linetype_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)

def view_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('view_handles', _handles)

def view_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _vh = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_height', _vh)
    _bitpos, _vw = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_width', _vw)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('view_center', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('target', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_dir', (_x, _y, _z))
    _bitpos, _ta = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('twist_angle', _ta)
    _bitpos, _ll = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('lens_length', _ll)
    _bitpos, _fc = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_clip', _fc)
    _bitpos, _bc = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_clip', _bc)
    _vm = dwgutil.get_bits(data, 4, _bitpos)
    _bitpos = _bitpos + 4
    ent.setEntityData('view_control_flags', _vm)
    _bitpos, _rmode = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('render_mode', _rmode)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('pspace_flag', _flag)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('view_control_handle', _handle)    
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('associated_ucs', _val)
    if _val:
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('ucs_origin', (_x, _y, _z))
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('ucs_x_axis', (_x, _y, _z))
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('ucs_y_axis', (_x, _y, _z))
        _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('elevation', _elev)
        _bitpos, _ovtype = dwgutil.get_bit_short(data, _bitpos)
        ent.setEntityData('orthographic_view_type', _ovtype)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('base_ucs_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('named_ucs_handle', _handle)

def ucs_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    # print "numentries: %d" % _ne
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('ucs_handles', _handles)

def ucs_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('origin', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_direction', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('y_direction', (_x, _y, _z))
    _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _bitpos, _ovtype = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('orthographic_view_type', _ovtype)
    _bitpos, _otype = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('orthographic_type',  _otype)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('ucs_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('base_ucs_handle',_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('unknown_handle', _handle)

def vport_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('vport_handles', _handles)

def vport_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _flag  = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _flag)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('aspect_ratio', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('view_center', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('target', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_dir', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('twist_angle',  _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('lens_length', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_clip', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_clip', _val)
    _flags = dwgutil.get_bits(data, 4, _bitpos)
    _bitpos = _bitpos + 4
    ent.setEntityData('vport_flags', _flags)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('render_mode', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('lower_left', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('upper_right', (_x, _y))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('ucsfollow', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('circle_zoom', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('fast_zoom', _flag)
    _flags = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    ent.setEntityData('ucsicon', _flags)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('grid_status', _flag)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('grid_spacing', (_x, _y))
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('snap_status', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('snap_style', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('snap_isopair', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('snap_rotation', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('snap_base', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('snap_spacing', (_x, _y))
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('unknown_bit', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('ucs_per_viewport', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('origin', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_direction', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('y_direction', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('orthographic_view_type', _val)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('vport_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('base_ucs_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('named_handle', _handle)

def appid_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('appid_handles', _handles)

def appid_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _u = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('unknown_char', _u)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('appid_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)

def dimstyle_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    # print "bitpos: %d" % _bitpos
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    # print "numentries: %d" % _ne
    # print "bitpos: %d" % _bitpos
    _bitpos, _nc5 = dwgutil.get_raw_char(data, _bitpos) # code 5 handles not in spec
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    # print "bitpos: %d" % _bitpos
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('dimstyle_handles', _handles)
    # print "bitpos: %d" % _bitpos
    if _nc5:
        _handles = []
        for _i in range(_nc5): # not in spec
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('code_5_handles', _handles)
    # print "bitpos: %d" % _bitpos

def dimstyle_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMPOST', _string)
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMAPOST', _string)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMSCALE', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMASZ', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMEXO', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMDLI', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMEXE', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMRND', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMDLE', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTP', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTM', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTOL', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMLIM', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTIH', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTOH', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSE1', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSE2', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMTAD', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMZIN', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMAZIN',  _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTXT', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMCEN', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTSZ', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMALTF', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMLFAC', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTVP',  _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTFAC', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMGAP', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMALTRND', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMALT', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTD', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTOFL', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSAH', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTIX', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSOXD', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMCLRD', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMCLRE', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMCLRT', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMADEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMDEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMTDEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTU', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTTD', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMAUNIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMFRAC', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMLUNIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMDSEP', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMTMOVE', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMJUST', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSD1', _flag)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSD2', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMTOLJ', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMTZIN', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTZ', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTTZ', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMUPT', _flag)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMFIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMLWD', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMLWE', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('unknown', _flag)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('shapefile_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('leader_block_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimblk_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimblk1_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimblk2_handle', _handle)

def vpentity_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_short(data, _bitpos)
    # print "numentries: %d" % _ne
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('vpentity_handles', _handles)

def vpentity_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _flag)
    _bitpos, _xrefplus1 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _xrefplus1)
    _bitpos, _xdep = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _xdep)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('1-flag', _flag)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('vpentity_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('next_vpentity_handle', _handle)

def group_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _unnamed = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('unnamed', _unnamed)
    _bitpos, _selectable = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('selectable', _selectable)
    _bitpos, _nh = dwgutil.get_bit_long(data, _bitpos)
    # print "numhandles: %d" % _nh
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _nh:
        _handles = []
        for _i in range(_nh):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('entry_handles', _handles)

def mlinestyle_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _desc = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('description', _desc)
    _bitpos, _flags = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _flags)
    _bitpos, _fc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('fill_color', _fc)
    _bitpos, _sa = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_angle', _sa)
    _bitpos, _ea = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_angle', _ea)
    _bitpos, _lc = dwgutil.get_raw_char(data, _bitpos)
    if _lc:
        _lines = []
        for _i in range(_lc):
            _bitpos, _offset = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _color = dwgutil.get_bit_short(data, _bitpos)
            _bitpos, _ltindex = dwgutil.get_bit_short(data, _bitpos)
            _lines.append((_offset, _color, _ltindex))
        ent.setEntityData('lines', _lines)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def dictionaryvar_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _iv = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('intval', _iv)
    _bitpos, _s = dwgutil.get_text_string(data, _bitpos) # spec says bit_short
    ent.setEntityData('string', _s)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def hatch_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('z_coord', _z)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _name = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _name)
    _bitpos, _sfill = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('solid_fill', _sfill)
    _bitpos, _assoc = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('associative', _assoc)
    _bitpos, _np = dwgutil.get_bit_long(data, _bitpos)
    # print "numpaths: %d" % _np
    _allbounds = 0
    _pixel = 0
    _paths = []
    for _i in range(_np):
        _bitpos, _pf = dwgutil.get_bit_long(data, _bitpos)
        if _pf & 0x4:
            _pixel = _pixel + 1
        if (_pf & 0x2): # POLYLINE
            _bitpos, _bulges = dwgutil.test_bit(data, _bitpos)
            _bitpos, _closed = dwgutil.test_bit(data, _bitpos)
            _bitpos, _nps = dwgutil.get_bit_long(data, _bitpos)
            _segs = []
            for _j in range(_nps):
                _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
                _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
                _bulge = None
                if (_bulges):
                    _bitpos, _bulge = dwgutil.get_bit_double(data, _bitpos)
                _segs.append((_x1, _y1, _bulge))
            _paths.append(('polyline', _segs))
        else:
            _bitpos, _nps = dwgutil.get_bit_long(data, _bitpos)
            _segs = []
            for _j in range(_nps):
                _bitpos, _pts = dwgutil.get_raw_char(data, _bitpos)
                if (_pts == 1): # LINE
                    _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _x2 = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _y2 = dwgutil.get_raw_double(data, _bitpos)
                    _segs.append(('line', _x1, _y1, _x2, _y2))
                elif (_pts == 2): # CIRCULAR ARC
                    _bitpos, _xc = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _yc = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _r = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _sa = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _ea = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _isccw = dwgutil.test_bit(data, _bitpos)
                    _segs.append(('arc', _xc, _yc, _r, _sa, _ea, _isccw))
                elif (_pts == 3): # ELLIPTICAL ARC
                    _bitpos, _xc = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _yc = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _xe = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _ye = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _ratio = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _sa = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _ea = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _isccw = dwgutil.test_bit(data, _bitpos)
                    _segs.append(('elliptical_arc', _xc, _yc, _xe, _ye, _ratio, _sa, _ea, _isccw))
                elif (_pts == 4): # SPLINE
                    _bitpos, _deg = dwgutil.get_bit_long(data, _bitpos)
                    _bitpos, _israt = dwgutil.test_bit(data, _bitpos)
                    _bitpos, _isper = dwgutil.test_bit(data, _bitpos)
                    _bitpos, _nknots = dwgutil.get_bit_long(data, _bitpos)
                    _bitpos, _nctlpts = dwgutil.get_bit_long(data, _bitpos)
                    _knots = []
                    for _k in range(_nknots):
                        _bitpos, _knot = dwgutil.get_bit_double(data, _bitpos)
                        _knots.append(_knot)
                    _ctlpts = []
                    for _k in range(_nctlpts):
                        _bitpos, _x1 = dwgutil.get_raw_double(data, _bitpos)
                        _bitpos, _y1 = dwgutil.get_raw_double(data, _bitpos)
                        _weight = None
                        if (_israt):
                            _bitpos, _weight = dwgutil.get_bit_double(data, _bitpos)
                        _ctlpts.append((_x1, _y1, _weight))
                    _segs.append(('spline', _israt, _isper, _knots, _ctlpts))
                else:
                    raise ValueError, "Unexpected path type: %d" % _pts
            _paths.append(('stdpath', _segs))
        _bitpos, _nbh = dwgutil.get_bit_long(data, _bitpos)
        _allbounds = _allbounds + _nbh
    _bitpos, _style = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('style', _style)
    _bitpos, _pattype = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('pattern_type', _pattype)
    if not _sfill:
        _bitpos, _angle = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('fill_angle', _angle)
        _bitpos, _sos = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('fill_scale_or_spacing', _sos)
        _bitpos, _dh = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('fill_doublehatch', _dh)
        _bitpos, _ndf = dwgutil.get_bit_short(data, _bitpos)
        _lines = []
        for _i in range(_ndf):
            _bitpos, _angle = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _x1 = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _y1 = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _ox = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _oy = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _nds = dwgutil.get_bit_short(data, _bitpos)
            _dashes = []
            for _j in range(_nds):
                _bitpos, _dl = dwgutil.get_bit_double(data, _bitpos)
                _dashes.append(_dl)
            _lines.append((_angle, _x1, _y1, _ox, _oy, _dashes))
        ent.setEntityData('fill_lines', _lines)
    if _pixel:
        _bitpos, _ps = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('pixel_size', _ps)
    _bitpos, _nsp = dwgutil.get_bit_long(data, _bitpos)
    if _nsp:
        _seedpts = []
        for _i in range(_nsp):
            _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
            _seedpts.append((_x, _y))
        ent.setEntityData('seed_points', _seedpts)
    _bitpos = tail_read(ent, data, _bitpos)
    if _allbounds:
        _boundaries = []
        for _i in range(_allbounds):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _boundaries.append(_handle)
        ent.setEntityData('boundary_handles', _boundaries)

def idbuffer_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _u = dwgutil.get_raw_char(data, _bitpos)
    # print "unknown char: %#02x" % _u
    _bitpos, _nids = dwgutil.get_bit_long(data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _nids:
        _handles = []
        for _i in range(_nids):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('objid_handles', _handles)

def image_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class_version', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('pt0', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('uvec', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('vvec', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('display_props', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('clipping', _flag)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('brightness', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('contrast', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('fade', _val)
    _bitpos, _cbt = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('clip_type', _cbt)
    if (_cbt == 1):
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('corner1', (_x, _y))
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('corner2', (_x, _y))
    else:
        _bitpos, _ncv = dwgutil.get_bit_long(data, _bitpos)
        _verts = []
        for _i in range(_ncv):
            _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
            _verts.append((_x, _y))
        ent.setEntityData('vertices', _verts)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('imagedef_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('imagedef_reactor_handle', _handle)

def imagedef_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _clsver = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class_version', _clsver)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _h = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _filepath = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('filepath', _filepath)
    _bitpos, _isloaded = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('is_loaded', _isloaded)
    _bitpos, _res = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('res_units', _res)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('pixel_width', _val)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('pixel_height', _val)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def imagedefreactor_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _clsver = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class version', _clsver)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def layer_index_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ts1 = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp1', _ts1)
    _bitpos, _ts2 = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp2', _ts2)
    _bitpos, _ne = dwgutil.get_bit_long(data, _bitpos)
    if _ne:
        _indicies = []
        for _i in range(_ne):
            _bitpos, _il = dwgutil.get_bit_long(data, _bitpos)
            _bitpos, _is = dwgutil.get_text_string(data, _bitpos)
            _indicies.append((_il, _is))
        ent.setEntityData('index_handles', _indicies)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    if _ne:
        _entries = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _entries.append(_handle)
        ent.setEntityData('entry_handles', _entries)

def layout_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('page_setup_name', _string)
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('printer_config', _string)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('plot_layout_flags', _val)
    _bitpos, _lm = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _bm = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _rm = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _tm = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('margins', (_lm, _bm, _rm, _tm))
    _bitpos, _pw = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _ph = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('paper_dim', (_pw, _ph))
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('paper_size', _string)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('plot_origin', (_x, _y))
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('paper_units', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('plot_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('plot_type', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('window_min', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('window_max', (_x, _y))
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('plot_view_name', _string)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('real_world_units', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('drawing_units', _val)
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('current_style_sheet', _string)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('scale_type', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale_factor', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('paper_image_origin', (_x, _y))
    _bitpos, _string = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('layout_name', _string)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('tab_order', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('layout_flag', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ucs_origin', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('layout_minima', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('layout_maxima', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ucs_x_axis', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ucs_y_axis', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('orthoview_type', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extmin', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extmax', (_x, _y, _z))
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('paperspace_block_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('last_active_viewport_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('base_ucs_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('named_ucs_handle', _handle)
    
def lwpline_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _flag = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flag', _flag)
    _cw = 0.0
    if (_flag & 0x4):
        _bitpos, _cw = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('const_width', _cw)
    _elev = 0.0
    if (_flag & 0x8):
        _bitpos, _elev = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _elev)
    _th = 0.0
    if (_flag & 0x2):
        _bitpos, _th = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _th)
    _nx = _ny = _nz = 0.0
    if (_flag & 0x1):
        _bitpos, _nx = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _ny = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _nz = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('normal', (_nx, _ny, _nz))
    _bitpos, _np = dwgutil.get_bit_long(data, _bitpos)
    _nb = 0
    if (_flag & 0x10):
        _bitpos, _nb = dwgutil.get_bit_long(data, _bitpos)
    _nw = 0
    if (_flag & 0x20):
        _bitpos, _nw = dwgutil.get_bit_long(data, _bitpos)
    _verticies = []
    _bitpos, _vx = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _vy = dwgutil.get_raw_double(data, _bitpos)
    # print "first vertex: (%g,%g)" % (_vx, _vy)
    _verticies.append((_vx, _vy))
    for _i in range((_np - 1)):
        _bitpos, _x = dwgutil.get_default_double(data, _bitpos, _vx)
        _bitpos, _y = dwgutil.get_default_double(data, _bitpos, _vy)
        _verticies.append((_x, _y))
        _vx = _x
        _vy = _y
    ent.setEntityData('verticies', _verticies)
    if _nb:
        _bulges = []
        for _i in range(_nb):
            _bitpos, _bulge = dwgutil.get_raw_double(data, _bitpos)
            _bulges.append(_bulge)
        ent.setEntityData('bulges', _bulges)
    if _nw:
        _widths = []
        for _i in range(_nw):
            _bitpos, _sw = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _ew = dwgutil.get_bit_double(data, _bitpos)
            _widths.append((_sw, _ew))
        ent.setEntityData('widths', _widths)
    _bitpos = tail_read(ent, data, _bitpos)

def rastervariables_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _clsver = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class_version', _clsver)
    _bitpos, _df = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('dispfrm', _df)
    _bitpos, _dq = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('dispqual', _dq)
    _bitpos, _units = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('units', _units)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def sortentstable_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ne = dwgutil.get_bit_long(data, _bitpos)
    # print "numentries: %d" % _ne
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('sort_handles', _handles)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    #
    # the spec says there is an owner handle here
    #
    # _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    # print "owner handle: " + str(_handle)
    if _ne:
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('obj_handles', _handles)

def spatial_filter_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _npts = dwgutil.get_bit_short(data, _bitpos)
    if _npts:
        _points = []
        for _i in range(_npts):
            _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
            _points.append((_x, _y))
        ent.setEntityData('points', _points)
    _bitpos, _ex = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _ey = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _ez = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_ex, _ey, _ez))
    _bitpos, _cx = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _cy = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _cz = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('clip_bound_origin', (_cx, _cy, _cz))
    _bitpos, _db = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('disp_bound', _db)
    _bitpos, _fc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('front_clip_on', _fc)
    _bitpos, _fd = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_dist', _fd)
    _bitpos, _bc = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('back_clip_on', _bc)
    _bitpos, _bd = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_dist', _bd)
    _invtr = array.array('d', 12 * [0.0])
    for _i in range(12):
        _bitpos, _invtr[_i] = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('inv_array', _invtr)
    _clptr = array.array('d', 12 * [0.0])
    for _i in range(12):
        _bitpos, _clptr[_i] = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('clip_array', _clptr)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('parent_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def spatial_index_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ts1 = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp1', _ts1)
    _bitpos, _ts2 = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp2', _ts2)
    #
    # fixme - lots of unknown stuff here
    # ...

def xrecord_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _ndb = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('data_bytes', _ndb)
    #
    # fixme - more stuff here ...
    #

_objprops = [
    (False, None), # Unused [0x00]
    (True, text_reader), # Text
    (True, attrib_reader), # Attrib
    (True, attdef_reader), # Attdef
    (True, block_reader), # Block
    (True, endblk_reader), # Endblk
    (True, seqend_reader), # Seqend
    (True, insert_reader), # Insert
    (True, minsert_reader), # Minsert [0x08]
    (False, None), # Skipped [0x09]
    (True, vertex2d_reader), # Vertex_2D
    (True, vertex3d_reader), # Vertex_3D
    (True, vertex_mesh_reader), # Vertex_mesh
    (True, vertex_pface_reader), # Vertex_pface
    (True, vertex_pface_face_reader), # Vertex_pface_face
    (True, polyline2d_reader), # Polyline_2D
    (True, polyline3d_reader), # Polyline_3D [0x10]
    (True, arc_reader), # Arc,
    (True, circle_reader), # Circle,
    (True, line_reader), # Line
    (True, dimord_reader), # Dimension_ord
    (True, dimlin_reader), # Dimension_lin
    (True, dimalign_reader), # Dimension_align
    (True, dimang3p_reader), # Dimension_angle_3pt
    (True, dimang2l_reader), # Dimension_angle_2ln [0x18]
    (True, dimrad_reader), # Dimension_radius
    (True, dimdia_reader), # Dimension_diameter
    (True, point_reader), # Point
    (True, face3d_reader), # Face3D
    (True, pface_reader), # Polyline_pface
    (True, mesh_reader), # Polyline_mesh
    (True, solid_reader), # Solid
    (True, trace_reader), # Trace [0x20]
    (True, shape_reader), # Shape
    (True, viewport_reader), # Viewport
    (True, ellipse_reader), # Ellipse
    (True, spline_reader), # Spline
    (True, rsb_reader), # Region
    (True, rsb_reader), # Solid3D
    (True, rsb_reader), # Body
    (True, ray_reader), # Ray [0x28]
    (True, xline_reader), # Xline
    (False, dict_reader), # Dictionary
    (False, None), # Skipped [0x2b]
    (True, mtext_reader), # Mtext
    (True, leader_reader), # Leader
    (True, tolerance_reader), # Tolerance
    (True, mline_reader), # Mline
    (False, block_control_reader), # Block control [0x30]
    (False, block_header_reader), # Block header
    (False, layer_control_reader), # Layer control
    (False, layer_reader), # Layer
    (False, shapefile_control_reader), # Style control
    (False, shapefile_reader), # Style
    (False, None), # Skipped [0x36]
    (False, None), # Skipped [0x37]
    (False, linetype_control_reader), # Linetype control [0x38]
    (False, linetype_reader), # Linetype
    (False, None), # Skipped [0x3a]
    (False, None), # Skipped [0x3b]
    (False, view_control_reader), # View control [0x3c]
    (False, view_reader), # View
    (False, ucs_control_reader), # UCS control,
    (False, ucs_reader), # UCS
    (False, vport_control_reader), # Vport control [0x40]
    (False, vport_reader), # Vport
    (False, appid_control_reader), # Appid control
    (False, appid_reader), # Appid
    (False, dimstyle_control_reader), # Dimstyle control
    (False, dimstyle_reader), # Dimstyle
    (False, vpentity_control_reader), # VP ENT HDR control
    (False, vpentity_reader), # VP ENT HDR
    (False, group_reader), # Group [0x48]
    (False, mlinestyle_reader), # Mlinestyle
    ]

_vobjmap = {
    'DICTIONARYVAR' : dictionaryvar_reader,
    'HATCH' : hatch_reader,
    'IDBUFFER' : idbuffer_reader,
    'IMAGE' : image_reader,
    'IMAGEDEF' : imagedef_reader,
    'IMAGEDEFREACTOR' : imagedefreactor_reader,
    'LAYER_INDEX' : layer_index_reader,
    'LAYOUT' : layout_reader,
    'LWPLINE' : lwpline_reader,
#     'OLE2FRAME' : ole2frame_reader,
    'RASTERVARIABLES' : rastervariables_reader,
    'SORTENTSTABLE' : sortentstable_reader,
    'SPATIAL_FILTER' : spatial_filter_reader,
    'SPATIAL_INDEX' : spatial_index_reader,
    'XRECORD' : xrecord_reader
    }

def get_object(dwg, offset):
    _handle = dwg.getHandle()
    _handle.seek(offset, 0)
    _size = dwgutil.get_modular_short(_handle)
    _data = array.array('B')
    _data.fromfile(_handle, _size)
    _ent = dwgbase.dwgEntity()
    # _ent.setEntityData('bitstream', data) # save the bitstream data
    _bitpos = 0
    _bitpos, _type = dwgutil.get_bit_short(_data, _bitpos)
    _ent.setType(_type)
    _bitpos, _objbsize = dwgutil.get_raw_long(_data, _bitpos)
    _ent.setEntityData('size_in_bits', _objbsize)
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    _ent.setHandle(_handle)
    _bitpos, _extdata = dwgutil.read_extended_data(_data, _bitpos)
    _ent.setEntityData('extended_data', _extdata)
    #
    # use the objprops table to determine if the _entity
    # has a graphics bit and the appropriate bitstream
    # decoding function
    #
    _gflag = False
    _reader = None
    if _type < len(_objprops):
        _gflag, _reader = _objprops[_type]
    if _gflag:
        _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
        if _val is True:
            _bitpos, _size = dwgutil.get_raw_long(_data, _bitpos)
            _bgsize = _size * 8
            _gidata = dwgutil.get_bits(_data, _bgsize, _bitpos)
            _ent.setEntityData('graphic_data', _gidata)
            _bitpos = _bitpos + _bgsize
    if _reader is not None:
        _reader(_ent, _data, _bitpos)
    else:
        _stype = dwg.getDxfName(_type)
        if _stype is not None:
            if _stype == 'HATCH': # where is the data kept?
                _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
            if _stype in _vobjmap:
                _vobjmap[_stype](_ent, _data, _bitpos)
    return _ent

def read_second_header(handle, offset):
    # print "read_second_header() ..."
    handle.seek(offset, 0)
    _at = handle.tell()
    # print "offset at %d [%#x]" % (_at, _at)
    _s = array.array('B')
    _s.fromfile(handle, 16)
    if _s[0] != 0xd4: raise ValueError, "_s[0] != 0xd4"
    if _s[1] != 0x7b: raise ValueError, "_s[1] != 0x7b"
    if _s[2] != 0x21: raise ValueError, "_s[2] != 0x21"
    if _s[3] != 0xce: raise ValueError, "_s[3] != 0xce"
    if _s[4] != 0x28: raise ValueError, "_s[4] != 0x28"
    if _s[5] != 0x93: raise ValueError, "_s[5] != 0x93"
    if _s[6] != 0x9f: raise ValueError, "_s[6] != 0x9f"
    if _s[7] != 0xbf: raise ValueError, "_s[7] != 0xbf"
    if _s[8] != 0x53: raise ValueError, "_s[8] != 0x53"
    if _s[9] != 0x24: raise ValueError, "_s[9] != 0x24"
    if _s[10] != 0x40: raise ValueError, "_s[10] != 0x40"
    if _s[11] != 0x09: raise ValueError, "_s[11] != 0x09"
    if _s[12] != 0x12: raise ValueError, "_s[12] != 0x12"
    if _s[13] != 0x3c: raise ValueError, "_s[13] != 0x3c"
    if _s[14] != 0xaa: raise ValueError, "_s[14] != 0xaa"
    if _s[15] != 0x01: raise ValueError, "_s[15] != 0x01"
    # _at = handle.tell()
    # print "offset at %d [%#x]" % (_at, _at)
    _size = struct.unpack('<l', handle.read(4))[0]
    # print "section size: %d" % _size
    _at = handle.tell()
    # print "second header data offset at %d [%#x]" % (_at, _at)
    _data = array.array('B')
    _data.fromfile(handle, (_size - 4)) # size includes itself in byte count
    # _at = handle.tell()
    # print "offset at %d [%#x]" % (_at, _at)
    _s.fromfile(handle, 16)
    if _s[16] != 0x2b: raise ValueError, "_s[16] != 0x2b"
    if _s[17] != 0x84: raise ValueError, "_s[17] != 0x84"
    if _s[18] != 0xde: raise ValueError, "_s[18] != 0xde"
    if _s[19] != 0x31: raise ValueError, "_s[19] != 0x31"
    if _s[20] != 0xd7: raise ValueError, "_s[20] != 0xd7"
    if _s[21] != 0x6c: raise ValueError, "_s[21] != 0x6c"
    if _s[22] != 0x60: raise ValueError, "_s[22] != 0x60"
    if _s[23] != 0x40: raise ValueError, "_s[23] != 0x40"
    if _s[24] != 0xac: raise ValueError, "_s[24] != 0xac"
    if _s[25] != 0xdb: raise ValueError, "_s[25] != 0xdb"
    if _s[26] != 0xbf: raise ValueError, "_s[26] != 0xbf"
    if _s[27] != 0xf6: raise ValueError, "_s[27] != 0xf6"
    if _s[28] != 0xed: raise ValueError, "_s[28] != 0xed"
    if _s[29] != 0xc3: raise ValueError, "_s[29] != 0xc3"
    if _s[30] != 0x55: raise ValueError, "_s[30] != 0x55"
    if _s[31] != 0xfe: raise ValueError, "_s[31] != 0xfe"
    _at = handle.tell()
    # print "offset at %d [%#x]" % (_at, _at)
    return _data

def decode_second_header(data):
    # print "decode_second_header() ..."
    _map = {}
    _bitpos = 0
    _bitpos, _loc = dwgutil.get_bit_long(data, _bitpos)
    # print "location: %d" % _loc
    # print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # A
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # C
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 1
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 1
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 2 or 4
    # print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0 in spec, not always in files ...
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    # print "val1: " + str(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    # print "val1: " + str(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    # print "val1: " + str(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    # print "val1: " + str(_val)
    # print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0x18 in spec
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0x78 in spec
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0x01 in spec
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # 0x04 for R13, 0x05 for R14, in spec
    # print "bitpos: %d" % _bitpos
    return _map
    #
    # bail out - some R15 drawings make it through reading the
    # class 0, class1, and class 2 stuff, others only make it
    # through reading class 0 and class 1 - these files don't
    # match at all the spec ...
    
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # class 0
    _bitpos, _haddr = dwgutil.get_bit_long(data, _bitpos)
    # print "header address: %d [%#x]" % (_haddr, _haddr)
    _bitpos, _hsize = dwgutil.get_bit_long(data, _bitpos)
    # print "header size: %d" % _hsize
    # print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # class 1
    _bitpos, _caddr = dwgutil.get_bit_long(data, _bitpos)
    # print "class address: %d [%#x]" % (_caddr, _caddr)
    _bitpos, _csize = dwgutil.get_bit_long(data, _bitpos)
    # print "class size: %d" % _csize
    # print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # class 2
    _bitpos, _omaddr = dwgutil.get_bit_long(data, _bitpos)
    # print "objmap address: %d [%#x]" % (_omaddr, _omaddr)
    _bitpos, _omsize = dwgutil.get_bit_long(data, _bitpos)
    # print "objmap size: %d" % _omsize
    # print "bitpos: %d" % _bitpos
    # return _map # bail out - R15 is different ...
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    # print "char: %#x" % _char # class 3
    _bitpos, _uaddr = dwgutil.get_bit_long(data, _bitpos)
    # print "unknown address: %d [%#x]" % (_uaddr, _uaddr)
    _bitpos, _usize = dwgutil.get_bit_long(data, _bitpos)
    # print "unknown size: %d" % _usize
    # print "bitpos: %d" % _bitpos
    _bitpos, _nrh = dwgutil.get_bit_short(data, _bitpos)
    # print "nrh: %d" % _nrh
    _bitpos, _recnum = dwgutil.get_bit_short(data, _bitpos)
    # print "num of following handle records: %d" % _recnum
    return _map
    # for _i in range(_recnum):
        # print "record %d" % _i
        # _bitpos, _sizeof = dwgutil.get_raw_char(data, _bitpos)
        # print "size of chars: %d" % _sizeof
        # _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
        # print "val: %d" % _val
        # _bitpos, _size = dwgutil.get_raw_char(data, _bitpos)
        # print "size chars: %d" % _size
    #
    # there is more stuff left in data that we ignore ...
    #
    return _map
