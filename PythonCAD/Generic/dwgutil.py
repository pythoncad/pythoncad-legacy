#
# Copyright (c) 2003, 2006 Art Haas
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

import struct
import sys
import array

_debug = 0
dbg_handle = sys.stdout

#
# bitstream decoding class
#

class DWGBitStream(object):
    __mask_table = [
        (0xff, 0, 0x00, 0), # bit offset == 0
        (0x7f, 1, 0x80, 7), # bit offset == 1
        (0x3f, 2, 0xc0, 6), # bit offset == 2
        (0x1f, 3, 0xe0, 5), # bit offset == 3
        (0x0f, 4, 0xf0, 4), # bit offset == 4
        (0x07, 5, 0xf8, 3), # bit offset == 5
        (0x03, 6, 0xfc, 2), # bit offset == 6
        (0x01, 7, 0xfe, 1), # bit offset == 7
        ]
    
    def __init__(self, bits):
        if not isinstance(bits, array.array):
            raise TypeError, "Invalid bit array: " + `type(bits)`
        _tc = bits.typecode
        if _tc != 'B':
            raise ValueError, "Unexpected array typecode: %s" % _tc
        self.__bits = bits
        self.__offset = 0

    def getOffset(self):
        return self.__offset

    offset = property(getOffset, None, None, "Offset into bit array")

    def get_bytes(self, count):
        if ((count < 0) or (count & 0x07)):
            raise ValueError, "Invalid count: %d" % count
        _bits = self.__bits
        _idx = self.__offset >> 3
        _bidx = self.__offset & 0x07
        _m1, _lsh, _m2, _rsh = DWGBitStream.__mask_table[_bidx]
        _bytes = []
        _read = 0
        while _read < count:
            if _bidx == 0:
                _byte = _bits[_idx]
                _idx = _idx + 1
            else:
                _b1 = (_bits[_idx] & _m1)
                _idx = _idx + 1
                _b2 = (_bits[_idx] & _m2)
                _byte = (_b1 << _lsh) | (_b2 >> _rsh)
            _bytes.append(chr(_byte))
            self.__offset = self.__offset + 8
            _read = _read + 8
        return "".join(_bytes)

    def get_byte(self, count):
        if ((count < 0) or (count > 8)):
            raise ValueError, "Invalid count: %d" % count
        _bits = self.__bits
        _idx = self.__offset >> 3
        _bidx = self.__offset & 0x07
        _m = DWGBitStream.__mask_table[_bidx][0]
        _bav = 8 - _bidx # bits available at the current index
        _byte = _b1 = 0x0
        _rem = 0
        if count > _bav: # need bits at next index also
            _b1 = (_bits[_idx] & _m)
            _rem = count - _bav
        else:
            _byte = ((_bits[_idx] & _m) >> (8 - _bidx - count))
        if _rem > 0:
            _idx = _idx + 1
            _byte = (_b1 << _rem) | (_bits[_idx] >> (8 - _rem))
        self.__offset = self.__offset + count
        return _byte

    def test_bit(self):
        _bits = self.__bits
        _idx = self.__offset >> 3
        _bidx = self.__offset & 0x07
        _mask = 0x1 << (7 - _bidx)
        _val = (_bits[_idx] & _mask) != 0x0
        self.__offset = self.__offset + 1
        return _val

    def set_bit(self, flag):
        _bits = self.__bits
        _idx = self.__offset >> 3
        _bidx = self.__offset & 0x07
        if len(_bits) < _idx:
            _bits.append(0x0)
        _val = _bits[_idx]
        _mask = 0x01 << (7 - _bidx)
        if flag:
            _bits[_idx] = _val | _mask
        else:
            _bits[_idx] = _val & (0xff ^ _mask)
        self.__offset = self.__offset + 1
        
    def get_default_double(self, defval):
        _flags = self.get_byte(2)
        if (_flags == 0x0):
            _val = defval
        else:
            if (_flags == 0x3):
                _dstr = self.get_bytes(64)
                _val = struct.unpack('<d', _dstr)[0]
            else:
                _dstr = list(struct.pack('<d', defval))
                if (_flags == 0x1):
                    _dd = self.get_bytes(32)
                    _dstr[0] = _dd[0]
                    _dstr[1] = _dd[1]
                    _dstr[2] = _dd[2]
                    _dstr[3] = _dd[3]
                else: # flags == 0x2
                    _dd = self.get_bytes(48)
                    _dstr[4] = _dd[0]
                    _dstr[5] = _dd[1]
                    _dstr[0] = _dd[2]
                    _dstr[1] = _dd[3]
                    _dstr[2] = _dd[4]
                    _dstr[3] = _dd[5]
                _val = struct.unpack('<d', "".join(_dstr))[0]
        return _val

    def get_bit_double(self):
        _type = self.get_byte(2)
        _val = None
        if _type == 0x0:
            _db = self.get_bytes(64)
            _val = struct.unpack('<d', _db)[0]
        elif _type == 0x01:
            _val = 1.0
        elif _type == 0x02:
            _val = 0.0
        else:
            _offset = self.__offset
            raise ValueError, "Bad value at bit offset %d: 0x3" % _offset
        return _val

    def get_raw_double(self):
        _db = self.get_bytes(64)
        return struct.unpack('<d', _db)[0]

    def get_bit_short(self):
        _type = self.get_byte(2)
        _val = None
        if _type == 0x0:
            _sh = self.get_bytes(16)
            _val = struct.unpack('<h', _sh)[0]
        elif _type == 0x01:
            _val = self.get_byte(8)
        elif _type == 0x02:
            _val = 0
        elif _type == 0x03:
            _val = 256
        return _val

    def get_raw_short(self):
        _sh = self.get_bytes(16)
        return struct.unpack('<h', _sh)[0]

    def get_bit_long(self):
        _type = self.get_byte(2)
        _val = None
        if _type == 0x0:
            _long = self.get_bytes(32)
            _val = struct.unpack('<l', _long)[0]
        elif _type == 0x01:
            _val = self.get_byte(8)
        elif _type == 0x02:
            _val = 0
        else:
            _offset = self.__offset
            raise ValueError, "Bad value at bit offset %d: 0x03" % _offset
        return _val

    def get_raw_long(self):
        _long = self.get_bytes(32)
        return struct.unpack('<l', _long)[0]

    def get_raw_char(self):
        return self.get_byte(8)

    def get_modular_char(self):
        _bytes = []
        _read = True
        _fac = 1
        while _read:
            _byte = self.get_byte(8)
            if not (_byte & 0x80): # final byte has 0 in high bit
                _read = False
                if (_byte & 0x40): # negation
                    _fac = -1
                    _byte = _byte & 0xbf # turn off negative bit
            _bytes.append(_byte & 0x7f) # turn off high bit
        _blen = len(_bytes)
        if _blen == 1:
            _val = _bytes[0]
        elif _blen == 2:
            _val = _bytes[0] | (_bytes[1] << 7)
        elif _blen == 3: # possible?
            _val = _bytes[0] | (_bytes[1] << 7) | (_bytes[2] << 14)
        elif _blen == 4:
            _val = _bytes[0] | (_bytes[1] << 7) | (_bytes[2] << 14) | (_bytes[3] << 21)
        else:
            raise ValueError, "Unexpected byte array length: %d" % _blen
        return (_fac * _val)

    def get_text_string(self):
        _len = self.get_bit_short()
        return self.get_bytes((_len * 8))

    def get_handle(self):
        _code = self.get_byte(4)
        _counter = self.get_byte(4)
        _hlist = []
        if _counter:
            _hlen = _counter * 8
            _handle = self.get_bytes(_hlen)
            if _hlen > 8: # convert string into list of bytes
                for _chr in _handle:
                    _hlist.append(ord(_chr))
            else:
                _hlist.append(_handle)
        return (_code, _counter) + tuple(_hlist)

    def get_modular_short(self, handle):
        _shorts = []
        _short = struct.unpack('>h', handle.read(2))[0] # msb first
        while (_short & 0x80): # test high bit in lsb byte
            _shorts.append(_short)
            _short = struct.unpack('>h', handle.read(2))[0] # msb first
            _shorts.append(_short)
        for _i in range(len(_shorts)): # reverse bytes in shorts
            _short = _shorts[_i]
            _shorts[_i] = ((_short & 0xff00) >> 8) | ((_short & 0xff) << 8)
        _slen = len(_shorts)
        if _slen == 1:
            _size = _shorts[0] & 0x7fff
        elif _slen == 2:
            _tmp = _shorts[0]
            _shorts[0] = _shorts[1]
            _shorts[1] = _tmp
            _size = ((_shorts[0] & 0x7fff) << 15) | (_shorts[1] & 0x7fff)
        else:
            raise ValueError, "Unexpected array length: %d" % _slen
        return _size

    def read_extended_data(self):
        _extdata = []
        while True:
            _size = self.get_bit_short()
            if _size == 0:
                break
            _handle = self.get_handle()
            _eedata = []
            while (_size > 0):
                _cb = self.get_raw_char()
                _size = _size - 1
                if _cb == 0x0: # string
                    _len = self.get_raw_char()
                    _cp = self.get_raw_short()
                    _i = 0
                    _chars = []
                    while _i < _len:
                        _chars.append(chr(self.get_raw_char()))
                        _i = _i + 1
                    _eedata.append("".join(_chars))
                    _size = _size - _len - 3
                elif _cb == 0x1:
                    raise ValueError, "Invalid EEX code byte: 0x1"
                elif _cb == 0x2: # either '{' or '}'
                    _char = self.get_raw_char()
                    if _char == 0x0:
                        _eedata.append("{")
                    elif _char == 0x1:
                        _eedata.append("}")
                    else:
                        raise ValueError, "Unexpected EEX char: %#02x" % _char
                    _size = _size - 1
                elif (_cb == 0x3 or # layer table reference
                      _cb == 0x5): # entity handle reference
                    _chars = []
                    _i = 0
                    while _i < 8:
                        _chars.append(self.get_raw_char())
                        _i = _i + 1
                    _eedata.append(tuple(_chars)) # this seems odd ...
                    _size = _size - 8
                elif _cb == 0x4: # binary data
                    _len = self.get_raw_char()
                    _i = 0
                    _chars = []
                    while _i < _len:
                        _chars.append(self.get_raw_char())
                        _i = _i + 1
                    _eedata.append(_chars)
                    _size = _size - _len - 1
                elif (0xa <= _cb <= 0xd): # three doubles
                    _d1 = self.get_raw_double()
                    _d2 = self.get_raw_double()
                    _d3 = self.get_raw_double()
                    _eedata.append((_d1, _d2, _d3))
                    _size = _size - 24
                elif (0x28 <= _cb <= 0x2a): # one double
                    _d = self.get_raw_double()
                    _eedata.append(_d)
                    _size = _size - 8
                elif _cb == 0x46: # short int
                    _short = self.get_raw_short()
                    _eedata.append(_short)
                    _size = _size - 2
                elif _cb == 0x47: # long int
                    _long = self.get_raw_long()
                    _eedata.append(_long)
                    _size = _size - 4
                else:
                    raise ValueError, "Unexpected code byte: %#02x" % _cb
            _extdata.append((_handle, _eedata))
        return _extdata
    
