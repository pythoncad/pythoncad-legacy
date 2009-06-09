#
# Copyright (c) 2002, 2003, 2004, 2005 Art Haas
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
# classes for points
#

from __future__ import generators

import math

from PythonCAD.Generic import tolerance
from PythonCAD.Generic import util
from PythonCAD.Generic import baseobject
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import entity

class Point(baseobject.Subpart):
    """A 2-D point Class.

A Point has the following attributes:

x: x-coordinate
y: y-coordinate

A Point object has the following methods:

{get/set}x(): Get/Set the x-coordinate of the Point.
{get/set}y(): Get/Set the y-coordinate of the Point.
{get/set}Coords(): Get/Set both the x and y coordinates of the Point.
move(): Move a Point.
clone(): Return an identical copy of a Point.
inRegion(): Returns True if the point is in some area.
    """
    __messages = {
        'moved' : True,
        }
    # member functions

    def __init__(self, x, y=None, **kw):
        """Initialize a Point.

There are two ways to initialize a Point:

Point(xc,yc) - Two arguments, with both arguments being floats
Point((xc,yc)) - A single tuple containing two float objects
        """
        super(Point, self).__init__(**kw)
        if isinstance(x, tuple):
            if y is not None:
                raise SyntaxError, "Invalid call to Point()"
            _x, _y = util.tuple_to_two_floats(x)
        elif y is not None:
            _x = util.get_float(x)
            _y = util.get_float(y)
        else:
            raise SyntaxError, "Invalid call to Point()."
        self.__x = _x
        self.__y = _y

    def __str__(self):
        return "(%g,%g)" % (self.__x, self.__y)

    def __sub__(self, p):
        """Return the separation between two points.

This function permits the use of '-' to be an easy to read
way to find the distance between two Point objects.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid type for Point subtraction: " + `type(p)`
        _px, _py = p.getCoords()
        return math.hypot((self.__x - _px), (self.__y - _py))

    def __eq__(self, obj):
        """Compare a Point to either another Point or a tuple for equality.
        """
        if not isinstance(obj, (Point,tuple)):
            return False
        if isinstance(obj, Point):
            if obj is self:
                return True
            _x, _y = obj.getCoords()
        else:
            _x, _y = util.tuple_to_two_floats(obj)
        if abs(self.__x - _x) < 1e-10 and abs(self.__y - _y) < 1e-10:
            return True
        return False

    def __ne__(self, obj):
        """Compare a Point to either another Point or a tuple for inequality.
        """
        if not isinstance(obj, (Point,tuple)):
            return True
        if isinstance(obj, Point):
            if obj is self:
                return False
            _x, _y = obj.getCoords()
        else:
            _x, _y = util.tuple_to_two_floats(obj)
        if abs(self.__x - _x) < 1e-10 and abs(self.__y - _y) < 1e-10:
            return False
        return True

    def finish(self):
        self.__x = self.__y = None
        super(Point, self).finish()

    def getValues(self):
        """Return values comprising the Point.

getValues()

This method extends the Subpart::getValues() method.
        """
        _data = super(Point, self).getValues()
        _data.setValue('type', 'point')
        _data.setValue('x', self.__x)
        _data.setValue('y', self.__y)
        return _data

    def getx(self):
        """Return the x-coordinate of a Point.

getx()
        """
        return self.__x

    def setx(self, val):
        """Set the x-coordinate of a Point

setx(val)

The argument 'val' must be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Coordinate change not allowed - object locked."
        _v = util.get_float(val)
        _x = self.__x
        if abs(_x - _v) > 1e-10:
            self.startChange('moved')
            self.__x = _v
            self.endChange('moved')
            self.sendMessage('moved', _x, self.__y)
            self.modified()

    x = property(getx, setx, None, "x-coordinate value")

    def gety(self):
        """Return the y-coordinate of a Point.

gety()
        """
        return self.__y

    def sety(self, val):
        """Set the y-coordinate of a Point

sety(val)

The argument 'val' must be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Coordinate change not allowed - object locked."
        _v = util.get_float(val)
        _y = self.__y
        if abs(_y - _v) > 1e-10:
            self.startChange('moved')
            self.__y = _v
            self.endChange('moved')
            self.sendMessage('moved', self.__x, _y)
            self.modified()

    y = property(gety, sety, None, "y-coordinate value")

    def getCoords(self):
        """Return the x and y Point coordinates in a tuple.

getCoords()
        """
        return self.__x, self.__y

    def setCoords(self, x, y):
        """Set both the coordinates of a Point.

