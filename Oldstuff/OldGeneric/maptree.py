#
# Copyright (c) 2002, 2003 Art Haas
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
# A PointMapTree and PointBMapTree extend a basic Tree
#

from PythonCAD.Generic import point
from PythonCAD.Generic import util
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import tree

class PointMapTree(tree.Tree):
    """A Tree class that containing objects that have Point objects.

The PointMapTree is based on the Tree class, so it shares all
the functionality of that class.

There is one extra method in the PointMapTree

mapPoint(): Find objects in the tree that a Point could fall upon.

Any class stored in this tree must provide a mapPoint() method.
The format of that method is as follows:

mapPoint(p[, tol])

p: Either a Point object or a two-float tuple

Optional argument:

tol: The tolerance used for testing the Point's proximity to the object.

A class should also have a __cmp__ method that can handle an instance
of the class being compared to a Point.
    """
    def __init__(self, t):
        """Instantiate a PointMapTree.

PointMapTree(t)

This function has one required argument:

t: The type of object stored in the tree.
        """
        tree.Tree.__init__(self, t)

    def mapPoint(self, p, tol=tolerance.TOL, count=2):
        """See if an object in the PointMapTree exists at a Point.

mapPoint(p [, tol, count])

This method has one required parameter:

p: Either a Point object or a tuple of two-floats

There are two optional arguments:

tol: A float equal or greater than 0 used to decide if the
     point is close enough to the objects held in the Tree.

count: An integer indicating the maximum number of objects
       to return. By default this value is 2.

The function returns a list of at tuples, each of the form

(obj, pt)

obj: Object that the Point is mapped to
pt: The projected Point on the object
        """
        _p = p
        if not isinstance(_p, (point.Point, tuple)):
            raise TypeError, "Invalid type for searching in PointMapTree: " + `_p`            
        if isinstance(_p, tuple):
            _x, _y = util.tuple_to_two_floats(_p)
            _p = point.Point(_x, _y)
        _t = tolerance.toltest(tol)
        _count = count
        if not isinstance(_count, int):
            _count = int(count)
        if _count < 0:
            raise ValueError, "Invalid count: %d" % _count
        _objlist = []
        for _obj in self:
            _pt = _obj.mapPoint(_p, _t)
            if _pt is not None:
                _objlist.append((_obj, _pt))
            if len(_objlist) == _count or cmp(_obj, _p) == 1:
                break
        return _objlist

class PointBMapTree(PointMapTree):
    """A Tree class that containing objects that have Point objects.

The PointBMapTree is based on the PointMapTree class, so it shares all
the functionality of that class. The PointBMapTree uses a binary
scan search on objects in the tree to find a particular object, where
the PointMapTree uses a linear search. This implies that any
PointBMapTree will only contain at most one object that a Point
object may be mapped on to.
    """
    def __init__(self, t):
        """Instantiate a PointBMapTree.

PointBMapTree(t)

This function has one required argument:

t: The type of object stored in the tree.
        """
        PointMapTree.__init__(self, t)

    def mapPoint(self, p, tol=tolerance.TOL):
        """See if an object in the PointBMapTree exists at a Point.

mapPoint(p [, tol])

This method has one required parameter:

p: Either a Point object or a tuple of two-floats

There is a single optional argument:

tol: A float equal or greater than 0 used to decide if the
     point is close enough to the objects held in the Tree.

The function returns a list of at tuples, each of the form

(obj, pt)

obj: Object that the Point is mapped to
pt: The projected Point on the object

The list will contain at most two tuples.
        """
        _p = p
        if not isinstance(_p, (point.Point, tuple)):
            raise TypeError, "Invalid type for searching in PointMapTree: " + `_p`            
        if isinstance(_p, tuple):
            _x, _y = util.tuple_to_two_floats(_p)
            _p = point.Point(_x, _y)
        _t = tolerance.toltest(tol)
        _objlist = []
        _scanlist = []        
        _lo = 0
        _hi = len(self)
        while _lo < _hi:
            _mid = (_hi+_lo)//2
            if _mid in _scanlist:
                break
            _scanlist.append(_mid)
            _obj = self[_mid]
            _res = cmp(_obj, _p)
            if _res == -1:
                _lo = _mid + 1
            elif _res == 1:
                _hi = _mid
            else:
                _pt = _obj.mapPoint(_p, _t)
                if _pt is not None:
                    _objlist.append((_obj, _pt))
                break
        return _objlist