#
# bitstream reading functions for DWG files
#
# these functions are used in R13/R14/R15 file decoding
#
# data: an array.array instance of unsigned bytes ("B")
# offset: the current bit offset where the value begins
#

def read_extended_data(data, offset):
    _bitpos = offset
    _extdata = []
    while True:
        _bitpos, _size = get_bit_short(data, _bitpos)
        if _size == 0:
            break
        _bitpos, _handle = get_handle(data, _bitpos)
        _eedata = []
        while (_size > 0):
            _bitpos, _cb = get_raw_char(data, _bitpos)
            _size = _size - 1
            if _cb == 0x0: # string
                _bitpos, _len = get_raw_char(data, _bitpos)
                _bitpos, _cp = get_raw_short(data, _bitpos)
                _chars = []
                for _i in range(_len):
                    _bitpos, _char = get_raw_char(data, _bitpos)
                    _chars.append(chr(_char))
                _eedata.append("".join(_chars))
                _size = _size - _len - 3
            elif _cb == 0x1:
                raise ValueError, "invalid EEX code byte: 0x1"
            elif _cb == 0x2: # either '{' or '}'
                _bitpos, _char = get_raw_char(data, _bitpos)
                if _char == 0x0:
                    _eedata.append("{")
                elif _char == 0x1:
                    _eedata.append("}")
                else:
                    raise ValueError, "Unexpected EEX char: %#02x" % _char
                _size = _size - 1
            elif (_cb == 0x3 or # layer table reference
                  _cb == 0x5): # entity handle reference
                _chars = []
                for _i in range(8):
                    _bitpos, _char = get_raw_char(data, _bitpos)
                    _chars.append(_char)
                _eedata.append(tuple(_chars)) # this seems odd ...
                _size = _size - 8
            elif _cb == 0x4: # binary data
                _bitpos, _len = get_raw_char(data, _bitpos)
                _chars = []
                for _i in range(_len):
                    _bitpos, _char = get_raw_char(data, _bitpos)
                    _chars.append(_char)
                _eedata.append(_chars)
                _size = _size - _len - 1
            elif (0xa <= _cb <= 0xd): # three doubles
                _bitpos, _d1 = get_raw_double(data, _bitpos)
                _bitpos, _d2 = get_raw_double(data, _bitpos)
                _bitpos, _d3 = get_raw_double(data, _bitpos)
                _eedata.append((_d1, _d2, _d3))
                _size = _size - 24
            elif (0x28 <= _cb <= 0x2a): # one double
                _bitpos, _d = get_raw_double(data, _bitpos)
                _eedata.append(_d)
                _size = _size - 8
            elif _cb == 0x46: # short int
                _bitpos, _short = get_raw_short(data, _bitpos)
                _eedata.append(_short)
                _size = _size - 2
            elif _cb == 0x47: # long int
                _bitpos, _long = get_raw_long(data, _bitpos)
                _eedata.append(_long)
                _size = _size - 4
            else:
                raise ValueError, "Unexpected code byte: %#02x" % _cb
        _extdata.append((_handle, _eedata))
    return _bitpos, _extdata