setCoords(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _sx = self.__x
        _sy = self.__y
        if abs(_sx - _x) > 1e-10 or abs(_sy - _y) > 1e-10:
            self.startChange('moved')
            self.__x = _x
            self.__y = _y
            self.endChange('moved')
            self.sendMessage('moved', _sx, _sy)
            self.modified()

    def move(self, dx, dy):
        """Move a Point.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked():
            raise RuntimeError, "Moving not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x = self.__x
            _y = self.__y
            self.startChange('moved')
            self.__x = _x + _dx
            self.__y = _y + _dy
            self.endChange('moved')
            self.sendMessage('moved', _x, _y)
            self.modified()

    def clone(self):
        """Create an identical copy of a Point.

clone()
        """
        return Point(self.__x, self.__y)

    def inRegion(self, xmin, ymin, xmax, ymax, fully=True):
        """Returns True if the Point is within the bounding values.

inRegion(xmin, ymin, xmax, ymax)

The four arguments define the boundary of an area, and the
function returns True if the Point lies within that area.
Otherwise, the function returns False.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        util.test_boolean(fully)
        _x = self.__x
        _y = self.__y
        return not ((_x < _xmin) or
                    (_x > _xmax) or
                    (_y < _ymin) or
                    (_y > _ymax))

    def sendsMessage(self, m):
        if m in Point.__messages:
            return True
        return super(Point, self).sendsMessage(m)

#
# Quadtree Point storage
#

class PointQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(PointQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 2:
            raise ValueError, "Expected 2 arguments, got %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_x < _xmin) or
                (_y < _ymin) or
                (_x > _xmax) or
                (_y > _ymax)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = False
                #
                # NE node (xmid,ymid) to (xmax,ymax)
                #
                if not ((_x < _xmid) or (_y < _ymid)):
                    _ne = True
                #
                # NW node (xmin,ymid) to (xmid,ymax)
                #
                if not ((_x > _xmid) or (_y < _ymid)):
                    _nw = True
                #
                # SW node (xmin,ymin) to (xmid,ymid)
                #
                if not ((_x > _xmid) or (_y > _ymid)):
                    _sw = True
                #
                # SE node (xmid,ymin) to (xmax,ymid)
                #
                if not ((_x < _xmid) or (_y > _ymid)):
                    _se = True
                if _ne:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.NENODE))
                if _nw:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.NWNODE))
                if _sw:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.SWNODE))
                if _se:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.SENODE))
            else:
                yield _node

    def addObject(self, obj):
        if not isinstance(obj, Point):
            raise TypeError, "Invalid Point object: " + `type(obj)`
        if obj in self:
            return
        _x, _y = obj.getCoords()
        _bounds = self.getTreeRoot().getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _x - 1.0
            _ymin = _y - 1.0
            _xmax = _x + 1.0
            _ymax = _y + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _x < _xmin:
                _xmin = _x - 1.0
                _resize = True
            if _x > _xmax:
                _xmax = _x + 1.0
                _resize = True
            if _y < _ymin:
                _ymin = _y - 1.0
                _resize = True
            if _y > _ymax:
                _ymax = _y + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_x, _y):
            _node.addObject(obj)
        super(PointQuadtree, self).addObject(obj)
        obj.connect('moved', self._movePoint)

    def delObject(self, obj):
        if obj not in self:
            return
        _x, _y = obj.getCoords()
        for _node in self.getNodes(_x, _y):
            _node.delObject(obj)
            _parent = _node.getParent()
            if _parent is not None:
                self.purgeSubnodes(_parent)
        super(PointQuadtree, self).delObject(obj)
        obj.disconnect(self)

    def find(self, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _t = tolerance.TOL
        if _alen > 2 :
            _t = tolerance.toltest(args[2])
        return self.getInRegion((_x - _t), (_y - _t), (_x + _t), (_y + _t))

    def _movePoint(self, obj, *args):
        if obj not in self:
            raise ValueError, "Point not stored in Quadtree: " + `obj`
        _alen = len(args)
        if len(args) < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        for _node in self.getNodes(_x, _y):
            _node.delObject(obj)
        super(PointQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        return self.find(x, y, tol)

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _pts = []
        if not len(self):
            return _pts
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                for _subnode in _node.getSubnodes():
                    _sxmin, _symin, _sxmax, _symax = _subnode.getBoundary()
                    if ((_sxmin > _xmax) or
                        (_symin > _ymax) or
                        (_sxmax < _xmin) or
                        (_symax < _ymin)):
                        continue
                    _nodes.append(_subnode)
            else:
                for _pt in _node.getObjects():
                    if _pt.inRegion(_xmin, _ymin, _xmax, _ymax):
                        _pts.append(_pt)
        return _pts

#
# Point history class
#

class PointLog(entity.EntityLog):
    def __init__(self, p):
        if not isinstance(p, Point):
            raise TypeError, "Invalid point: " + `type(p)`
        super(PointLog, self).__init__(p)
        p.connect('moved', self.__movePoint)

    def __movePoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = args[0]
        if not isinstance(_x, float):
            raise TypeError, "Unexpected type for 'x': " + `type(_x)`
        _y = args[1]
        if not isinstance(_y, float):
            raise TypeError, "Unexpected type for 'y': " + `type(_y)`
        self.saveUndoData('moved', _x, _y)

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _p = self.getObject()
        _op = args[0]
        if _op == 'moved':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _x = args[1]
            if not isinstance(_x, float):
                raise TypeError, "Unexpected type for 'x': " + `type(_x)`
            _y = args[2]
            if not isinstance(_y, float):
                raise TypeError, "Unexpected type for 'y': " + `type(_y)`
            _px, _py = _p.getCoords()
            self.ignore(_op)
            try:
                if undo:
                    _p.startUndo()
                    try:
                        _p.setCoords(_x, _y)
                    finally:
                        _p.endUndo()
                else:
                    _p.startRedo()
                    try:
                        _p.setCoords(_x, _y)
                    finally:
                        _p.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _px, _py)
        else:
            super(PointLog, self).execute(undo, *args)
