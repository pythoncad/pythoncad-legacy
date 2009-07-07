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
# construction circle class
#

from __future__ import generators

import math

from PythonCAD.Generic import point
from PythonCAD.Generic import conobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import util

class CCircle(conobject.ConstructionObject):
    """A class for contruction circles

A CCircle has two attributes:

center: A Point object
radius: The CCircle's radius

A CCircle has the following methods:

{get/set}Center(): Get/Set the center Point of a CCircle.
{get/set}Radius(): Get/Set the radius of a CCircle.
move(): Move the CCircle.
circumference(): Get the CCircle's circumference.
area(): Get the CCircle's area.
mapCoords(): Find the nearest Point on the CCircle to a coordinate pair.
inRegion(): Returns whether or not a CCircle can be seen in a bounded area.
clone(): Return an indentical copy of a CCircle.
    """

    __messages = {
        'moved' : True,
        'center_changed' : True,
        'radius_changed' : True,
        }

    def __init__(self, center, radius, **kw):
        """Initialize a CCircle.

CCircle(center, radius)

The center should be a Point, or a two-entry tuple of floats,
and the radius should be a float greater than 0.
        """
        _cp = center
        if not isinstance(_cp, point.Point):
            _cp = point.Point(center)
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        super(CCircle, self).__init__(**kw)
        self.__radius = _r
        self.__center = _cp
        _cp.connect('moved', self.__movePoint)
        _cp.connect('change_pending', self.__pointChangePending)
        _cp.connect('change_complete', self.__pointChangeComplete)
        _cp.storeUser(self)

    def __eq__(self, obj):
        """Compare a CCircle to another for equality.
        """
        if not isinstance(obj, CCircle):
            return False
        if obj is self:
            return True
        _val = False
        if self.__center == obj.getCenter():
            if abs(self.__radius - obj.getRadius()) < 1e-10:
                _val = True
        return _val

    def __ne__(self, obj):
        """Compare a CCircle to another for inequality.
        """
        if not isinstance(obj, CCircle):
            return True
        if obj is self:
            return False
        _val = True
        if self.__center == obj.getCenter():
            if abs(self.__radius - obj.getRadius()) < 1e-10:
                _val = False
        return _val

    def finish(self):
        self.__center.disconnect(self)
        self.__center.freeUser(self)
        self.__center = self.__radius = None
        super(CCircle, self).finish()

    def getValues(self):
        _data = super(CCircle, self).getValues()
        _data.setValue('type', 'ccircle')
        _data.setValue('center', self.__center.getID())
        _data.setValue('radius', self.__radius)
        return _data

    def getCenter(self):
        """Return the center Point of the CCircle.

getCenter()
        """
        return self.__center

    def setCenter(self, c):
        """Set the center Point of the CCircle.

setCenter(c)

The argument must be a Point or a tuple containing
two float values.
        """
        if self.isLocked():
            raise RuntimeError, "Setting center not allowed - object locked."
        _cp = self.__center
        if not isinstance(c, point.Point):
            raise TypeError, "Invalid center point: " + `type(c)`
        if _cp is not c:
            _cp.disconnect(self)
            _cp.freeUser(self)
            self.startChange('center_changed')
            self.__center = c
            self.endChange('center_changed')
            self.sendMessage('center_changed', _cp)
            c.connect('moved', self.__movePoint)
            c.connect('change_pending', self.__pointChangePending)
            c.connect('change_complete', self.__pointChangeComplete)
            c.storeUser(self)
            if abs(_cp.x - c.x) > 1e-10 or abs(_cp.y - c.y) > 1e-10:
                self.sendMessage('moved', _cp.x, _cp.y, self.__radius)
            self.modified()

    center = property(getCenter, setCenter, None, "CCircle center")

    def getRadius(self):
        """Return the radius of the the CCircle.

getRadius()
        """
        return self.__radius

    def setRadius(self, radius):
        """Set the radius of the CCircle.

setRadius(radius)

The argument must be float value greater than 0.
        """
        if self.isLocked():
            raise RuntimeError, "Setting radius not allowed - object locked."
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        _cr = self.__radius
        if abs(_cr - _r) > 1e-10:
            self.startChange('radius_changed')
            self.__radius = _r
            self.endChange('radius_changed')
            self.sendMessage('radius_changed', _cr)
            _cx, _cy = self.__center.getCoords()
            self.sendMessage('moved', _cx, _cy, _cr)
            self.modified()

    radius = property(getRadius, setRadius, None, "CCircle radius")

    def move(self, dx, dy):
        """Move a CCircle.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked():
            raise RuntimeError, "Setting radius not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x, _y = self.__center.getCoords()
            self.ignore('moved')
            try:
                self.__center.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _x, _y, self.__radius)

    def circumference(self):
        """Return the circumference of the CCircle.