def get_default_double(data, offset, defval):
    _flags = get_bits(data, 2, offset)
    _read = 2
    if (_flags == 0x0):
        _val = defval
    else:
        _offset = offset + 2
        if (_flags == 0x3):
            _dstr = get_bits(data, 64, _offset)
            _val = struct.unpack('<d', _dstr)[0]
            _read = 66
        else:
            _dstr = list(struct.pack('<d', defval))
            if (_flags == 0x1):
                _dd = get_bits(data, 32, _offset)
                _dstr[0] = _dd[0]
                _dstr[1] = _dd[1]
                _dstr[2] = _dd[2]
                _dstr[3] = _dd[3]
                _read = 34
            else: # flags == 0x2
                _dd = get_bits(data, 48, _offset)
                _dstr[4] = _dd[0]
                _dstr[5] = _dd[1]
                _dstr[0] = _dd[2]
                _dstr[1] = _dd[3]
                _dstr[2] = _dd[4]
                _dstr[3] = _dd[5]
                _read = 50
            _val = struct.unpack('<d', "".join(_dstr))[0]
    return (offset + _read), _val

def get_bit_double(data, offset):
    _type = get_bits(data, 2, offset)
    _read = 2
    _val = None
    if _type == 0x00:
        _db = get_bits(data, 64, (offset + 2))
        _val = struct.unpack('<d', _db)[0]
        _read = 66
    elif _type == 0x01:
        _val = 1.0
    elif _type == 0x02:
        _val = 0.0
    else:
        raise ValueError, "bad type at bit offset %d: 0x3" % offset
    return (offset + _read), _val

