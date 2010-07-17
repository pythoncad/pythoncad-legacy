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
# read autocad r12 file format
#

import struct
import array
import sys

r13 = False # ugh - global variable

def dump_info(handle):
    global r13
    handle.seek(0, 0)
    _version = handle.read(6)
    if _version != 'AC1009':
        if _version == 'AC1010':
            r13 = True
        else:
            print "unknown version"
            return
    handle.seek(6, 1) # skip rest of version
    (_b1, _w1, _w2, _w3, _b2) = struct.unpack("<BhhhB", handle.read(8))
    print "byte: %#02x" % _b2
    print "word: %d" % _w1
    print "word: %d" % _w2
    print "word: %d" % _w3
    print "byte: %#02x" % _b2
    _estart, _eend = struct.unpack("<ll", handle.read(8))
    print "entity offsets: %d to %d" % (_estart, _eend)
    _bsstart, _l1, _bsend, _l2 = struct.unpack("<llll", handle.read(16))
    print "blocksec offsets: %d to %d" % (_bsstart, _bsend)
    print "longs: %d, %d" % (_l1, _l2)
    _block_table = get_table(handle)
    print "block table: " + str(_block_table)
    _layer_table = get_table(handle)
    print "layer table: " + str(_layer_table)
    _style_table = get_table(handle)
    print "style table: " + str(_style_table)
    _ltype_table = get_table(handle)
    print "ltype table: " + str(_ltype_table)
    _view_table = get_table(handle)
    print "view table: " + str(_view_table)
    #
    read_header(handle)
    #
    # more tables ...
    _ucs_table = get_table(handle)
    print "ucs table: " + str(_ucs_table)
    handle.seek(0x500, 0)
    _vport_table = get_table(handle)
    print "vport table: " + str(_vport_table)
    handle.seek(8, 1)
    _appid_table = get_table(handle)
    print "appid table: " + str(_appid_table)
    handle.seek(6, 1)
    _dimstyle_table = get_table(handle)
    print "dimstyle table: " + str(_dimstyle_table)
    handle.seek(0x69f, 0)    
    _p13_table = get_table(handle)
    print "p13 table: " + str(_p13_table)
    handle.seek(38, 1)
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)
    if _at != _estart:
        print "expected to be at entity start: %#x" % _estart
        return
    read_entities(handle, _estart, _eend)
    handle.seek(19, 1)
    read_block_table(handle, _block_table)
    read_layer_table(handle, _layer_table)
    read_style_table(handle, _style_table)
    read_ltype_table(handle, _ltype_table)
    read_view_table(handle, _view_table)
    read_ucs_table(handle, _view_table)
    read_vport_table(handle, _vport_table)
    read_appid_table(handle, _appid_table)
    read_dimstyle_table(handle, _dimstyle_table)
    read_p13_table(handle, _p13_table)
    read_entities(handle, _bsstart, _bsend)
    handle.seek(36, 1)
    _pestart, _peend, _pbstart,_pbend = struct.unpack('<4l', handle.read(16))
    print "pestart: %d; peend: %d" % (_pestart, _peend)
    print "bstart: %d; bend: %d" % (_pbstart, _pbend)    
    if (_pestart != _estart):
        print "pestart != estart: %d != %d" % (_pestart, _estart)
    if (_peend != _eend):
        print "peend != eend: %d != %d" % (_peend, _eend)
    if (_bsstart != _pbstart):
        print "pstart != bstart: %d != %d" % (_pbstart, _bsstart)
    if (_bsend != _pbend):
        print "pbend != bend: %d != %d" % (_pbend, _bsend)
    print "handle at: %#x" % handle.tell()        
    handle.seek(12, 1)
    print "handle at: %#x" % handle.tell()
    _bts = get_table_test(handle)
    print "test table: " + str(_bts)
    # handle.seek(6, 1)
    _lyrts = get_table_test(handle)
    print "test table: " + str(_lyrts)    
    # handle.seek(6, 1)
    _sts = get_table_test(handle)
    print "test table: " + str(_sts)    
    # handle.seek(6, 1)
    _ltts = get_table_test(handle)
    print "test table: " + str(_ltts)
    # handle.seek(6, 1)
    _vts = get_table_test(handle)
    print "test table: " + str(_vts)
    # handle.seek(6, 1)
    _uts = get_table_test(handle)
    print "test table: " + str(_uts)
    # handle.seek(6, 1)
    _vpts = get_table_test(handle)
    print "test table: " + str(_vts)
    # handle.seek(6, 1)
    _ats = get_table_test(handle)
    print "test table: " + str(_ats)
    # handle.seek(6, 1)
    _dts = get_table_test(handle)
    print "test table: " + str(_dts)
    # handle.seek(6, 1)
    _pts = get_table_test(handle)
    print "test table: " + str(_pts)
    # handle.seek(6, 1)
    
