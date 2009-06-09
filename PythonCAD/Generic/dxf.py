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
# simple DXF file reader
#

import sys

def read_dxf(handle):
    handle.seek(0,0)
    while True:
        _code, _data = get_group(handle)
        if _code == 0 and _data == 'EOF':
            break
        if _code == 0 and _data == 'SECTION':
            _secdata = read_section(handle)

def read_section(handle):
    _sdata = None
    while True:
        _code, _data = get_group(handle)
        if _code == 0 and _data == 'EOF':
            break
        if _code != 2:
            raise ValueError, "Expected code 2; got %d" % _code
        _sdata = None        
        if _data == 'HEADER':
            _sdata = read_header(handle)
            print "HEADER data:"
        elif _data == 'CLASSES':
            _sdata = read_classes(handle)
            print "CLASSES data:"
        elif _data == 'TABLES':
            _sdata = read_tables(handle)
            print "TABLES data:"
        elif _data == 'BLOCKS':
            _sdata = read_blocks(handle)
            print "BLOCKS data:"
        elif _data == 'ENTITIES':
            _sdata = read_entities(handle)
            print "ENTITY data:"
        elif _data == 'OBJECTS':
            _sdata = read_objects(handle)
            print "OBJECTS data:"
        else:
            while True:
                _code, _data = get_group(handle)
                if _code == 0 and (_data == 'ENDSEC' or _data == 'EOF'):
                    break
        if _sdata is not None:
            _keys = _sdata.keys()
            _keys.sort()
            for _key in _keys:
                print "%s -> %s" % (_key, str(_sdata[_key]))
        break
    return _sdata

def read_header(handle):
    _hmap = {}
    _code, _data = get_group(handle)
    while True:
        if _code == 0 and (_data == 'EOF' or _data == 'ENDSEC'):
            break
        if _code != 9:
            raise ValueError, "Expected code 9; got %d" % _code
        while True:
            _var = _data[1:]
            _dlist = []
            while True:
                _code, _data = get_group(handle)
                if _code == 0 or _code == 9:
                    break
                _dlist.append(_data)
            if len(_dlist) == 1:
                _hmap[_var] = _dlist[0]
            else:
                _hmap[_var] = tuple(_dlist)
            if _code == 0:
                break
    return _hmap

def read_classes(handle):
    _cmap = {}
    while True:
        _code, _r0 = get_group(handle)
        if _code != 0:
            raise ValueError, "Expected code 0, got %d" % _code
        if _r0 == 'EOF' or _r0 == 'ENDSEC':
            break
        _code, _r1 = get_group(handle)
        if _code != 1:
            raise ValueError, "Expected code 1, got %d" % _code
        _code, _r2 = get_group(handle)
        if _code != 2:
            raise ValueError, "Expected code 2, got %d" % _code
        _code, _r3 = get_group(handle)
        if _code != 3:
            raise ValueError, "Expected code 3, got %d" % _code
        _code, _r90 = get_group(handle)
        if _code != 90:
            raise ValueError, "Expected code 90, got %d" % _code
        _code, _r280 = get_group(handle)
        if _code != 280:
            raise ValueError, "Expected code 280, got %d" % _code
        _code, _r281 = get_group(handle)
        if _code != 281:
            raise ValueError, "Expected code 281, got %d" % _code
        _cmap[_r1] = (_r2, _r3, _r90, _r280, _r281)
    return _cmap

def read_tables(handle):
    _tmap = {}
    while True:
        _code, _r0 = get_group(handle)
        if _code == 0 and (_r0 == 'EOF' or _r0 == 'ENDSEC'):
            break
        if _code == 0 and _r0 == 'TABLE':
            _code, _name = get_group(handle)
            if _code != 2:
                raise ValueError, "Expected code 2 for table name: %d" % _code
            _tdata = []
            while True:
                _code, _val = get_group(handle)
                if _code == 0 and _val == 'ENDTAB':
                    break
                _tdata.append((_code, _val))
            _tmap[_name] = _tdata
    return _tmap

def read_blocks(handle):
    _bmap = {}
    _i = 0
    _code, _val = get_group(handle)
    while True:
        if _code != 0:
            raise ValueError, "Expected code 0; got %d" % _code
        if _val == 'EOF' or _val == 'ENDSEC':
            break
        if _val != 'BLOCK':
            raise ValueError, "Expected BLOCK, got " + str(_val)
        _bdata = []
        while True:
            _code, _val = get_group(handle)
            if _code == 0 and _val == 'ENDBLK':
                break
            _bdata.append((_code, _val))
        _ebdata = []
        while True:
            _code, _val = get_group(handle)
            if _code == 0 and (_val == 'BLOCK' or _val == 'ENDSEC'):
                break
            _ebdata.append((_code, _val))
        _bmap[_i] = _bdata + _ebdata
        _i = _i + 1
    return _bmap