def get_raw_double(data, offset):
    _db = get_bits(data, 64, offset)
    _val = struct.unpack('<d', _db)[0]
    return (offset + 64), _val

def get_bit_short(data, offset):
    _type = get_bits(data, 2, offset)
    _read = 2
    _val = None
    if _type == 0x00:
        _sh = get_bits(data, 16, (offset + 2))
        _val = struct.unpack('<h', _sh)[0]
        _read = 18
    elif _type == 0x01:
        _val = get_bits(data, 8, (offset + 2))
        _read = 10
    elif _type == 0x02:
        _val = 0
    elif _type == 0x03:
        _val = 256
    return (offset + _read), _val

def get_raw_short(data, offset):
    _sh = get_bits(data, 16, offset)
    _val = struct.unpack('<h', _sh)[0]
    return (offset + 16), _val

def get_bit_long(data, offset):
    _type = get_bits(data, 2, offset)
    _read = 2
    _val = None
    if _type == 0x0:
        _long = get_bits(data, 32, (offset + 2))
        _val = struct.unpack('<l', _long)[0]
        _read = 34
    elif _type == 0x01:
        _val = get_bits(data, 8, (offset + 2))
        _read = 10
    elif _type == 0x02:
        _val = 0
    else:
        raise ValueError, "Bad type at bit offset %d: 0x03" % offset
    return (offset + _read), _val

