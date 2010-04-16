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
# read in an AutoCAD dwg file
#

import struct
import array
import sys

from PythonCAD.Generic import dwgbase
from PythonCAD.Generic import dwgutil

r14 = False # ugh, a global variable ...

def dump_info(handle):
    global r14
    _offsets = {}
    handle.seek(0, 0) # start of file
    _buf = handle.read(6)
    if _buf == 'AC1012':
        print "Autocad 13 format"
    elif _buf== 'AC1014':
        print "Autocad 14 format"
        r14 = True
    else:
        print "unknown format"
        return
    # print "offset at %#x" % handle.tell()
    _buf = array.array('B')
    _buf.fromfile(handle, 7)
    # if _buf[0] != 0:
        # print "buf[0] != 0"
    # if _buf[1] != 0:
        # print "buf[1] != 0"
    # if _buf[2] != 0:
        # print "buf[2] != 0"
    # if _buf[3] != 0:
        # print "buf[3] != 0"
    # if _buf[4] != 0:
        # print "buf[4] != 0"
    # if _buf[5] != 0: # ACADMAINTVER in Autocad 14
        # print "buf[5] != 0"
    # if _buf[6] != 1:
        # print "buf[6] != 1"
    print "offset at %#x" % handle.tell()
    #
    # ub1 and ub2 are unknown bytes
    #
    _image_seeker, _ub1, _ub2 = struct.unpack('<lBB', handle.read(6))
    if _image_seeker != 0:
        _offsets['IMAGE'] = _image_seeker
        _offset = handle.tell()
        _bmpdata, _wmfdata = read_image(handle, _image_seeker)
        handle.seek(_offset, 0)
    print "image seeker to %#x" % _image_seeker
    print "offset at %#x" % handle.tell()
    _codepage, _count = struct.unpack('<hl', handle.read(6))
    print "codepage: %d" % _codepage
    print "count: %d" % _count
    print "offset at %#x" % handle.tell()
    _recs = {}
    _sizes = {}
    for _i in range(_count):
        _rec, _seek, _size = struct.unpack('<bll', handle.read(9))
        print "record: %d" % _rec
        print "seek: %d" % _seek
        print "size: %d" % _size
        print "offset at %#x" % handle.tell()
        _recs[_rec] = (_seek, _size)
        if _rec == 0: # header
            print "hit header rec"
            _offsets['HEADER'] = _seek
            _sizes['HEADER'] = _size
        elif _rec == 1: # class
            print "hit class rec"
            _offsets['CLASS'] = _seek
            _sizes['CLASS'] = _size
        elif _rec == 2: # object map
            print "hit object map rec"
            _offsets['OBJECT_MAP'] = _seek
            _sizes['OBJECT_MAP'] = _size
        elif _rec == 3: # unknown
            print "hit unknown rec"
            _offsets['R14_UNKNOWN'] = _seek
            _sizes['R14_UNKNOWN'] = _size
        elif _rec == 4: # r14 where there may be data stored
            print "hit data rec"
            _offsets['R14_DATA'] = _seek
            _sizes['R14_DATA'] = _size
        elif _rec == 5: # occasionally exists
            print "hit rec5"
            _offsets['R14_REC5'] = _seek
            _sizes['R14_REC5'] = _size
        else:
            raise ValueError, "Unexpected record number %d" % _rec
    _crc = struct.unpack('<h', handle.read(2))[0]
    print "crc: %#x" % _crc
    _s = array.array('B')
    _s.fromfile(handle, 16)
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
    print "offset at %#x" % handle.tell()
    #
    # read header
    #
    print "reading header data ..."
    _offset = _offsets['HEADER']
    _size = _sizes['HEADER']
    _header_data = read_header(handle, _offset, _size)
    _hmap = decode_header_data(_header_data)
    _keys = _hmap.keys()
    _keys.sort()
    print "HEADER variables:"
    for _key in _keys:
        print "%s => %s" % (_key, str(_hmap[_key]))
    #
    # read class section
    #
    print "reading class data ..."
    _offset = _offsets['CLASS']
    _size = _sizes['CLASS']
    _class_data = read_class(handle, _offset, _size)
    print "class data offset: %d [%#x]" % (_offset, _offset)
    print "read %d bytes" % _size
    _cmap = decode_class_data(_class_data)
    #
    # read object section
    #
    print "reading object map data ..."
    _offset = _offsets['OBJECT_MAP']
    _size = _sizes['OBJECT_MAP']
    _sections = read_object_map(handle, _offset, _size)
    _objmap = decode_object_map(_sections)
    #
    # read the objects from the object map
    #
    _objects = read_objects(handle, _objmap, _cmap)
    #
    # read unknown section
    #
    print "reading unknown section ..."
    _offset = _offsets['R14_UNKNOWN']
    _size = _sizes['R14_UNKNOWN'] # apparently always 53 ...
    handle.seek(_offset, 0)
    _unknown_data = handle.read(_size)
    #
    # read second header - apparently this starts immediately
    # following the unknown section ...
    #
    print "reading second header ..."
    _offset = handle.tell()
    _second_data = read_second_header(handle, _offset)
    _second_map = decode_second_header(_second_data)