circumference()
        """
        return 2.0 * math.pi * self.__radius

    def area(self):
        """Return the area enclosed by the CCircle.

area()
        """
        return math.pi * pow(self.__radius, 2)

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the CCircle to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the x-coordinate
y: A Float value giving the y-coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the CCircle. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _cx, _cy = self.__center.getCoords()
        _r = self.__radius
        _dist = math.hypot((_x - _cx), (_y - _cy))
        if abs(_dist - _r) < _t:
            _angle = math.atan2((_y - _cy),(_x - _cx))
            _xoff = _r * math.cos(_angle)
            _yoff = _r * math.sin(_angle)
            return (_cx + _xoff), (_cy + _yoff)
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not an CCircle exists within a region.

inRegion(xmin, ymin, xmax, ymax[, fully])

The first four arguments define the boundary. The optional
fifth argument 'fully' indicates whether or not the CCircle
must be completely contained within the region or just pass
through it.
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
        _xc, _yc = self.__center.getCoords()
        _r = self.__radius
        #
        # cheap test to see if ccircle cannot be in region
        #
        if (((_xc - _r) > _xmax) or
            ((_yc - _r) > _ymax) or
            ((_xc + _r) < _xmin) or
            ((_yc + _r) < _ymin)):
            return False
        _val = False
        _bits = 0        
        #
        # calculate distances from center to region boundary
        #
        if abs(_xc - _xmin) < _r: _bits = _bits | 1 # left edge
        if abs(_xc - _xmax) < _r: _bits = _bits | 2 # right edge
        if abs(_yc - _ymin) < _r: _bits = _bits | 4 # bottom edge
        if abs(_yc - _ymax) < _r: _bits = _bits | 8 # top edge
        if _bits == 0:
            #
            # if the ccircle center is in region then the entire
            # ccircle is visible since the distance from the center
            # to any edge is greater than the radius. If the center
            # is not in the region then the ccircle is not visible in
            # the region because the distance to any edge is greater
            # than the radius, and so one of the bits should have been
            # set ...
            #
            if ((_xmin < _xc < _xmax) and (_ymin < _yc < _ymax)):
                _val = True
        else:
            _val = True
            #
            # calculate distance to corners of region
            #
            if math.hypot((_xc - _xmin), (_yc - _ymax)) < _r:
                _bits = _bits | 0x10 # upper left
            if math.hypot((_xc - _xmax), (_yc - _ymin)) < _r:
                _bits = _bits | 0x20 # lower right
            if math.hypot((_xc - _xmin), (_yc - _ymin)) < _r:
                _bits = _bits | 0x40 # lower left
            if math.hypot((_xc - _xmax), (_yc - _ymax)) < _r:
                _bits = _bits | 0x80 # upper right
            #
            # if all bits are set then distance from ccircle center
            # to region endpoints is less than radius - ccircle
            # entirely outside the region
            #
            if _bits == 0xff or fully:
                _val = False
        return _val

    def __pointChangePending(self, p, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if args[0] == 'moved':
            self.startChange('moved')

    def __pointChangeComplete(self, p, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if args[0] == 'moved':
            self.endChange('moved')

    def __movePoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _cp = self.__center
        if p is not _cp:
            raise ValueError, "Point is not ccircle center: " + `p`
        _x, _y = _cp.getCoords()
        self.sendMessage('moved', _x, _y, self.__radius)

    def clone(self):
        """Create an identical copy of a CCircle