#
# entity reading routines
#

def line_reader(handle, flags, opts):
    print "line_reader() ..."
    _zflag = True
    if (flags & 0x4):
        _zflag = False
    _pt10 = get_point(handle, _zflag)
    _pt11 = get_point(handle, _zflag)
    print "p1: " + str(_pt10)
    print "p2: " + str(_pt11)
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)

def point_reader(handle, flags, opts):
    print "point_reader() ..."
    _zflag = True
    if (flags & 0x4):
        _zflag = False
    _pt10 = get_point(handle, _zflag)
    print "point: " + str(_pt10)
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)

def circle_reader(handle, flags, opts):
    print "circle_reader() ..."
    _zflag = False
    if (flags & 0x4):
        _zflag = True
    _pt10 = get_point(handle, _zflag)
    print "center: " + str(_pt10)
    _d40 = struct.unpack("<d", handle.read(8))[0]
    print "radius: %g" % _d40
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)

def shape_reader(handle, flags, opts):
    print "shape_reader() ..."
    _pt10 = get_point(handle, False)
    print "pt: " + str(_pt10)
    _w2 = struct.unpack('<h', handle.read(2))[0]
    print "word: %d" % _w2
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38
        
def text_reader(handle, flags, opts):
    print "text_reader() ..."
    _pt10 = get_point(handle, False)
    print "point: " + str(_pt10)
    _db40 = struct.unpack('<d', handle.read(8))[0]
    print "double: %g" % _db40 # angle of text
    _text = get_string(handle)
    print "text: %s" % _text
    if (opts & 0x1):
        _db50 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db50
    if (opts & 0x2):
        _db41 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db41
    if (opts & 0x4):
        _db51 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db51
    if (opts & 0x8):
        _b7 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b7
    if (opts & 0x10):
        _b71 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b71
    if (opts & 0x20):
        _b72 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b72
    if (opts & 0x40):
        _pt11 = get_point(handle, False)
        print "pt11: " + str(_pt11)
    if (opts & 0x100):
        _b73 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b73
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)

def arc_reader(handle, flags, opts):
    print "arc_reader() ..."
    _pt10 = get_point(handle, False)
    print "center: " + str(_pt10)
    _d40 = struct.unpack('<d', handle.read(8))[0]
    print "radius: %g" % _d40
    _d50 = struct.unpack('<d', handle.read(8))[0]
    print "start angle: %g" % _d50
    _d51 = struct.unpack('<d', handle.read(8))[0]
    print "end angle: %g" % _d51
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38

def trace_reader(handle, flags, opts):
    print "trace_reader() ..."
    _pt10 = get_point(handle, False)
    print "pt: " + str(_pt10)
    _pt11 = get_point(handle, False)
    print "pt: " + str(_pt11)
    _pt12 = get_point(handle, False)
    print "pt: " + str(_pt12)
    _pt13 = get_point(handle, False)
    print "pt: " + str(_pt13)
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38

