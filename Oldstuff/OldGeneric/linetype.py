#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
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
# linetype class
#

import types
from sys import maxint

from PythonCAD.Generic import globals

class Linetype(object):
    """A class representing linetypes.

This class provides the basis for solid and dashed lines.
Dashed lines are more 'interesting' in the various ways
the dashes can be drawn.

A Linetype object has two attributes:

name: A string describing this linetype
dlist: A list of integers used for drawing dashed lines

A solid line has a dlist attribute of None.

A Linetype object has the following methods:

getName(): Return the Linetype name
getList(): Return the Linetype dashlist
clone(): Make a copy of a Linetype object.
    """
    def __init__(self, name, dashlist=None):
        """Initstantiate a Linetype object.

Linetype(name, dashlist)

The name should be a string representing what this linetype
is called. The dashlist can be None (solid lines) or a list of
integers which will be used to determine the on/off bits
of a dashed line. The list must have at least two integers.
        """
        _n = name
        if not isinstance(_n, types.StringTypes):
            raise TypeError, "Invalid Linetype name: " + `_n`
        if not isinstance(_n, unicode):
            _n = unicode(name)
        _l = dashlist
        if _l is not None:
            if not isinstance(_l, list):
                raise TypeError, "Second argument must be a list or None."
            _length = len(_l)
            if _length < 2:
                raise ValueError, "Dash list must hold at least two integers."
            _temp = []
            for _i in range(_length):
                _item = _l[_i]
                if not isinstance(_item, int):
                    _item = int(_l[_i])
                if _item < 0:
                    raise ValueError, "Invalid list value: %d" % _item
                _temp.append(_item)
            _l = _temp
        self.__name = _n
        if _l is None:
            self.__list = None
        else:
            self.__list = _l[:]

    def __str__(self):
        if self.__list is None:
            return "Solid Line: '%s'" % self.__name
        else:
            _str = "Dashed Line: '%s': " % self.__name
            return _str + `self.__list`
        
    def __eq__(self, obj):
        """Compare one Linetype to another for equality.

The comparison examines the dash list - if both lists
are None, or the same length and with identical values,
the function returns True. Otherwise the function returns
False.
        """
        if not isinstance(obj, Linetype):
            return False
        if obj is self:
            return True
        _slist = self.__list
        _olist = obj.getList()
        return ((_slist is None and _olist is None) or
                ((type(_slist) == type(_olist)) and (_slist == _olist)))

    def __ne__(self, obj):
        """Compare one Linetype to another for non-equality.

The comparison examines the dash list - if both lists
are None, or the same length and with identical values,
the function returns False. Otherwise the function returns
True.
        """
        return not self == obj

    def __hash__(self):
        """Provide a hash function for Linetypes.

Defining this method allows Linetype objects to be stored
as dictionary keys.
        """
        _dashlist = self.__list
        _val = 0 # hash value for solid lines
        if _dashlist is not None:
            _val = hash_dashlist(_dashlist)
        return _val
    
    def getName(self):
        """Get the name of the Linetype.

getName()        
        """
        return self.__name

    name = property(getName, None, None, "Linetype name.")

    def getList(self):
        """Get the list used for determining the dashed line pattern.

getList()
This function returns None for solid Linetypes.
        """
        _list = None
        if self.__list is not None:
            _list = self.__list[:]
        return _list

    list = property(getList, None, None, "Linetype dash list.")

    def clone(self):
        """Make a copy of a Linetype

clone()        
        """
        _name = self.__name[:]
        _dashlist = None
        if self.__list is not None:
            _dashlist = self.__list[:]
        return Linetype(_name, _dashlist)

#
# LinetypeDict Class
#
# The LinetypeDict is built from the dict object. Using instances
# of this class will guarantee than only Linetype objects will be
# stored in the instance
#

class LinetypeDict(dict):
    def __init__(self):
        super(LinetypeDict, self).__init__()
        
    def __setitem__(self, key, value):
        if not isinstance(key, Linetype):
            raise TypeError, "LinetypeDict keys must be Linetype objects: " + `key`
        if not isinstance(value, Linetype):
            raise TypeError, "LinetypeDict values must be Linetype objects: " + `value`
        super(LinetypeDict, self).__setitem__(key, value)

#
# the hash function for linetype dashlists
#

def hash_dashlist(dashlist):
    """The hashing function for linetype dashlists

hash_dashlist(dashlist)

Argument 'dashlist' should be a list containing two or
more integer values.
    """
    if not isinstance(dashlist, list):
        raise TypeError, "Invalid list: " + `dashlist`
    if len(dashlist) < 2:
        raise ValueError, "Invalid list length: " + str(dashlist)
    _dlist = []
    for _obj in dashlist:
        if not isinstance(_obj, int):
            raise TypeError, "Invalid list item: " + `_obj`
        if _obj < 0:
            raise ValueError, "Invalid list value: %d" % _obj
        _dlist.append(_obj)
    _val = (0xffffff & _dlist[0]) << 6
    for _i in _dlist:
        _val =  c_mul(160073, _val) ^ ((_i << 5) | _i) # made this up
    _val = _val ^ len(_dlist)
    if _val == -1:
        _val = -2
    return _val

#
# mulitplication used for hashing
#
# an eval-based routine came from http://effbot.org/zone/python-hash.htm,
# but the move to Python 2.3 printed warnings when executing that code
# due to changes in large hex values, so the code was re-written to
# avoid the eval-loop and hackish long->str->int conversions ...
#

def c_mul(a, b):
    _lval = (long(a * b) & 0xffffffffL) - maxint
    return int(_lval)

#
# find an existing linetype in the global linetype dictionary
#

def get_linetype_by_dashes(dashlist):
    if dashlist is None:
        _key = 0
    elif isinstance(dashlist, list):
        _key = hash_dashlist(dashlist)
    else:
        raise TypeError, "Invalid dashlist: " + `dashlist`
    for _k in globals.linetypes.keys():
        if hash(_k) == _key:
            return _k
    raise ValueError, "No matching linetype found: " + str(dashlist)
        
def get_linetype_by_name(name):
    if not isinstance(name, types.StringTypes):
        raise TypeError, "Invalid linetype name: " + str(name)
    _name = name
    if not isinstance(_name, unicode):
        _name = unicode(name)
    for _lt in globals.linetypes:
        if _lt.getName() == _name:
            return _lt
    return None