def read_entities(handle):
    _emap = {}
    _i = 0
    _code, _val = get_group(handle)
    while True:
        if _code != 0:
            raise ValueError, "Expected code 0; got %d" % _code
        if _val == 'EOF' or _val == 'ENDSEC':
            break
        _edata = []
        _edata.append((_code, _val)) # entity type is _val
        while True:
            _code, _val = get_group(handle)
            if _code == 0: # either next entity or end of section
                break
            _edata.append((_code, _val))
        _emap[_i] = _edata
        _i = _i + 1
    return _emap

def read_objects(handle):
    _omap = {}
    _i = 0
    _code, _val = get_group(handle)
    while True:
        if _code != 0:
            raise ValueError, "Expected code 0: got %d" % _code
        if _val == 'EOF' or _val == 'ENDSEC':
            break
        _odata = []
        _odata.append((_code, _val)) # object type is _val
        while True:
            _code, _val = get_group(handle)
            if _code == 0: # either next object or end of section
                break
            _odata.append((_code, _val))
        _omap[_i] = _odata
        _i = _i + 1
    return _omap

def get_group(handle):
    _code = int(handle.readline())
    _dfun = get_data_type(_code)
    _data = _dfun(handle.readline())
    return _code, _data

def string_data(text):
    return text.strip()

def float_data(text):
    return float(text)

def int_data(text):
    return int(text)

def unicode_data(text):
    return unicode(text.strip())

def handle_data(text):
    return int(text.strip(), 16) # fixme

def hex_data(text):
    return int(text.strip(), 16) # ???

def bin_data(text):
    _str = text.strip()
    _bytes = []
    if not len(_str) % 2: # even length -> good data ...
        for _i in range(0, len(_str), 2):
            _bytes.append(chr(int(_str[_i:_i+2], 16)))
    return _bytes
        
def bool_data(text):
    _btext = text.strip()
    if _btext == '0':
        _flag = False
    elif _btext == '1':
        _flag = True
    else:
        raise ValueError, "Unexpected boolean data string: %s" % _btext
    return _flag

def get_data_type(code):
    if (0 <= code <= 9):
        _dfun = string_data
    elif (10 <= code <= 59):
        _dfun = float_data
    elif (60 <= code <= 79):
        _dfun = int_data # 16-bit int
    elif (90 <= code <= 99):
        _dfun = int_data # 32-bit int
    elif (code == 100):
        _dfun = unicode_data
    elif (code == 102):
        _dfun = unicode_data
    elif (code == 105):
        _dfun = handle_data
    elif (110 <= code <= 139):
        _dfun = float_data # not in dxf spec
    elif (140 <= code <= 149): # says 147 in dxf spec
        _dfun = float_data
    elif (170 <= code <= 179): # says 175 in dxf spec
        _dfun = int_data # 16-bit int
    elif (270 <= code <= 279):
        _dfun = int_data # not in dxf spec
    elif (280 <= code <= 289):
        _dfun = int_data # 8-bit int
    elif (290 <= code <= 299):
        _dfun = bool_data
    elif (300 <= code <= 309):
        _dfun = string_data
    elif (310 <= code <= 319):
        _dfun = bin_data
    elif (320 <= code <= 329):
        _dfun = handle_data
    elif (330 <= code <= 369):
        _dfun = hex_data
    elif (370 <= code <= 379):
        _dfun = int_data # 8-bit int
    elif (380 <= code <= 389):
        _dfun = int_data # 8-bit int
    elif (390 <= code <= 399):
        _dfun = handle_data
    elif (400 <= code <= 409):
        _dfun = int_data # 16-bit int
    elif (410 <= code <= 419):
        _dfun = string_data
    elif (code == 999):
        _dfun = string_data # comment
    elif (1000 <= code <= 1009):
        _dfun = string_data
    elif (1010 <= code <= 1059):
        _dfun = float_data
    elif (1060 <= code <= 1070):
        _dfun = int_data # 16-bit int
    elif (code == 1071):
        _dfun = int_data # 32-bit int
    else:
        raise ValueError, "Unexpected code: %d" % code
    return _dfun

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: dxf.py filename"
        sys.exit(1)
    try:
        _fh = file(sys.argv[1])
    except:
        print "failed to open '%s'. Exiting ..." % sys.argv[1]
        sys.exit(1)
    read_dxf(_fh)
    _fh.close()