def solid_reader(handle, flags, opts):
    print "solid_reader() ..."
    _pt11 = get_point(handle, False)
    print "pt: " + str(_pt11)
    _pt12 = get_point(handle, False)
    print "pt: " + str(_pt12)
    _pt13 = get_point(handle, False)
    print "pt: " + str(_pt13)
    _pt14 = get_point(handle, False)
    print "pt: " + str(_pt14)
    if (opts & 0x1):
        _pt210 = get_point(handle, True)
        print "pt: " + str(_pt210)
    if (opts & 0x2):
        _db38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db38

def block_reader(handle, flags, opts):
    print "block_reader() ..."
    _pt10 = get_point(handle, False)
    print "pt: " + str(_pt10)
    _s1 = get_string(handle)
    print "name: %s" % _s1
    if (opts & 0x2):
        _s3 = get_string(handle)
        print "string: %s" % _s3

def endblk_reader(handle, flags, opts):
    print "endblk_reader() ..."

def insert_reader(handle, flags, opts):
    print "insert_reader() ..."
    _w1 = struct.unpack('<h', handle.read(2))[0]
    print "word: %d" % _w1
    _p10 = get_point(handle, False)
    print "point: " + str(_p10)
    if (opts & 0x1):
        _db41 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db41
    if (opts & 0x2):
        _db42 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db42
    if (opts & 0x4):
        _db43 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db43
    if (opts & 0x8):
        _db50 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db50
    if (opts & 0x10):
        _w70 = struct.unpack('<h', handle.read(2))[0]
        print "word: %d" % _w70
    if (opts & 0x10):
        _w71 = struct.unpack('<h', handle.read(2))[0]
        print "word: %d" % _w71
    if (opts & 0x40):
        _db44 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db44
    if (opts & 0x80):
        _db45 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _db45
        
def attdef_reader(handle, flags, opts):
    print "attdef_reader() ..."
    _p10 = get_point(handle, False)
    print "pt: " + str(_p10)
    _s1 = get_string(handle)
    print "string: %s" % _s1
    _s3 = get_string(handle)
    print "string: %s" % _s3
    _s2 = get_string(handle)
    print "string: %s" % _s2
    _b70 = struct.unpack('B', handle.read(1))[0]
    print "byte: %#x" % _b70
    if (opts & 0x1):
        _b73 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b73
    if (opts & 0x2):
        _d50 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d50
    if (opts & 0x4):
        _d41 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d41
    if (opts & 0x8):
        _d42 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d42
    if (opts & 0x10):
        _b7 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b7
    if (opts & 0x20):
        _b71 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b71
    if (opts & 0x40):
        _b72 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b72
    if (opts & 0x80):
        _p11 = get_point(handle, False)
        print "pt: " + str(_p11)
    if (opts & 0x100):
        _p210 = get_point(handle, True)
        print "pt: " + str(_p210)
    if (opts & 0x200):
        _d38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d38

def attrib_reader(handle, flags, opts):
    print "attrib_reader() ..."
    _p10 = get_point(handle, False)
    print "pt: " + str(_p10)
    _d40 = struct.unpack('<d', handle.read(8))[0]
    print "double: %g" % _d40
    _s1 = get_string(handle)
    print "string: %s" % _s1
    _s2 = get_string(handle)
    print "string: %s" % _s2
    if (opts & 0x1):
        _b73 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b73
    if (opts & 0x2):
        _d50 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d50
    if (opts & 0x4):
        _d41 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d41
    if (opts & 0x8):
        _d42 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d42
    if (opts & 0x10):
        _b7 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b7
    if (opts & 0x20):
        _b71 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b71
    if (opts & 0x40):
        _b72 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b72
    if (opts & 0x80):
        _p11 = get_point(handle, False)
        print "pt: " + str(_p11)
    if (opts & 0x100):
        _p210 = get_point(handle, True)
        print "pt: " + str(_p210)
    if (opts & 0x200):
        _d38 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d38