def get_raw_long(data, offset):
    _long = get_bits(data, 32, offset)
    _val = struct.unpack('<l', _long)[0]
    return (offset + 32), _val

def get_raw_char(data, offset):
    _char = get_bits(data, 8, offset)
    return (offset + 8), _char

def get_modular_char(data, offset):
    _bytes = []
    _read = True
    _offset = offset
    _fac = 1
    while _read:
        _byte = get_bits(data, 8, _offset)
        _offset = _offset + 8
        if not (_byte & 0x80): # final byte has 0 in high bit
            _read = False
            if (_byte & 0x40): # negation
                _fac = -1
                _byte = _byte & 0xbf # turn off negative bit
        _bytes.append(_byte & 0x7f) # turn off high bit
    if len(_bytes) == 1:
        _val = _bytes[0]
    elif len(_bytes) == 2:
        _val = _bytes[0] | (_bytes[1] << 7)
    elif len(_bytes) == 3: # possible?
        _val = _bytes[0] | (_bytes[1] << 7) | (_bytes[2] << 14)
    elif len(_bytes) == 4:
        _val = _bytes[0] | (_bytes[1] << 7) | (_bytes[2] << 14) | (_bytes[3] << 21)
    else:
        raise ValueError, "unexpected byte array length: %d" % len(_bytes)
    return _offset, (_fac * _val)

def get_text_string(data, offset):
    _bitpos, _len = get_bit_short(data, offset)
    _bitlen = _len * 8
    _string = get_bits(data, _bitlen, _bitpos)
    _bitpos = _bitpos + _bitlen
    return _bitpos, _string

def get_handle(data, offset):
    _code = get_bits(data, 4, offset)
    _counter = get_bits(data, 4, (offset + 4))
    _read = 8
    _hlist = []
    if _counter:
        _hlen = _counter * 8
        _handle = get_bits(data, _hlen, (offset + 8))
        _read = _read + _hlen
        if _hlen > 8: # convert string into list of bytes
            for _chr in _handle:
                _hlist.append(ord(_chr))
        else:
            _hlist.append(_handle)
    return (offset + _read), (_code, _counter) + tuple(_hlist)

def get_modular_short(handle):
    _shorts = []
    _short = struct.unpack('>h', handle.read(2))[0] # msb first
    while (_short & 0x80): # test high bit in lsb byte
        _shorts.append(_short)
        _short = struct.unpack('>h', handle.read(2))[0] # msb first
    _shorts.append(_short)
    for _i in range(len(_shorts)): # reverse bytes in shorts
        _short = _shorts[_i]
        _shorts[_i] = ((_short & 0xff00) >> 8) | ((_short & 0xff) << 8)
    _slen = len(_shorts)
    if _slen == 1:
        _size = _shorts[0] & 0x7fff
    elif _slen == 2:
        _tmp = _shorts[0]
        _shorts[0] = _shorts[1]
        _shorts[1] = _tmp
        _size = ((_shorts[0] & 0x7fff) << 15) | (_shorts[1] & 0x7fff)
    else:
        raise ValueError, "Unexpected array length: %d" % _slen
    return _size