clone()
        """
        _cp = self.__center.clone()
        return CCircle(_cp, self.__radius)

    def sendsMessage(self, m):
        if m in CCircle.__messages:
            return True
        return super(CCircle, self).sendsMessage(m)

#
# Quadtree CCircle storage
#

class CCircleQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(CCircleQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 3:
            raise ValueError, "Expected 3 arguments, got %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        _cxmin = _x - _r
        _cxmax = _x + _r
        _cymin = _y - _r
        _cymax = _y + _r
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_cxmin > _xmax) or
                (_cxmax < _xmin) or
                (_cymin > _ymax) or
                (_cymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _cxmax < _xmid: # circle on left side
                    _ne = _se = False
                if _cxmin > _xmid: # circle on right side
                    _nw = _sw = False
                if _cymax < _ymid: # circle below
                    _nw = _ne = False
                if _cymin > _ymid: # circle above
                    _sw = _se = False
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
        if not isinstance(obj, CCircle):
            raise TypeError, "Invalid CCircle object: " + `type(obj)`
        if obj in self:
            return
        _x, _y = obj.getCenter().getCoords()
        _r = obj.getRadius()
        _node = self.getTreeRoot()
        _bounds = _node.getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _cxmin = _x - _r
        _cxmax = _x + _r
        _cymin = _y - _r
        _cymax = _y + _r
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _cxmin - 1.0
            _ymin = _cymin - 1.0
            _xmax = _cxmax + 1.0
            _ymax = _cymax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _cxmin < _xmin:
                _xmin = _cxmin - 1.0
                _resize = True
            if _cxmax > _xmax:
                _xmax = _cxmax + 1.0
                _resize = True
            if _cymin < _ymin:
                _ymin = _cymin - 1.0
                _resize = True
            if _cymax > _ymax:
                _ymax = _cymax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_x, _y, _r):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(CCircleQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveCCircle)

    def delObject(self, obj):
        if obj not in self:
            return
        _x, _y = obj.getCenter().getCoords()
        _r = obj.getRadius()
        _pdict = {}
        for _node in self.getNodes(_x, _y, _r):
            _node.delObject(obj) # ccircle may not be in the node ...
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(CCircleQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        _t = tolerance.TOL
        if _alen > 3:
            _t = tolerance.toltest(args[4])
        _xmin = _x - _r - _t
        _xmax = _x + _r + _t
        _ymin = _y - _r - _t
        _ymax = _y + _r + _t
        _ccircles = []
        for _ccirc in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _cx, _cy = _ccirc.getCenter().getCoords()
            if ((abs(_cx - _x) < _t) and
                (abs(_cy - _y) < _t) and
                (abs(_ccirc.getRadius() - _r) < _t)):
                _ccircles.append(_ccirc)
        return _ccircles

    def _moveCCircle(self, obj, *args):
        if obj not in self:
            raise ValueError, "CCircle not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        for _node in self.getNodes(_x, _y, _r):
            _node.delObject(obj) # ccircle may not be in node ...
        super(CCircleQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _circ = _tsep = None
        _bailout = False
        _cdict = {}
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_x < (_xmin - _t)) or
                (_x > (_xmax + _t)) or
                (_y < (_ymin - _t)) or
                (_y > (_ymax + _t))):
                continue
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _c in _node.getObjects():
                    _cid = id(_c)
                    if _cid not in _cdict:
                        _cp = _c.mapCoords(_x, _y, _t)
                        if _cp is not None:
                            _cx, _cy = _cp
                            _sep = math.hypot((_cx - _x), (_cy - _y))
                            if _tsep is None:
                                _tsep = _sep
                                _circ = _c
                            else:
                                if _sep < _tsep:
                                    _tsep = _sep
                                    _circ = _c
                            if _sep < 1e-10 and _circ is not None:
                                _bailout = True
                                break
            if _bailout:
                break
        return _circ

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _circs = []
        if not len(self):
            return _circs
        _nodes = [self.getTreeRoot()]
        _cdict = {}
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
                for _circ in _node.getObjects():
                    _cid = id(_circ)
                    if _cid not in _cdict:
                        if _circ.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _circs.append(_circ)
                        _cdict[_cid] = True
        return _circs

#
# CCircle history class
#

class CCircleLog(conobject.ConstructionObjectLog):
    def __init__(self, c):
        if not isinstance(c, CCircle):
            raise TypeError, "Invalid CCircle object: " + `type(c)`
        super(CCircleLog, self).__init__(c)
        c.connect('center_changed' ,self._centerChange)
        c.connect('radius_changed', self._radiusChange)

    def _radiusChange(self, c, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _r = args[0]
        if not isinstance(_r, float):
            raise TypeError, "Unexpected type for radius: " + `type(_r)`
        self.saveUndoData('radius_changed', _r)

    def _centerChange(self, c, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old center point: " + `type(_old)`
        self.saveUndoData('center_changed', _old.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _c = self.getObject()
        _cp = _c.getCenter()
        _op = args[0]
        if _op == 'radius_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _r = args[1]
            if not isinstance(_r, float):
                raise TypeError, "Unexpected type for radius: " + `type(_r)`
            _sdata = _c.getRadius()
            self.ignore(_op)
            try:
                if undo:
                    _c.startUndo()
                    try:
                        _c.setRadius(_r)
                    finally:
                        _c.endUndo()
                else:
                    _c.startRedo()
                    try:
                        _c.setRadius(_r)
                    finally:
                        _c.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'center_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _parent = _c.getParent()
            if _parent is None:
                raise ValueError, "CCircle has no parent - cannot undo"
            _pt = _parent.getObject(_oid)
            if _pt is None or not isinstance(_pt, point.Point):
                raise ValueError, "Center point missing: id=%d" % _oid
            _sdata = _cp.getID()
            self.ignore(_op)
            try:
                if undo:
                    _c.startUndo()
                    try:
                        _c.setCenter(_pt)
                    finally:
                        _c.endUndo()
                else:
                    _c.startRedo()
                    try:
                        _c.setCenter(_pt)
                    finally:
                        _c.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(CCircleLog, self).execute(undo, *args)