def sbend_reader(handle, flags, opts):
    print "sbend_reader() ..."
    _l = struct.unpack('<l', handle.read(4))[0]
    print "long: %d" % _l
    
def pline_reader(handle, flags, opts):
    print "pline_reader() ..."
    if (opts & 0x1):
        _b70 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b70
    if (opts & 0x2):
        _d40 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d40
    if (opts & 0x4):
        _b71 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b71
    if (opts & 0x8):
        _b72 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b72
    if (opts & 0x10):
        _b73 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b73
    if (opts & 0x20):
        _b74 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b74
    if (opts & 0x40):
        _b75 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b75

def vertex_reader(handle, flags, opts):
    print "vertex_reader() ..."
    _pt10 = get_point(handle, False)
    print "pt: " + str(_pt10)
    if (opts & 0x1):
        _d40 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d40
    if (opts & 0x2):
        _d41 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d41
    if (opts & 0x4):
        _d50 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d50
    if (opts & 0x8):
        _b70 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b70
    
def face3d_reader(handle, flags, opts):
    print "face3d_reader() ..."
    _zflag = False
    if (flags & 0x4):
        _zflag = True
    _pt10 = get_point(handle, _zflag)
    print "pt: " + str(_pt10)
    _pt11 = get_point(handle, _zflag)
    print "pt: " + str(_pt11)
    _pt12 = get_point(handle, _zflag)
    print "pt: " + str(_pt12)
    _pt13 = get_point(handle, _zflag)
    print "pt: " + str(_pt13)

def dim_reader(handle, flags, opts):
    print "dim_reader() ..."
    _w1 = struct.unpack('<h', handle.read(2))[0]
    print "word: %d" % _w1
    _pt10 = get_point(handle, True)
    print "pt: " + str(_pt10)
    _pt11 = get_point(handle, False)
    print "pt: " + str(_pt11)
    if (opts & 0x2):
        _b70 = struct.unpack('B', handle.read(1))[0]
        print "byte: %#x" % _b70
    if (opts & 0x1):
        _pt12 = get_point(handle, True)
        print "pt: " + str(_pt12)
    if (opts & 0x4):
        _s1 = get_string(handle)
        print "text: %s" % _s1
    if (opts & 0x8):
        _pt13 = get_point(handle, True)
        print "pt: " + str(_pt13)
    if (opts & 0x10):
        _pt14 = get_point(handle, True)
        print "pt: " + str(_pt14)
    if (opts & 0x20):
        _pt15 = get_point(handle, True)
        print "pt: " + str(_pt15)
    if (opts & 0x40):
        _pt16 = get_point(handle, True)
        print "pt: " + str(_pt16)
    if (opts & 0x80):
        _d40 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d40
    if (opts & 0x100):
        _d50 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d50
    if (opts & 0x200):
        _d51 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d51
    if (opts & 0x400):
        _d52 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d52
    if (opts & 0x800):
        _d53 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d53

def vport_reader(handle, flags, opts):
    print "vport_reader() ..."
    _pt10 = get_point(handle, True)
    print "pt: " + str(_pt10)
    _d40 = struct.unpack('<d', handle.read(8))[0]
    print "double: %g" % _d40
    _d41 = struct.unpack('<d', handle.read(8))[0]
    print "double: %g" % _d41
    _w68 = struct.unpack('<h', handle.read(2))[0]
    print "word: %d" % _w68
    
entities = [
    None,
    line_reader,
    point_reader,
    circle_reader,
    shape_reader,
    None,
    None,
    text_reader,
    arc_reader,
    trace_reader,
    None,
    solid_reader,
    block_reader,
    endblk_reader,
    insert_reader,
    attdef_reader,
    attrib_reader,
    sbend_reader,
    None,
    pline_reader,
    vertex_reader,
    None,
    face3d_reader,
    dim_reader,
    vport_reader
    ]