#
# mask1: bit mask to apply to the current byte
# lshift: left shift amount of mask results
# mask2: bit mask to apply to the next byte
# rshift: right shift amount of the mask results
#
_mask_table = [
    (0xff, 0, 0x00, 0), # bit offset == 0
    (0x7f, 1, 0x80, 7), # bit offset == 1
    (0x3f, 2, 0xc0, 6), # bit offset == 2
    (0x1f, 3, 0xe0, 5), # bit offset == 3
    (0x0f, 4, 0xf0, 4), # bit offset == 4
    (0x07, 5, 0xf8, 3), # bit offset == 5
    (0x03, 6, 0xfc, 2), # bit offset == 6
    (0x01, 7, 0xfe, 1), # bit offset == 7
    ]

def get_bits(data, count, offset):
    # dbg_print("debugging on")
    dbg_print("passed %d data length with %d count at %d offset" %
              (len(data), count, offset))
    _idx = offset / 8 # index to the byte offset
    _bitidx = offset % 8 # index to the bit offset within the byte
    _mask1, _lsh, _mask2, _rsh = _mask_table[_bitidx]
    _binc = 8 - _bitidx # bits available in current byte
    _read = 0
    _rem = count
    _byte = 0x0
    _bytes = []
    while _read < count:
        if _rem > _binc: # need more bits than this byte can provide
            dbg_print("_rem > _binc")
            _b1 = (data[_idx] & _mask1)
            _read = _read + _binc
            if not isinstance(_rem, int):
                dbg_print("rem type: " + str(type(_rem)))
                dbg_print("rem: " + str(_rem))
            if not isinstance(_binc, int):
                dbg_print("binc type: " + str(type(_binc)))
                dbg_print("binc: " + str(_binc))
            _rem = _rem - _binc
        else: # this byte can give all the bits needed
            dbg_print("_rem <= _binc")
            _byte = _b1 = ((data[_idx] & _mask1) >> (8 - _bitidx - _rem))
            _read = _read + _rem
            _rem = 0
        if _read < count: # need bits from next byte
            dbg_print("_read %d < %d count" % (_read, count))
            _idx = _idx + 1
            if _rem > _bitidx: # use all bitidx bits - make a complete byte
                dbg_print("_rem (%d) > (%d) _bitidx" % (_rem, _bitidx))
                dbg_print("index %d of %d" % (_idx, len(data)))
                _b2 = (data[_idx] & _mask2)
                _byte = (_b1 << _lsh) | (_b2 >> _rsh)
                _read = _read + _bitidx
                _rem = _rem - _bitidx
            else: # use some bitidx to complete bit count request
                dbg_print("_rem <= _bitidx")
                _mask = _mask_table[_rem][2] # mask for current byte
                _b2 = data[_idx] & _mask
                _byte = (_b1 << _rem) | (_b2 >> (8 - _rem))
                _read = _read + _rem
                _rem = 0
        if count > 8:
            _bytes.append(chr(_byte))
    if len(_bytes):
        return "".join(_bytes)
    return _byte

def test_bit(data, offset):
    _idx = offset / 8 # index to the byte offset
    _bitidx = offset % 8 # index to the bit offset within the byte
    _mask = 0x1 << (7 - _bitidx)
    _val = False
    if (data[_idx] & _mask):
        _val = True
    return (offset + 1), _val

#
# debug routines
#

def set_nodebug():
    import dwgutil
    dwgutil._debug = 0

def set_debug(filename=None):
    import dwgutil
    dwgutil._debug = 1
    if filename != None:
        dwgutil.dbg_handle = open(filename, 'w')
    else:
        dwgutil.dbg_handle = sys.stdout

def dbg_print(*s):
    if _debug:
        string = ""
        for arg in s:
            string += str(arg) + " "
        string += "\n"
        dbg_handle.write(string)
