#!/usr/bin/python
#
# simply binary dump
#

import sys
import array

if len(sys.argv) < 4:
    print "bindump.py file offset count"
    sys.exit(1)
else:
    try:
        _fname = file(sys.argv[1])
    except:
        print "invalid file: " + sys.argv[1]
        sys.exit(1)
    try:
        _offset = int(sys.argv[2])
    except:
        print "invalid offset: " + sys.argv[2]
        sys.exit(1)
    if _offset < 0:
        print "invalid offset: %d" % _offset
        sys.exit(1)
    try:
        _count = int(sys.argv[3])
    except:
        print "invalid byte count: " + sys.argv[3]
        sys.exit(1)
    if _count < 0:
        print "invalid byte count: %d" % _count
        sys.exit(1)

print "opening file: " + _fname.name
print "offset: %d" % _offset
print "count: %d" % _count 

try:
    _fname.seek(_offset, 0)
except:
    _fname.close()
    print "invalid offset into file: %d" % _offset
    sys.exit(1)

_data = array.array('B')
try:
    _data.fromfile(_fname, _count)
except:
    _fname.close()
    print "invalid read of %d bytes from file: %s" % (_count, _fname.name)
    sys.exit(1)

_fname.close()

_patterns = [
    '0 0 0 0', # 0
    '0 0 0 1', # 1
    '0 0 1 0', # 2
    '0 0 1 1', # 3
    '0 1 0 0', # 4
    '0 1 0 1', # 5
    '0 1 1 0', # 6
    '0 1 1 1', # 7
    '1 0 0 0', # 8
    '1 0 0 1', # 9
    '1 0 1 0', # A
    '1 0 1 1', # B
    '1 1 0 0', # C
    '1 1 0 1', # D
    '1 1 1 0', # E
    '1 1 1 1'  # F
    ]

_i = 0
while (_i < _count):
    _bitoffset = _i * 8
    _nib1 = _patterns[((_data[_i] & 0xf0) >> 4)]
    _nib2 = _patterns[(_data[_i] & 0x0f)]
    print "%d [%d]: 0x%02x %s %s" % (_i, _bitoffset, _data[_i], _nib1, _nib2)
    _i = _i + 1