def read_p13_table(handle, lt): # no info on this ...
    print "read_p13_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        handle.seek(_end)
    _crc32 = handle.read(32)
    
def read_dimstyle_table(handle, lt):
    print "read_dimstyle_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _word = struct.unpack('<h', handle.read(2))[0]
        print "word: %d" % _word
        _d4048 = struct.unpack('<9d', handle.read(72))
        print "d4048: " + str(_d4048)
        _d140145 = struct.unpack('<6d', handle.read(48))
        print "d140145: " + str(_d140145)
        _b7078 = struct.unpack('<7B', handle.read(7))
        print "b7078: " + str(_b7078)
        _b170175 = struct.unpack('<6B', handle.read(6))
        print "b170175: " + str(_b170175)
        _s3 = handle.read(16)
        print "string: %s" % _s3
        _s4 = handle.read(16)
        print "string: %s" % _s4
        _s5 = handle.read(32)
        print "string: %s" % _s5
        _s6 = handle.read(32)
        print "string: %s" % _s6
        _s7 = handle.read(32)
        print "string: %s" % _s7
        handle.seek(3, 1)
        _w176, _w177, _w178 = struct.unpack('<3h', handle.read(6))
        print "word: %d" % _w176
        print "word: %d" % _w177
        print "word: %d" % _w178
        _d146, _d147 = struct.unpack('<dd', handle.read(16))
        print "double: %d" % _d146
        print "double: %d" % _d147
        _offset = _end - handle.tell() - 2
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
    _crc32 = handle.read(32)

def read_appid_table(handle, lt):
    print "read_appid_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _word = struct.unpack('<h', handle.read(2))[0]
        print "word: %d" % _word
        _offset = _end - handle.tell() - 2
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
    _crc32 = handle.read(32)

def read_vport_table(handle, lt):
    print "read_vport_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _used = struct.unpack('<h', handle.read(2))[0]
        _pt10 = get_point(handle, False)
        print "pt: " + str(_pt10)
        _pt11 = get_point(handle, False)
        print "pt: " + str(_pt11)
        _pt17 = get_point(handle, True)
        print "pt: " + str(_pt17)
        _pt16 = get_point(handle, True)
        print "pt: " + str(_pt16)
        _d50, _d40 = struct.unpack('<dd', handle.read(16))
        print "double: %g" % _d50
        print "double: %g" % _d40
        _pt12 = get_point(handle, False)
        print "pt: " + str(_pt12)
        _d41, _d42, _d43, _d44 = struct.unpack('<4d', handle.read(32))
        print "double: %g" % _d41
        print "double: %g" % _d42
        print "double: %g" % _d43
        print "double: %g" % _d44
        _w7178 = struct.unpack('<8h', handle.read(16))
        print "words: " + str(_w7178)
        _d51 = struct.unpack('<d', handle.read(8))[0]
        print "double: %g" % _d51
        _pt13 = get_point(handle, False)
        print "pt: " + str(_pt13)
        _pt14 = get_point(handle, False)
        print "pt: " + str(_pt14)
        _pt15 = get_point(handle, False)
        print "pt: " + str(_pt15)
        _offset = _end - handle.tell() - 2
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
    _crc32 = handle.read(32)
    
def read_ucs_table(handle, lt):
    print "read_ucs_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _used = struct.unpack('<h', handle.read(2))[0]
        print "used: %d" % _used
        _pt10 = get_point(handle, True)
        print "pt: " + str(_pt10)
        _pt11 = get_point(handle, True)
        print "pt: " + str(_pt11)
        _pt12 = get_point(handle, True)
        print "pt: " + str(_pt12)
        _offset = _end - handle.tell() - 2
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
    _crc32 = handle.read(32)
    