def initialize_dwg(dwg):
    _handle = dwg.getHandle()
    _handle.seek(0, 0)
    _buf = _handle.read(6)
    if _buf != 'AC1012':
        if _buf != 'AC1014':
            raise ValueError, "File not R13/R14 DWG format"
    _handle.seek(7, 1) # padding and a revision byte
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
        print "code: %#x" % _code
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
            raise ValueError, "unexpected code: %#x" % _code
    if _headerstart is not None and _headersize is not None:
        _handle.seek(_headerstart, 0)
        _headerdata.fromfile(_handle, _headersize)
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
        dwg.setImageData('BMP', _bmpdata)
    if _wmfdata is not None:
        dwg.setImageData('WMF', _wmfdata)

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
    # print "bit position: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL2', _val)
    # print "bit position: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL3', _val)
    # print "bit position: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('VAL4', _val)
    # print "bit position: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING1', _string)
    # print "bit position: %d" % _bitpos
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING2', _string)
    # print "bit position: %d" % _bitpos
    _bitpos, _str = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING3', _string)
    # print "bit position: %d" % _bitpos
    _bitpos, _str = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('STRING4', _string)
    _bitpos, _val = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('LONG1', _val)
    _bitpos, _val = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('LONG2', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHORT1', _val)
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('HANDLE1', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMASO', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSHO', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSAV', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PLINEGEN', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('ORTHOMODE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('REGENMODE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('FILLMODE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('QTEXTMODE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PSLTSCALE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('LIMCHECK', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('BLIPMODE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('USER_TIMER', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('SKPOLY', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('ANGDIR', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('SPLFRAME', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('ATTREQ', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('ATTDIA', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('MIRRTEXT', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('WORLDVIEW', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('WIREFRAME', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('TILEMODE', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PLIMCHECK', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('VISRETAIN', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DELOBJ', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DISPSILH', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('PELLISE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    if dwg.getVersion() == 'R14':
        dwg.setHeader('PROXYGRAPH', _val)
    else:
        dwg.setHeader('SAVEIMAGES', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DRAGMODE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('TREEDEPTH', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('LUNITS', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('LUPREC', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('AUNITS', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('AUPREC', _val)
    # print "bitpos at osmode: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('OSMODE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('ATTMODE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('COORDS', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('PDMODE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('PICKSTYLE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI1', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI2', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI3', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI4', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('USERI5', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SPLINESEGS', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFU', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFV', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFTYPE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFTAB1', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SURFTAB2', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SPLINETYPE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHADEDGE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('SHADEDIF', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('UNITMODE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('MAXACTVP', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('ISOLINES', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('CMLJUST', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('TEXTQLTY', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('LTSCALE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('TEXTSIZE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('TRACEWID', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('SKETCHINC', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('FILLETRAD', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('THICKNESS', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('ANGBASE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PDSIZE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PLINEWID', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR1', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR2', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR3', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR4', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('USERR5', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERA', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERB', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERC', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CHAMFERD', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('FACETRES', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CMLSCALE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('CELTSCALE', _val)
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('MENUNAME', _val)
    _bitpos, _val1 = dwgutil.get_bit_long(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDCREATE', (_val1, _val2))
    _bitpos, _val1 = dwgutil.get_bit_long(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDUPDATE', (_val1, _val2))
    _bitpos, _val1 = dwgutil.get_bit_long(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDINDWG', (_val1, _val2))
    _bitpos, _val1 = dwgutil.get_bit_long(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_long(_data, _bitpos)
    dwg.setHeader('TDUSRTIMER', (_val1, _val2))
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('CECOLOR', _val)
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
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_INSBASE', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_EXTMIN', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_EXTMAX', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('PSPACE_LIMMIN', (_val1, _val2))
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('PSPACE_LIMMAX', (_val1, _val2))
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_ELEVATION', _val)
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSORG', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSXDIR', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSYDIR', (_val1, _val2, _val3))
    _bitpos,  _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PSPACE_UCSNAME', _handle)
    #print "bitpos: %d" % _bitpos
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_INSBASE', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_EXTMIN', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_EXTMAX', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('MSPACE_LIMMIN', (_val1, _val2))
    _bitpos, _val1 = dwgutil.get_raw_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_raw_double(_data, _bitpos)
    dwg.setHeader('MSPACE_LIMMAX', (_val1, _val2))
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_ELEVATION', _val)
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSORG', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSXDIR', (_val1, _val2, _val3))
    _bitpos, _val1 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val2 = dwgutil.get_bit_double(_data, _bitpos)
    _bitpos, _val3 = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSYDIR', (_val1, _val2, _val3))
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('MSPACE_UCSNAME', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTOL', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMLIM', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTIH', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTOH', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSE1', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSE2', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMALT', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTOFL', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSAH', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMTIX', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSOXD', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMALTD', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMZIN', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSD1', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMSD2', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMTOLJ', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMJUST', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMFINT', _val)
    _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
    dwg.setHeader('DIMUPT', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMTZIN', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMMALTZ', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMMALTTZ', _val)
    _bitpos, _val = dwgutil.get_raw_char(_data, _bitpos)
    dwg.setHeader('DIMTAD', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMUNIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMAUNIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMDEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMTDEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTU', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMALTTD', _val)
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('DIMTXSTY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMSCALE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMASZ', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMEXO', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMDLI', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMEXE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMAND', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMDLE', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTP', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTM', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTXT', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMCEN', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMSZ', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMALTF', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMLFAC', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTVP', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMTFAC', _val)
    _bitpos, _val = dwgutil.get_bit_double(_data, _bitpos)
    dwg.setHeader('DIMGAP', _val)
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMPOST', _val)
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMAPOST', _val)
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMBLK', _string)
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMBLK1', _string)
    _bitpos, _string = dwgutil.get_text_string(_data, _bitpos)
    dwg.setHeader('DIMBLK2', _string)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMCLRD', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMCLRE', _val)
    _bitpos, _val = dwgutil.get_bit_short(_data, _bitpos)
    dwg.setHeader('DIMCLRT', _val)
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
    dwg.setHeader('VIEWPORT_ENTITY_HEADER', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('ACAD_GROUP_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('ACAD_MLINE_DICTIONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('NAMED_OBJECT_DICTONARY', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('PAPER_BLOCK_RECORD', _handle)
    # print "bitpos: %d" % _bitpos
    _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
    dwg.setHeader('MODEL_BLOCK_RECORD', _handle)
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

def r1314_read_objects(dwg):
    global r14
    _version = dwg.getVersion()
    if _version == 'R14':
        r14 = True
    _handle = dwg.getHandle()
    _offset, _size = dwg.getOffset('OBJECTS')
    _sections = read_object_map(_handle, _offset, _size)
    _omap = decode_object_map(_sections)
    _classes = dwg.getClassKeys()
    _cmap = {}
    for _class in _classes:
        _cmap[_class] = dwg.getClass(_class)
    for _obj in read_objects(_handle, _omap, _cmap):
        dwg.setObject(_obj)

def read_object_map(handle, offset, size):
    # print "read_object_map() ..."
    handle.seek(offset, 0)
    _at = handle.tell()
    # print "offset at %d [%#x]" % (_at, _at)
    _read = True
    _sections = []
    while _read:
        # print "reading section ..."
        _secdata = array.array('B')
        _size = struct.unpack('>h', handle.read(2))[0]
        # print "section size: %d" % _size
        if _size == 2:
            _read = False
        _secdata.fromfile(handle, _size)
        _sections.append(_secdata)
    return _sections

def decode_object_map(seclist):
    _map = {}
    #
    # the spec says 'last_handle' and 'last_loc' are initialized outside
    # the outer for loop - postings on OpenDWG forum say these variables
    # must be initialized for each section
    #
    _i = 0
    for _sec in seclist:
        _last_handle = 0
        _last_loc = 0
        _bitpos = 0
        _seclen = len(_sec)
        if _seclen == 2: # section of just CRC
            break
        _bitmax = (_seclen - 2) * 8 # remove two bytes for section CRC
        while  _bitpos < _bitmax:
            # print "i: %d" % _i
            # print "bitpos: %d" % _bitpos
            _bitpos, _hoffset = dwgutil.get_modular_char(_sec, _bitpos)
            # print "hoffset: %d" % _hoffset
            _last_handle = _last_handle + _hoffset
            # print "last_handle: %d [%#x]" % (_last_handle, _last_handle)
            # print "bitpos: %d" % _bitpos
            _bitpos, _foffset = dwgutil.get_modular_char(_sec, _bitpos)
            # print "foffset: %d" % _foffset
            _last_loc = _last_loc + _foffset
            # print "last loc: %d [%#x]" % (_last_loc, _last_loc)
            _map[_i] = (_last_handle, _foffset, _last_loc)
            # print "object: %d; mapping: %s" % (_i, str(_map[_i]))
            # print "bitpos before incrementing i: %d" % _bitpos
            _i = _i + 1
    return _map

#
# read the common parts at the start of an entity

def header_read(ent, data, offset):
    _bitpos = offset
    _mode = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    ent.setMode(_mode)
    _bitpos, _rnum = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_rnum)
    _bitpos, _islayer = dwgutil.test_bit(data, _bitpos)
    ent.setIsLayerByLinetype(_islayer)
    _bitpos, _nolinks = dwgutil.test_bit(data, _bitpos)
    ent.setNoLinks(_nolinks)
    _bitpos, _color = dwgutil.get_bit_short(data, _bitpos)
    ent.setColor(_color)
    _bitpos, _ltscale = dwgutil.get_bit_double(data, _bitpos)
    ent.setLinetypeScale(_ltscale)
    _bitpos, _invis = dwgutil.get_bit_short(data, _bitpos)
    ent.setInvisiblity(_invis)
    return _bitpos

#
# read the common parts at the end of many entities
#
        
def tail_read(ent, data, offset):
    _bitpos = offset
    if ent.getMode() == 0x0:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setSubentity(_handle)
    for _i in range(ent.getNumReactors()):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setLayer(_handle)
    if ent.getIsLayerByLinetype() is False:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setLinetype(_handle)
    if ent.getNoLinks() is False:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setPrevious(_handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setNext(_handle)
    return _bitpos

#
# read the various entities stored in the DWG file
#

def text_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('alignment_point', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('generation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('halign', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('valign', _val)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def attrib_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('alignment_point', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('generation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('halign', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('valign', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('tag', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('field_length', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def attdef_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('insertion_point', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('alignment_point', (_x, _y))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('generation', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('halign', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('valign', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('tag', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('field_length', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('prompt', _text)
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
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _val)
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
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _hasattr = dwgutil.test_bit(data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('column_count', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('row_count', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('column_spacing', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('row_spacing', _val)
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
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('bulge', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('tangent_dir', _val)
    _bitpos = tail_read(ent, data, _bitpos)

def vertex3d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def vertex_mesh_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def vertex_pface_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('point', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def vertex_pface_face_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _v1 = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_short(data, _bitpos)
    _bitpos, _v4 = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('points', (_v1, _v2, _v3, _v4))
    _bitpos = tail_read(ent, data, _bitpos)

def polyline2d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('curve_type', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_width', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_width', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('first_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('last_vertex_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('seqend_handle', _handle)

def polyline3d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('spline_flags', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('closed_flags', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def line_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('p1', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('p2', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_v1, _v2, _v3))
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags2', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_v1, _v2, _v3))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_ln_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('dimension_rotation', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_v1, _v2, _v3))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_ln_rotation', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_v1, _v2, _v3))
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('16-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('13-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('14-pt', (_v1, _v3, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_v1, _v2, _v3))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('leader_length', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('text_rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('horiz_dir', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_scale', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ins_rotation', _val)
    _bitpos, _v1 = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('12-pt', (_v1, _v2))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('10-pt', (_v1, _v2, _v3))
    _bitpos, _v1 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v2 = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _v3 = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('15-pt', (_v1, _v2, _v3))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('leader_length', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('x_axis_angle', _val)
    _bitpos = tail_read(ent, data, _bitpos)

def face3d_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('corner1', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('corner2', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('corner3', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('corner4', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos = tail_read(ent, data, _bitpos)

def pface_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('vertex_count', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('face_count', _val)
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
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('curve_type', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('m_verticies', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('n_verticies', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('m_density', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('n_density', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
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
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos = tail_read(ent, data, _bitpos)

def trace_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('rotation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('shape_number', _val)
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
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('vport_entity_handle', _handle)

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
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('degree', _val)
    _nknots = _nctlpts = _nfitpts = 0
    _weight = False
    if _sc == 2:
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('fit_tolerance', _val)
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
        _bitpos, _val = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('rational', _val)
        _bitpos, _val = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('closed', _val)
        _bitpos, _val = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('periodic', _val)
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('knot_tolerance', _val)
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('control_tolerance', _val)
        _bitpos, _nknots = dwgutil.get_bit_long(data, _bitpos)
        _bitpos, _nctlpts = dwgutil.get_bit_long(data, _bitpos)
        _bitpos, _weight = dwgutil.test_bit(data, _bitpos)
    else:
        raise ValueError, "Unexpected scenario: %d" % _sc
    if _nknots:
        _knots = []
        for _i in range(_nknots):
            _bitpos, _knot = dwgutil.get_bit_double(data, _bitpos)
            _knots.append(_knot)
        ent.setEntityData('knot_points', _knots)
    if _nctlpts:
        _ctrlpts = []
        _weights = []
        for _i in range(_nctlpts):
            _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
            _ctrlpts.append((_x, _y, _z))
            if _weight:
                _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
                _weights.append(_val)
        ent.setEntityData('control_points', _ctrlpts)
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
    if ent.getVersion() == 'R14':
        _bitpos, _u = dwgutil.get_raw_char(data, _bitpos)
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
    ent.setEntityData('x_axis_dir', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('attachment', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('drawing_dir', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('ext_width', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('text', _text)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('style_handle', _handle)

def leader_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos) # unknown
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('annotation_type', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('path_type', _val)
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
    ent.setEntityData('offset_block_insp_pt', (_x, _y, _z))
    #
    # the following unknown is only in R14 ...
    #
    if ent.getVersion() == 'R14':
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('dimgap', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('box_height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('box_width', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('hooklineoxdir', _val) # ???
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('arrowhead_on', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('arrowhead_type', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('dimasz',_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos) # unknown
    _bitpos, _val = dwgutil.test_bit(data, _bitpos) # unknown
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos) # unknown
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('by_block_color', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos) # unknown
    _bitpos, _val = dwgutil.test_bit(data, _bitpos) # unknown
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('associated_annotation_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)

def tolerance_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos) # unknown
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('dimgap', _val) # maybe not???
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
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos) # should this be text_string?
    ent.setEntityData('text', _val)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('dimstyle_handle', _handle)

def mline_reader(ent, data, offset):
    _bitpos = offset
    _bitpos = header_read(ent, data, _bitpos)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('scale', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('justification', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('base_point', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('open_closed', _val)
    _bitpos, _lis = dwgutil.get_raw_char(data, _bitpos)
    _bitpos, _nv = dwgutil.get_bit_short(data, _bitpos)
    _points = []
    for _i in range(_nv):
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _vertex = (_x, _y, _z)
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y= dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _direction = (_x, _y, _z)
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
        _miter_dir = (_x, _y, _z)
        _lines = []
        for _j in range(_lis):
            _bitpos, _ns = dwgutil.get_bit_short(data, _bitpos)
            _segparms = []
            for _k in range(_ns):
                _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
                _segparms.append(_val)
            _bitpos, _na = dwgutil.get_bit_short(data, _bitpos)
            _fillparms = []
            for _k in range(_na):
                _bitpos, _afp = dwgutil.get_bit_double(data, _bitpos)
                _fillparms.append(_afp)
            _lines.append((_segparms, _fillparms))
        _points.append((_vertex, _direction, _miter_dir, _lines))
    ent.setEntityData('points', _points)
    _bitpos = tail_read(ent, data, _bitpos)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('mline_style_handle', _handle)

def block_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_val)
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
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('anonymous', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('has_attrs', _val)
    _bitpos, _bxref = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('blk_is_xref', _bxref)
    _bitpos, _xover = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xrefoverlaid', _xover)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('base_point', (_x, _y, _z))
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('xref_pname', _text)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('block_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('block_handle', _handle)
    if not _bxref and not _xover:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('first_entity_handle', _handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('last_entity_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('endblk_handle', _handle)

def layer_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_val)
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
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('frozen', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('on', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('frz_in_new', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('locked', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('color', _val)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('layer_control_handle', _handle)
    for _i in range(ent.getNumReactors()):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('linetype', _handle)

def shapefile_control_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_val)
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
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('vertical', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('shape_file', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('fixed_height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('fixed_width', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('oblique_angle', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('generation', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('last_height', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('font_name', _text)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('big_font_name', _text)
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

def linetype_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('description', _text)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('pattern_length', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('alignment', _val)
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
    _strings = dwgutil.get_bits(data, 256, _bitpos) # unknown ?
    _bitpos = _bitpos + 256
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('ltype_control_handle', _handle)
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
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_height', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('view_width', _val)
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
    ent.setEntityData('twist_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('lens_length', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_clip', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_clip', _val)
    _val = dwgutil.get_bits(data, 4, _bitpos)
    _bitpos = _bitpos + 4
    ent.setEntityData('view_control_flags', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('pspace_flag', _val)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('view_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)

def ucs_control_reader(ent, data, offset):
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
        ent.setEntityData('ucs_handles', _handles)

def ucs_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
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
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('ucs_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)

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
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
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
    ent.setEntityData('twist_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('lens_length', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_clip', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_clip', _val)
    _val = dwgutil.get_bits(data, 4, _bitpos)
    _bitpos = _bitpos + 4
    ent.setEntityData('vport_flags', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('lower_left', (_x, _y))
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('upper_right', (_x, _y))
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('ucsfollow', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('circle_zoom', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('fast_zoom', _val)
    _val = dwgutil.get_bits(data, 2, _bitpos)
    _bitpos = _bitpos + 2
    ent.setEntityData('ucsicon', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('grid_status', _val)
    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('grid_spacing', (_x, _y))
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('snap_status', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('snap_style', _val)
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
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('vport_control_handle', _handle)
    for _i in range(_nr):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('null_handle', _handle)

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
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
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
        ent.setEntityData('dimstyle_handles', _handles)

def dimstyle_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTOL', _val)
    _bitpos, _flag = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMLIM', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTIH', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTOH', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSE1', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSE2', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMALT', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTOFL', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSAH', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMTIX', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSOXD', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMALTD', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMZIN', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSD1', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMSD2', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMTOLJ', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMJUST', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMFIT', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('DIMUPT', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMTZIN', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMALTZ', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMALTTZ', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('DIMTAD', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMUNIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMAUNIT', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMDEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMTDEC', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTU', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMALTTD', _val)
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
    ent.setEntityData('DIMAND', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMDLE', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTP', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTM', _val)
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
    ent.setEntityData('DIMTVP', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMTFAC', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('DIMGAP', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMPOST', _text)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMAPOST', _text)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMBLK', _text)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMBLK1', _text)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('DIMBLK2', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMCLAD', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMCLRE', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('DIMCLRT', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos) # unknown
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

def vpentity_control_reader(ent, data, offset):
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
        ent.setEntityData('vpentity_handles', _handles)

def vpentity_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('64-flag', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('xrefplus', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('xdep', _val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('1-flag', _val)
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
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('unnamed', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('selectable', _val)
    _bitpos, _nh = dwgutil.get_bit_long(data, _bitpos)
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
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('description', _text)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flags', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('fill_color', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('start_angle', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('end_angle', _val)
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
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('intval', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos) # spec says bit short
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
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('z_coord', _val)
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('name', _text)
    _bitpos, _solid_fill = dwgutil.test_bit(data, _bitpos)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('associative', _val)
    _bitpos, _np = dwgutil.get_bit_long(data, _bitpos)
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
                _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
                _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
                _bulge = None
                if (_bulges):
                    _bitpos, _bulge = dwgutil.get_bit_double(data, _bitpos)
                _segs.append((_x, _y, _bulge))
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
                    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _r = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _sa = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _ea = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _isccw = dwgutil.test_bit(data, _bitpos)
                    _segs.append(('arc', _x, _y, _r, _sa, _ea, _isccw))
                elif (_pts == 3): # ELLIPTICAL ARC
                    _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _xe = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _ye = dwgutil.get_raw_double(data, _bitpos)
                    _bitpos, _ratio = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _sa = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _ea = dwgutil.get_bit_double(data, _bitpos)
                    _bitpos, _isccw = dwgutil.test_bit(data, _bitpos)
                    _segs.append(('elliptical_arc', _x, _y, _xe, _ye, _ratio, _sa, _ea, _isccw))
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
                        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
                        _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
                        _weight = None
                        if (_israt):
                            _bitpos, _weight = dwgutil.get_bit_double(data, _bitpos)
                        _ctlpts.append((_x, _y, _weight))
                    _segs.append(('spline', _israt, _isper, _knots, _ctlpts))
                else:
                    raise ValueError, "Unexpected path type: %d" % _pts
            _paths.append(('stdpath', _segs))        
        _bitpos, _nbh = dwgutil.get_bit_long(data, _bitpos)
        _allbounds = _allbounds + _nbh
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('style', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('pattern_type', _val)
    if not _solid_fill:
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('fill_angle', _val)
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('fill_scale_or_spacing', _val)
        _bitpos, _val = dwgutil.test_bit(data, _bitpos)
        ent.setEntityData('file_doublehatch', _val)
        _bitpos, _ndf = dwgutil.get_bit_short(data, _bitpos)
        _lines = []
        for _i in range(_ndf):
            _bitpos, _angle = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _xo = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _yo = dwgutil.get_bit_double(data, _bitpos)
            _bitpos, _nds = dwgutil.get_bit_short(data, _bitpos)
            _dashes = []
            for _j in range(_nds):
                _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
                ent.setEntityData('dashlength', _val)
            _lines.append((_angle, _x, _y, _xo, _yo, _dashes))
        ent.setEntityData('fill_lines', _lines)                
    if _pixel:
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
        ent.setEntityData('pixel_size', _val)
    _bitpos, _nsp = dwgutil.get_bit_long(data, _bitpos)
    if _nsp:
        _points = []
        for _i in range(_nsp):
            _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
            _points.append((_x, _y))
        ent.setEntityData('seed_points', _points)
    for _i in range(ent.getNumReactors()):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.addReactor(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setEntityData('layer_handle', _handle)
    if ent.getIsLayerByLinetype() is False:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setEntityData('linetype_handle', _handle)
    if ent.getNoLinks() is False:
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setPrevious(_handle)
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        ent.setNext(_handle)
    _bounds = []
    for _i in range(_allbounds):
        _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
        _bounds.append(_handle)
    if len(_bounds):
        ent.setEntityData('boundary_handles', _bounds)

def idbuffer_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos) # unknown
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
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('clipping', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('brightness', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('contrast', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('fade', _val)
    _bitpos, _cbt = dwgutil.get_bit_short(data, _bitpos)
    if (_cbt == 1):
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('corner1', (_x, _y))
        _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
        ent.setEntityData('corner2', (_x, _y))
    else:
        _bitpos, _ncv = dwgutil.get_bit_long(data, _bitpos)
        if _ncv:
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
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class_version', _val)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('width', _val)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('height', _val)
    _bitpos, _text = dwgutil.get_text_string(data, _bitpos)
    ent.setEntityData('filepath', _text)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setEntityData('is_loaded', _val)
    _bitpos, _val = dwgutil.get_raw_char(data, _bitpos)
    ent.setEntityData('res_units', _val)
    _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
    ent.setEntityData('pixel_width', _val)
    _bitpos, _ph = dwgutil.get_raw_double(data, _bitpos)
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
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class_version', _val)
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
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp1', _val)
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp2', _val)
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
        _handles = []
        for _i in range(_ne):
            _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
            _handles.append(_handle)
        ent.setEntityData('entry_handles', _handles)

def lwpline_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setIsLayerByLinetype(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    ent.setNoLinks(_val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setColor(_val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setLinetypeScale(_val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setInvisiblity(_val)
    _bitpos, _flag = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('flag', _flag)
    _val = 0.0
    if (_flag & 0x4):
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('const_width', _val)
    _val = 0.0
    if (_flag & 0x8):
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('elevation', _val)
    _val = 0.0
    if (_flag & 0x2):
        _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('thickness', _val)
    _x = _y = _z = 0.0
    if (_flag & 0x1):
        _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
        _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('normal', (_x, _y, _z))
    _bitpos, _np = dwgutil.get_bit_long(data, _bitpos)
    _nb = 0
    if (_flag & 0x10):
        _bitpos, _nb = dwgutil.get_bit_long(data, _bitpos)
    _nw = 0
    if (_flag & 0x20):
        _bitpos, _nw = dwgutil.get_bit_long(data, _bitpos)
    if _np:
        _points = []
        for _i in range(_np):
            _bitpos, _x = dwgutil.get_raw_double(data, _bitpos)
            _bitpos, _y = dwgutil.get_raw_double(data, _bitpos)
            _points.append((_x, _y))
        ent.setEntityData('points', _points)
    if _nb:
        _bulges = []
        for _i in range(_nb):
            _bitpos, _val = dwgutil.get_raw_double(data, _bitpos)
            _bulges.append(_val)
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
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('class_version', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('dispfrm', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('dispqual', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('units', _val)
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
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('extrusion', (_x, _y, _z))
    _bitpos, _x = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _y = dwgutil.get_bit_double(data, _bitpos)
    _bitpos, _z = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('clip_bound_origin', (_x, _y, _z))
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('disp_bound', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('front_clip_on', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('front_dist', _val)
    _bitpos, _val = dwgutil.get_bit_short(data, _bitpos)
    ent.setEntityData('back_clip_on', _val)
    _bitpos, _val = dwgutil.get_bit_double(data, _bitpos)
    ent.setEntityData('back_dist', _val)
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
        ent.addReactors(_handle)
    _bitpos, _handle = dwgutil.get_handle(data, _bitpos)
    ent.setXdicobj(_handle)

def spatial_index_reader(ent, data, offset):
    _bitpos = offset
    _bitpos, _nr = dwgutil.get_bit_long(data, _bitpos)
    ent.setNumReactors(_nr)
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp1', _val)
    _bitpos, _val = dwgutil.get_bit_long(data, _bitpos)
    ent.setEntityData('timestamp2', _val)
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
    (True, None), # Unused [0x00]
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
    'LWPLINE' : lwpline_reader,
#     'OLE2FRAME' : ole2frame_reader,
    'RASTERVARIABLES' : rastervariables_reader,
    'SORTENTSTABLE' : sortentstable_reader,
    'SPATIAL_FILTER' : spatial_filter_reader,
    'SPATIAL_INDEX' : spatial_index_reader,
    'XRECORD' : xrecord_reader
    }

def read_objects(handle, objmap, cmap):
    # print "read_objects() ..."
    #
    # use the classmap to tie the variable object numbers
    # to the type of object for use in the vobjmap dict
    _vmap = {}
    for _key in cmap.keys():
        _type = cmap[_key][3] # classdxfclassname field
        _vmap[_key] = _type
        # print "mapping type %d to %s" % (_key, _type)
    _objkeys = objmap.keys()
    _objkeys.sort()
    _objlist = []
    for _obj in _objkeys:
        _ent = dwgbase.dwgEntity()
        _last_handle, _foffset, _last_loc = objmap[_obj]
        handle.seek(_last_loc, 0) # use absolete offset
        _size = dwgbase.get_modular_short(handle)
        _data = array.array('B')
        _data.fromfile(handle, _size)
        # _ent.setEntityData('bitstream', _data)
        _bitpos = 0
        _bitpos, _type = dwgutil.get_bit_short(_data, _bitpos)
        _ent.setType(_type)
        # print "bitpos: %d" % _bitpos
        _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
        _ent.setHandle(_handle)
        # print "bitpos: %d" % _bitpos
        _eexdata = []
        while True:
            _bitpos, _exsize = dwgutil.get_bit_short(_data, _bitpos)
            # print "extended data size: %d" % _exsize
            if _exsize == 0:
                break
            # print "bitpos: %d" % _bitpos
            _bitpos, _handle = dwgutil.get_handle(_data, _bitpos)
            # print "eed handle: " + str(_handle)
            _count = 0
            _eedata = []
            while (_count < _exsize):
                # print "count: %d" % _count
                _bitpos, _cb = dwgutil.get_raw_char(_data, _bitpos)
                # print "code byte: %#x" % _cb
                _count = _count + 1
                if _cb == 0x0:
                    _bitpos, _slen = dwgutil.get_raw_char(_data, _bitpos)
                    _bitpos, _cp = dwgutil.get_raw_short(_data, _bitpos)
                    # print "code page: %d" % _cp
                    _chars = []
                    for _i in range(_slen):
                        _bitpos, _char = dwgutil.get_raw_char(_data, _bitpos)
                        _chars.append(chr(_char))
                    _string = "".join(_chars)
                    _eedata.append(_string)
                    _count = _count + 3 + _slen
                elif _cb == 0x1:
                    raise ValueError, "Invalid EEX code byte: 0x1"
                elif _cb == 0x2:
                    _bitpos, _char = dwgutil.get_raw_char(_data, _bitpos)
                    if _char == 0x0:
                        _eedata.append("{")
                    elif _char == 0x1:
                        _eedata.append("}")
                    else:
                        raise ValueError, "Unexpected EEX char: %#02x" % _char
                    _count = _count + 1
                elif _cb == 0x3:
                    # print "layer table reference"
                    _chars = []
                    for _i in range(8):
                        _bitpos, _char = dwgutil.get_raw_char(_data, _bitpos)
                        _chars.append(_char)
                    _eedata.append(_chars)
                    _count = _count + 8
                elif _cb == 0x4:
                    # print "binary chunk"
                    _bitpos, _len = dwgutil.get_raw_char(_data, _bitpos)
                    _chars = []
                    for _i in range(_len):
                        _bitpos, _char = dwgutil.get_raw_char(_data, _bitpos)
                        _chars.append(_char)
                    _eedata.append(_chars)
                    _count = _count + 1 + _len
                elif _cb == 0x5:
                    # print "entity handle reference"
                    _chars = []
                    for _i in range(8):
                        _bitpos, _char = dwgutil.get_raw_char(_data, _bitpos)
                        _chars.append(_char)
                    _eedata.append(_chars)
                    _count = _count + 8
                elif (0xa <= _cb <= 0xd):
                    # print "three doubles"
                    _bitpos, _d1 = dwgutil.get_raw_double(_data, _bitpos)
                    _bitpos, _d2 = dwgutil.get_raw_double(_data, _bitpos)
                    _bitpos, _d3 = dwgutil.get_raw_double(_data, _bitpos)
                    _eedata.append((_d1, _d2, _d3))
                    _count = _count + 24
                elif (0x28 <= _cb <= 0x2a):
                    # print "one double"
                    _bitpos, _d = dwgutil.get_raw_double(_data, _bitpos)
                    _eedata.append(_d)
                    _count = _count + 8
                elif _cb == 0x46:
                    # print "short int"
                    _bitpos, _short = dwgutil.get_raw_short(_data, _bitpos)
                    _eedata.append(_short)
                    _count = _count + 2
                elif _cb == 0x47:
                    # print "long int"
                    _bitpos, _long = dwgutil.get_raw_long(_data, _bitpos)
                    _eedata.append(_long)
                    print "long: %d" % _long
                    _count = _count + 4
                else:
                    raise ValueError, "Unexpected code byte: %#02x" % _cb
        #
        # These objects may have the graphics bit
        #
        _gflag = False
        _reader = None
        if _type < len(_objflags):
            _gflag, _reader = _objflags[_type]
        if _gflag:
            _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
            # print "graphic flag: " + str(_val)
            # print "bitpos: %d" % _bitpos
            if _val is True:
                _bitpos, _gsize = dwgutil.get_raw_long(_data, _bitpos)
                # print "graphic data bit size: %d" % _gsize
                # print "bitpos: %d" % _bitpos
                _bgsize = _gsize * 8
                _gidata = dwgutil.get_bits(_data, _bgsize, _bitpos)
                _bitpos = _bitpos + _bgsize
                _ent.setEntityData('graphic_data', _gidata)
        _bitpos, _objbsize = dwgutil.get_raw_long(_data, _bitpos)
        # print "object data size in bits: %d" % _objbsize
        # print "bitpos: %d" % _bitpos
        if _reader is not None:
            _reader(_ent, _data, _bitpos)
        elif _type in _vmap:
            _stype = _vmap[_type]
            # print "type: %d => %s" % (_type, _stype)
            if _stype == 'HATCH': # where is the data kept?
                _bitpos, _val = dwgutil.test_bit(_data, _bitpos)
                # print "graphic flag: " + str(_val)
            if _stype in _vobjmap:
                _vobjmap[_stype](_ent, _data, _bitpos)
        else:
            # print "unhandled object type: %d" % _type
            pass
        _objlist.append(_ent)
    return _objlist

def get_object(dwg, offset):
    _handle = dwg.getHandle()
    _handle.seek(offset, 0)
    _size = dwgutil.get_modular_short(_handle)
    _data = array.array('B')
    _data.fromfile(_handle, _size)
    _ent = dwgbase.dwgEntity()
    # _ent.setEntityData('bitstream', data) # save the bitstream data
    _ent.setVersion(dwg.getVersion())
    _bitpos = 0
    _bitpos, _type = dwgutil.get_bit_short(_data, _bitpos)
    _ent.setType(_type)
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
    _bitpos, _objbsize = dwgutil.get_raw_long(_data, _bitpos)
    _ent.setEntityData('size_in_bits', _objbsize)
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
    print "read_second_header() ..."
    handle.seek(offset, 0)
    _at = handle.tell()
    print "offset at %d [%#x]" % (_at, _at)
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
    print "section size: %d" % _size
    _at = handle.tell()
    print "second header data offset at %d [%#x]" % (_at, _at)
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
    print "offset at %d [%#x]" % (_at, _at)
    return _data

def decode_second_header(data):
    print "decode_second_header() ..."
    _map = {}
    _bitpos = 0
    _bitpos, _loc = dwgutil.get_bit_long(data, _bitpos)
    print "location: %d" % _loc
    print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # A
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # C
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 1
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 1
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 2 or 4
    print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0
    print "bitpos: %d" % _bitpos
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    print "val1: " + str(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    print "val1: " + str(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    print "val1: " + str(_val)
    _bitpos, _val = dwgutil.test_bit(data, _bitpos)
    print "val1: " + str(_val)
    print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0x18 in spec
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0x78 in spec
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0x01 in spec
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # 0x04 for R13, 0x05 for R14, in spec
    print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # class 0
    _bitpos, _haddr = dwgutil.get_bit_long(data, _bitpos)
    print "header address: %d [%#x]" % (_haddr, _haddr)
    _bitpos, _hsize = dwgutil.get_bit_long(data, _bitpos)
    print "header size: %d" % _hsize
    print "bitpos: %d" % _bitpos    
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # class 1
    _bitpos, _caddr = dwgutil.get_bit_long(data, _bitpos)
    print "class address: %d [%#x]" % (_caddr, _caddr)
    _bitpos, _csize = dwgutil.get_bit_long(data, _bitpos)
    print "class size: %d" % _csize
    print "bitpos: %d" % _bitpos    
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # class 2
    _bitpos, _omaddr = dwgutil.get_bit_long(data, _bitpos)
    print "objmap address: %d [%#x]" % (_omaddr, _omaddr)
    _bitpos, _omsize = dwgutil.get_bit_long(data, _bitpos)
    print "objmap size: %d" % _omsize
    print "bitpos: %d" % _bitpos
    _bitpos, _char = dwgutil.get_raw_char(data, _bitpos)
    print "char: %#x" % _char # class 3
    _bitpos, _uaddr = dwgutil.get_bit_long(data, _bitpos)
    print "unknown address: %d [%#x]" % (_uaddr, _uaddr)
    _bitpos, _usize = dwgutil.get_bit_long(data, _bitpos)
    print "unknown size: %d" % _usize
    print "bitpos: %d" % _bitpos
    _bitpos, _nrh = dwgutil.get_bit_short(data, _bitpos)
    print "nrh: %d" % _nrh
    return _map # bail out ...
    #
    # things are messed up here - spec says get a short
    # and use it for handle records but that is not
    # what is done with 'dwg.tgz' code obj14.c ...
    #
    if True: # blah!
        print "bitpos: %d" % _bitpos
        _bitpos, _char = dwgutil.get_raw_char(data, _bitpos) # this isn't in the spec
        print "char: %#x" % _char # class 4
        _bitpos, _uaddr = dwgutil.get_bit_long(data, _bitpos) # nor this ...
        print "unknown address: %d [%#x]" % (_uaddr, _uaddr)
        _bitpos, _usize = dwgutil.get_bit_long(data, _bitpos) # nor this too
        print "unknown size: %d" % _usize
    print "bitpos: %d" % _bitpos    
    # _bitpos, _recnum = dwgutil.get_bit_short(data, _bitpos)
    # print "num of following handle records: %d" % _recnum
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