def read_view_table(handle, lt):
    print "read_view_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _used, _db40 = struct.unpack('<hd', handle.read(10))
        print "used: %d" % _used
        print "double: %d" % _db40
        _pt10 = get_point(handle, False)
        print "pt: " + str(_pt10)
        _db41 = struct.unpack('<d', handle.read(8))[0]
        print "double: %d" % _db41
        _pt11 = get_point(handle, True)
        print "pt: " + str(_pt11)
        _pt12 = get_point(handle, True)
        print "pt: " + str(_pt12)
        _w71, _db42, _db43, _db44, _db50 = struct.unpack('<hdddd', handle.read(34))
        print "word: %d" % _w71
        print "double: %g" % _db42
        print "double: %g" % _db43
        print "double: %g" % _db44
        print "double: %g" % _db50
        #
        # things probably are messed up here
        #
        _offset = _end - handle.tell()
        print "offset: %d" % _offset - 2
        if _offset:
            handle.seek(_offset, 1)
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
    _crc32 = handle.read(32)

def read_ltype_table(handle, lt):
    print "read_ltype_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _w1 = struct.unpack('<h', handle.read(2))[0]
        print "word: %d" % _w1
        _s1 = handle.read(48)
        print "string: %s" % _s1
        _b1, _b2 = struct.unpack('BB', handle.read(2))
        print "b1: %#x; b2: %#x" % (_b1, _b2)
        _doubles = struct.unpack('<13d', handle.read(104))
        print "doubles: " + str(_doubles)
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
        _offset = _end - handle.tell()
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
    _crc32 = handle.read(32)
    
def read_style_table(handle, lt):
    print "read_style_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _w1, _d1, _d2, _d3, _b1, _d4 = struct.unpack('<hdddBd', handle.read(35))
        print "word: %d" % _w1
        print "doubles: (%g,%g,%g)" % (_d1, _d2, _d3)
        print "byte: %#x" %_b1
        print "double: %g" % _d4
        _s1 = handle.read(128)
        print "string: %s" % _s1
        _crc = struct.unpack('<h', handle.read(2))[0]
        print "crc: %#x" % _crc
        _offset = _end - handle.tell()
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
    _crc32 = handle.read(32)
    
def read_layer_table(handle, lt):
    print "read_layer_table() ..."
    _size, _nr, _start = lt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _used, _color, _style, _crc = struct.unpack('<hhhh', handle.read(8))
        print "used: %d" % _used
        print "color: %d" % _color
        print "style: %d" % _style
        print "crc: %#x" % _crc        
        _offset = _end - handle.tell()
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
    _crc32 = handle.read(32)
    
def read_block_table(handle, bt):
    print "read_block_table() ..."
    _size, _nr, _start = bt
    print "size: %d, nr: %d, start: %d" % (_size, _nr, _start)
    handle.seek(_start, 0)
    for _i in range(_nr):
        print "reading from %#x" % handle.tell()
        _end = handle.tell() + _size        
        print "record: %d" % _i
        _flag = struct.unpack('B', handle.read(1))[0]
        print "flag: %#x" % _flag
        _name = handle.read(32)
        print "name: %s" % _name
        _used, _b1, _w1, _b2, _w2, _crc = struct.unpack('<hBhBhh', handle.read(10))
        print "used: %d" % _used
        print "b1: %#x" % _b1
        print "w1: %d" % _w1
        print "b2: %#x" % _b2
        print "w2: %d" % _w2
        print "crc: %#x" % _crc
        _offset = _end - handle.tell()
        print "offset: %d" % _offset
        if _offset:
            handle.seek(_offset, 1)
    _crc32 = handle.read(32)

def read_xdata(handle):
    _data = []
    _xlen = struct.unpack('<h', handle.read(2))[0]
    while (_xlen > 0):
        _xval = struct.unpack('B', handle.read(1))[0]
        _xlen = _xlen - 1
        if _xval == 0:
            if _xlen < 1: break
            _val = struct.unpack('B', handle.read(1))[0]
            _xlen = _xlen - 1
            if r13: # ugh
                if _xlen < 1: break
                _cp = struct.unpack('B', handle.read(1))[0] # code page?
                _xlen = _xlen - 1
            if _xlen < _val: break
            _string = handle.read(_val)
            _data.append(_string)
            _xlen = _xlen - _val
        elif (_xval == 1 or
              _xval == 3 or
              _xval == 70):
            if _xlen < 2: break
            _val = struct.unpack('<h', handle.read(2))[0]
            _data.append(_val)
            _xlen = _xlen - 2
        elif _xval == 2:
            if _xlen < 1: break
            _val = struct.unpack('B', handle.read(1))[0]
            if _val == 0:
                _data.append('{')
            elif _val == 1:
                _data.append('}')
            else:
                raise ValueError, "Unexpected char: %#02x" % _val
            _xlen = _xlen - 1
        elif _val == 5:
            if _xlen < 8: break
            _val = handle.read(8) # probably an entity handle
            _xlen = _xlen - 8
        elif (_xval == 40 or
              _xval == 41 or
              _xval == 42):
            if _xlen < 8: break
            _val = struct.unpack('<d', handle.read(8))[0]
            _data.append(_val)
            _xlen = _xlen - 8
        elif (_xval == 10 or
              _xval == 11 or
              _xval == 12 or
              _xval == 13): # 13 not in R12 spec sheet; is in R13/R14 spec
            if _xlen < 24: break
            _point = get_point(handle, True)
            _data.append(_point)
            _xlen = _xlen - 24
        elif _xval == 71:
            if _xlen < 4: break
            _val = struct.unpack('<l', handle.read(4))[0]
            _data.append(_val)
            _xlen = _xlen - 4
        else:
            _xlen = 0
    return _data
    
def read_entities(handle, start, end):
    print "read_entities() ..."
    handle.seek(start, 0)
    _at = handle.tell()
    _emax = len(entities)
    while (_at < (end - 32)):
        print "handle offset: %d [%#x]" % (_at, _at)
        print "max offset: %d [%#x]" % ((end - 32), (end - 32))
        _kind, _flag, _length = struct.unpack("<BBh", handle.read(4))
        print "kind: %#x" % _kind
        print "flag: %#x" % _flag
        print "length: %d" % _length
        _crcpos = _at + (_length - 2)
        print "crcpos: %d [%#x]" % (_crcpos, _crcpos)
        _layer, _opts = struct.unpack('<hh', handle.read(4))
        print "layer: %d" % _layer
        print "opts: %d" % _opts
        _color = 0
        if (_flag & 0x1):
            _color = struct.unpack('B', handle.read(1))[0]
        print "color: %#x" % _color
        _extra = 0
        if (_flag & 0x40):
            _extra = struct.unpack('B', handle.read(1))[0]
        print "extra: %#x" % _extra
        _xdata = None
        if (_extra & 0x2):
            _xdata = read_xdata(handle)
        _type = None
        if (_flag & 0x2):
            _type = struct.unpack('<h', handle.read(2))[0]
            print "type: %#x" % _type
        _z = None
        if ((_flag & 0x4) and (_kind > 2) and (_kind != 22)):
            _z = struct.unpack('<d', handle.read(8))[0]
            print "z: %g" % _z
        _th = None
        if (_flag & 0x8):
            _th = struct.unpack('<d', handle.read(8))[0]
            print "th: %g" % _th
        _handle = None
        if (_flag & 0x20):
            _handle = get_handle(handle)
            print "handle: " + str(_handle)
        _paper = None
        if (_extra & 0x4):
            _paper = struct.unpack('<h', handle.read(2))[0]
            print "paper: %d" % _paper
        if _kind < _emax:
            _reader = entities[_kind]
            if _reader is not None:
                _reader(handle, _flag, _opts)
                _at = handle.tell()
                if (_at < _crcpos):
                    print "at < crcpos"
                    handle.seek((_crcpos - _at), 1)
                elif (_at > _crcpos):
                    print "at > crcpos"
                else:
                    print "at == crcpos"
                _crc = struct.unpack('<h', handle.read(2))[0]
                print "crc: %d [%#x]" % (_crc, _crc)
        _at = handle.tell()
    _crc32 = handle.read(32)
    print "entity reading completes at %#x" % handle.tell()
        
def read_header(handle):
    print "read_header() ..."
    _w1 = struct.unpack("<h", handle.read(2))[0]    
    print "word: %d" % _w1
    _inbase = get_point(handle, True)
    print "inbase: " + str(_inbase)
    _extmin = get_point(handle, True)
    print "extmin: " + str(_extmin)
    _extmax = get_point(handle, True)
    print "extmax: " + str(_extmax)
    _limmin = get_point(handle, False)
    print "limmin: " + str(_limmin)
    _limmax = get_point(handle, False)
    print "limmax: " + str(_limmax)
    _vcx, _vcy, _d3, _d4 = struct.unpack("<dddd", handle.read(32))
    print "view center: (%g, %g)" % (_vcx, _vcy)
    print "doubles: %g, %g" % (_d3, _d4)
    _b1, _b2 = struct.unpack("<BB", handle.read(2))
    print "bytes: %#02x, %#02x" % (_b1, _b2)
    _sx, _sy = struct.unpack("<dd", handle.read(16))
    print "snap units: (%g,%g)" % (_sx, _sy)
    _b56 = array.array('B')
    _b56.fromfile(handle, 56)
    print "56 bytes: " + str(_b56)
    _d7, _d8, _d9 = struct.unpack("<ddd", handle.read(24))
    print "doubles: %g, %g, %g" % (_d7, _d8, _d9)
    _b18 = array.array('B')
    _b18.fromfile(handle, 18)
    print "18 bytes: " + str(_b18)
    _d10 = struct.unpack("<d", handle.read(8))
    print "double: %g" % _d10
    #
    # the following comes from the C code
    #
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)
    _w2, _w3 = struct.unpack("<hh", handle.read(4))
    print "word: %d, %d" % (_w2, _w3)
    _b44 = array.array('B')
    _b44.fromfile(handle, 44)
    print "44 bytes: " + str(_b44)
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)
    _b354 = array.array('B')
    _b354.fromfile(handle, 354)
    print "354 more bytes read ..."
    if _b354[0:4] == [0x61,0x63,0x61,0x64]: # acad
        print "found 'acad' at start of 354 byte block"
    _at = handle.tell()
    print "handle offset: %d [%#x]" % (_at, _at)
    #
    # skip to 0x3ef - remainder of header is mysterious ...
    #
    handle.seek(0x3ef, 0)

def get_point(handle, flag):
    if flag:
        _pt = struct.unpack('<ddd', handle.read(24))
    else:
        _pt = struct.unpack('<dd', handle.read(16))
    return _pt

def get_table(handle):
    return struct.unpack("<hll", handle.read(10))    

def get_table_test(handle):
    return struct.unpack('<hhhl', handle.read(10))

def get_handle(handle):
    _bytes = []
    _len = struct.unpack('B', handle.read(1))[0]
    for _i in range(_len):
        _byte = struct.unpack('B', handle.read(1))[0]
        _bytes.append(_byte)
    return (5, _len) + tuple(_bytes)

def get_string(handle):
    _len = struct.unpack('<h', handle.read(2))[0]
    return handle.read(_len)
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: dwg12.py filename"
        sys.exit(1)
    try:
        _fh = file(sys.argv[1])
    except:
        print "failed to open '%s'. Exiting ..." % sys.argv[1]
        sys.exit(1)
    dump_info(_fh)
    _fh.close()
