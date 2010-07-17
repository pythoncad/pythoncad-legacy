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
# single point construction lines at an arbitrary angle
#

from __future__ import generators

import math

from PythonCAD.Generic import conobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import util
from PythonCAD.Generic import point
from PythonCAD.Generic import quadtree

_dtr = math.pi/180.0

class ACLine(conobject.ConstructionObject):
    """A class for single point construction lines at a specified angle.

A ACLine object is derived from an Spcline,so it has
all that objects properties.

There is one additional attribute for an ACLine:

angle: A float value listing the angle at which this line rises or declines

The limits of the float value: -90.0 < value < 90.0. Any values outside
that range are adjusted to fall between those limits.

A ACLine has the following addtional methods:

{get/set}Angle(): Get/Set the angle of the ACLine.
mapCoords(): Test if a coordinate pair is within some distance to an ACLine.
inRegion(): Return whether or not a ACLine passes through a bounded region.
clone(): Return an identical copy of an ACLine.
    """
    __messages = {
        'moved' : True,
        'keypoint_changed' : True,
        'rotated' : True
        }
        
    def __init__(self, p, a, **kw):
        """Initialize an ACLine object.

ACLine(p, a)

p: A Point object the line passes through
a: The angle at which the line rises or declines
        """
        _a = util.make_angle(a)
        _p = p
        if not isinstance(p, point.Point):
            _p = point.Point(p)
        super(ACLine, self).__init__(**kw)
        self.__keypoint = _p
        self.__angle = _a
        _p.storeUser(self)
        _p.connect('moved', self.__movePoint)
        _p.connect('change_pending', self.__pointChangePending)
        _p.connect('change_complete', self.__pointChangeComplete)

    def __eq__(self, obj):
        """Compare one ACLine to another for equality.
        """
        if not isinstance(obj, ACLine):
            return False
        if obj is self:
            return True
        _as = self.__angle
        _ao = obj.getAngle()
        _xs, _ys = self.getLocation().getCoords()
        _xo, _yo = obj.getLocation().getCoords()
        _val = False
        if (self.isVertical() and
            obj.isVertical() and
            abs(_xs - _xo) < 1e-10):
            _val = True
        elif (self.isHorizontal() and
              obj.isHorizontal() and
              abs(_ys - _yo) < 1e-10):
              _val = True
        else:
            if abs(_as - _ao) < 1e-10: # same angle
                _ms = math.tan(_as * _dtr)
                _bs = _ys - (_ms * _xs)
                _y = (_ms * _xo) + _bs
                if abs(_y - _yo) < 1e-10:
                    _val = True
        return _val

    def __ne__(self, obj):
        """Compare one ACLine to another for inequality.
        """
        if not isinstance(obj, ACLine):
            return False
        if obj is self:
            return False
        _as = self.__angle
        _ao = obj.getAngle()
        _xs, _ys = self.getLocation().getCoords()
        _xo, _yo = obj.getLocation().getCoords()
        _val = True
        if (self.isVertical() and
            obj.isVertical() and
            abs(_xs - _xo) < 1e-10):
            _val = False
        elif (self.isHorizontal() and
              obj.isHorizontal() and
              abs(_ys - _yo) < 1e-10):
              _val = False
        else:
            if abs(_as - _ao) < 1e-10: # same angle
                _ms = math.tan(_as * _dtr)
                _bs = _ys - (_ms * _xs)
                _y = (_ms * _xo) + _bs
                if abs(_y - _yo) < 1e-10:
                    _val = False
        return _val

    def __str__(self):
        _point = self.getLocation()
        _angle = self.__angle
        return "Angled construction line through %s at %g degrees" % (_point, _angle)

    def finish(self):
        self.__keypoint.disconnect(self)
        self.__keypoint.freeUser(self)
        self.__keypoint = self.__angle = None
        super(ACLine, self).finish()

    def getValues(self):
        _data = super(ACLine, self).getValues()
        _data.setValue('type', 'acline')
        _data.setValue('keypoint', self.__keypoint.getID())
        _data.setValue('angle', self.__angle)
        return _data

    def getAngle(self):
        """Return the angle of the ACLine.

getAngle()
        """
        return self.__angle

    def setAngle(self, angle):
        """

setAngle(angle)

The argument a should be a float representing the angle
of the ACLine in degrees.
        """
        if self.isLocked():
            raise RuntimeError, "Setting angle not allowed - object locked."
        _a = util.make_angle(angle)
        _oa = self.__angle
        if abs(_a - _oa) > 1e-10:
            self.startChange('rotated')
            self.__angle = _a
            self.endChange('rotated')
            self.sendMessage('rotated', _oa)
            _x, _y = self.__keypoint.getCoords()
            self.sendMessage('moved', _x, _y, _oa)
            self.modified()

    angle = property(getAngle, setAngle, None, "Angle of inclination.")

    def isVertical(self):
        return abs(abs(self.__angle) - 90.0) < 1e-10

    def isHorizontal(self):
        return abs(self.__angle) < 1e-10

    def getLocation(self):
        return self.__keypoint

    def setLocation(self, p):
        if self.isLocked():
            raise RuntimeError, "Setting keypoint not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Unexpected type for point: " + `type(p)`
        _kp = self.__keypoint
        if p is not _kp:
            _x, _y = _kp.getCoords()
            _kp.disconnect(self)
            _kp.freeUser(self)
            self.startChange('keypoint_changed')
            self.__keypoint = p
            self.endChange('keypoint_changed')
            self.sendMessage('keypoint_changed', _kp)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            p.storeUser(self)
            _px, _py = p.getCoords()
            if abs(_px - _x) > 1e-10 or abs(_py - _y) > 1e-10:
                self.sendMessage('moved', _x, _y, self.getAngle())
            self.modified()

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the ACLine to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the x-coordinate
y: A Float value giving the y-coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the ACLine. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _xs, _ys = self.getLocation().getCoords()
        _angle = self.__angle
        #
        # the second point is 1 unit away - this simplifies things ...
        #
        if self.isHorizontal():
            _x2 = _xs + 1.0
            _y2 = _ys
        elif self.isVertical():
            _x2 = _xs
            _y2 = _ys + 1.0
        else:
            _x2 = _xs + math.cos(_angle * _dtr)
            _y2 = _ys + math.sin(_angle * _dtr)
        _r = ((_x - _xs)*(_x2 - _xs) + (_y - _ys)*(_y2 - _ys))
        _px = _xs + (_r * (_x2 - _xs))
        _py = _ys + (_r * (_y2 - _ys))
        if abs(_px - _x) < _t and abs(_py - _y) < _t:
            return _px, _py
        return None

    def getProjection(self, x, y):
        """Find the projection point of some coordinates on the ACLine.

getProjection(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _x1, _y1 = self.getLocation().getCoords()
        _angle = self.__angle
        if self.isHorizontal():
            _px = _x
            _py = _y1
        elif self.isVertical():
            _px = _x1
            _py = _y
        else:
            _rangle = _angle * _dtr
            _dx = math.cos(_rangle)
            _dy = math.sin(_rangle)
            _sqlen = pow(_dx, 2) + pow(_dy, 2)
            _rn = ((_x - _x1) * _dx) + ((_y - _y1) * _dy)
            _r = _rn/_sqlen
            _px = _x1 + (_r * _dx)
            _py = _y1 + (_r * _dy)
        return _px, _py

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not an ACLine passes through a region.

inRegion(xmin, ymin, xmax, ymax)

The first four arguments define the boundary. The method
will return True if the ACLine passes through the boundary.
Otherwise the function will return False.
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
        if fully:
            return False
        _x, _y = self.getLocation().getCoords()
        _angle = self.__angle
        _val = False
        if _xmin < _x < _xmax and _ymin < _y < _ymax:
            _val = True
        elif self.isHorizontal() and _ymin < _y < _ymax:
            _val = True
        elif self.isVertical() and _xmin < _x < _xmax:
            _val = True
        else:
            #
            # the ACLine can be parameterized as
            #
            # x = u * (x2 - x1) + x1
            # y = u * (y2 - y1) + y1
            #
            # for u = 0, x => x1, y => y1
            # for u = 1, x => x2, y => y2
            #
            # if the ACLine passes through the region then there
            # will be valid u occuring at the region boundary
            #
            _rangle = _angle * _dtr
            _dx = math.cos(_rangle)
            _dy = math.sin(_rangle)
            #
            # x = xmin
            #
            _u = (_xmin - _x)/_dx
            _yt = (_u * _dy) + _y
            if (_ymin - 1e-10) < _yt < (_ymax + 1e-10): # catch endpoints
                _val = True
            if not _val:
                #
                # x = xmax
                #
                _u = (_xmax - _x)/_dx
                _yt = (_u * _dy) + _y
                if (_ymin - 1e-10) < _yt < (_ymax + 1e-10): # catch endpoints
                    _val = True
                if not _val:
                    #
                    # y = ymin
                    #
                    # if this fails there is no way the ACLine can be in
                    # region because it cannot pass through only one side
                    #
                    _u = (_ymin - _y)/_dy
                    _xt = (_u * _dx) + _x
                    if _xmin < _xt < _xmax:
                        _val = True
        return _val

    def move(self, dx, dy):
        """Move an ACLine

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked() or self.__keypoint.isLocked():
            raise RuntimeError, "Moving ACLine not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x, _y = self.__keypoint.getCoords()
            self.ignore('moved')
            try:
                self.__keypoint.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _x, _y, self.getAngle())

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
        _plen = len(args)
        if _plen < 2:
            raise ValueError, "Invalid argument count: %d" % _plen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        if p is not self.__keypoint:
            raise ValueError, "Invalid point for ACLine::movePoint()" + `p`
        _px, _py = p.getCoords()
        if abs(_px - _x) > 1e-10 or abs(_py - _y) > 1e-10:
            self.sendMessage('moved', _x, _y, self.getAngle())

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _x, _y = self.getLocation().getCoords()
        _angle = self.__angle
        _coords = None
        if self.isVertical() and _xmin < _x < _xmax:
            _coords = (_x, _ymin, _x, _ymax)
        elif self.isHorizontal() and _ymin < _y < _ymax:
            _coords = (_xmin, _y, _xmax, _y)
        else:
            #
            # the ACLine can be parameterized as
            #
            # x = u * (x2 - x1) + x1
            # y = u * (y2 - y1) + y1
            #
            # for u = 0, x => x1, y => y1
            # for u = 1, x => x2, y => y2
            #
            # The following is the Liang-Barsky Algorithm
            # for segment clipping modified slightly for
            # construction lines
            #
            _rangle = _angle * _dtr
            _dx = math.cos(_rangle)
            _dy = math.sin(_rangle)
            _P = [-_dx, _dx, -_dy, _dy]
            _q = [(_x - _xmin), (_xmax - _x), (_y - _ymin), (_ymax - _y)]
            _u1 = None
            _u2 = None
            _valid = True
            for _i in range(4):
                _pi = _P[_i]
                _qi = _q[_i]
                if abs(_pi) < 1e-10: # this should be caught earlier ...
                    if _qi < 0.0:
                        _valid = False
                        break
                else:
                    _r = _qi/_pi
                    if _pi < 0.0:
                        if _u2 is not None and _r > _u2:
                            _valid = False
                            break
                        if _u1 is None or _r > _u1:
                            _u1 = _r
                    else:
                        if _u1 is not None and _r < _u1:
                            _valid = False
                            break
                        if _u2 is None or _r < _u2:
                            _u2 = _r
            if _valid:
                _coords = (((_u1 * _dx) + _x),
                           ((_u1 * _dy) + _y),
                           ((_u2 * _dx) + _x),
                           ((_u2 * _dy) + _y))
        return _coords

    def clone(self):
        """Create an identical copy of an ACLine.

clone()
        """
        return ACLine(self.__keypoint.clone(), self.__angle)

    def sendsMessage(self, m):
        if m in ACLine.__messages:
            return True
        return super(ACLine, self).sendsMessage(m)

def intersect_region(acl, xmin, ymin, xmax, ymax):
    if not isinstance(acl, ACLine):
        raise TypeError, "Argument not an ACLine: " + `type(acl)`
    _xmin = util.get_float(xmin)
    _ymin = util.get_float(ymin)
    _xmax = util.get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = util.get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _x, _y = acl.getLocation().getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if acl.isVertical() and _xmin < _x < _xmax:
        _x1 = _x
        _y1 = _ymin
        _x2 = _x
        _y2 = _ymax
    elif acl.isHorizontal() and _ymin < _y < _ymax:
        _x1 = _xmin
        _y1 = _y
        _x2 = _xmax
        _y2 = _y
    else:
        _angle = acl.getAngle()
        _slope = math.tan(_angle * _dtr)
        _yint = _y - (_x * _slope)
        _xt = _x + math.cos(_angle * _dtr)
        _yt = _y + math.sin(_angle * _dtr)
        #
        # find y for x = xmin
        #
        _yt = (_slope * _xmin) + _yint
        if _ymin < _yt < _ymax:
            # print "hit at y for x=xmin"
            _x1 = _xmin
            _y1 = _yt
        #
        # find y for x = xmax
        #
        _yt = (_slope * _xmax) + _yint
        if _ymin < _yt < _ymax:
            # print "hit at y for x=xmax"
            if _x1 is None:
                _x1 = _xmax
                _y1 = _yt
            else:
                _x2 = _xmax
                _y2 = _yt
        if _x2 is None:
            #
            # find x for y = ymin
            #
            _xt = (_ymin - _yint)/_slope
            if _xmin < _xt < _xmax:
                # print "hit at x for y=ymin"
                if _x1 is None:
                    _x1 = _xt
                    _y1 = _ymin
                else:
                    _x2 = _xt
                    _y2 = _ymin
        if _x2 is None:
            #
            # find x for y = ymax
            #
            _xt = (_ymax - _yint)/_slope
            if _xmin < _xt < _xmax:
                # print "hit at x for y=ymax"
                if _x1 is None:
                    _x1 = _xt
                    _y1 = _ymax
                else:
                    _x2 = _xt
                    _y2 = _ymax
    return _x1, _y1, _x2, _y2

#
# Quadtree ACLine storage
#

class ACLineQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(ACLineQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 3:
            raise ValueError, "Expected 3 arguments, got %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _angle = util.get_float(args[2])
        _v = abs(abs(_angle) - 90.0) < 1e-10
        _h = abs(_angle) < 1e-10
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if _node.hasSubnodes():
                _ne = _nw = _sw = _se = False
                if _v:
                    if _x < _xmin or _x > _xmax:
                        continue
                    _xmid = (_xmin + _xmax)/2.0
                    if _x < _xmid: # left of midpoint
                        _nw = _sw = True
                    else:
                        _se = _ne = True
                elif _h:
                    if _y < _ymin or _y > _ymax:
                        continue
                    _ymid = (_ymin + _ymax)/2.0
                    if _y < _ymid: # below midpoint
                        _sw = _se = True
                    else:
                        _nw = _ne = True
                else:
                    _ne = _nw = _sw = _se = True
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
        if not isinstance(obj, ACLine):
            raise TypeError, "Argument not an ACLine: " + `type(obj)`
        if obj in self:
            return
        _x, _y = obj.getLocation().getCoords()
        _angle = obj.getAngle()
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
        for _node in self.getNodes(_x, _y, _angle):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(ACLineQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveACLine)

    def delObject(self, obj):
        if obj not in self:
            return
        _x, _y = obj.getLocation().getCoords()
        _angle = obj.getAngle()
        _pdict = {}
        for _node in self.getNodes(_x, _y, _angle):
            _node.delObject(obj)
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(ACLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _angle = util.make_angle(args[2])
        _t = tolerance.TOL
        if _alen > 3:
            _t = tolerance.toltest(args[3])
        _xmin = _x - _t
        _xmax = _x + _t
        _ymin = _y - _t
        _ymax = _y + _t
        _aclines = []
        for _acl in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _ax, _ay = _acl.getLocation().getCoords()
            if ((abs(_ax - _x) < _t) and
                (abs(_ay - _y) < _t) and
                (abs(_acl.getAngle() - _angle) < 1e-10)):
                _aclines.append(_acl)
        return _aclines

    def _moveACLine(self, obj, *args):
        if obj not in self:
            raise ValueError, "ACLine not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _angle = util.get_float(args[2])
        for _node in self.getNodes(_x, _y, _angle):
            _node.delObject(obj) # acline may not be in node
        super(ACLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _acline = _tsep = None
        _adict = {}
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _a in _node.getObjects():
                    _aid = id(_a)
                    if _aid not in _adict:
                        _ax, _ay = _a.getProjection(_x, _y)
                        if abs(_ax - _x) < _t and abs(_ay - _y) < _t:
                            _sep = math.hypot((_ax - _x), (_ay - _y))
                            if _tsep is None:
                                _tsep = _sep
                                _acline = _a
                            else:
                                if _sep < _tsep:
                                    _tsep = _sep
                                    _acline = _a
        return _acline


    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _acls = []
        if not len(self):
            return _acls
        _nodes = [self.getTreeRoot()]
        _adict = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _acl in _node.getObjects():
                    _aid = id(_acl)
                    if _aid not in _adict:
                        if _acl.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _acls.append(_acl)
                        _adict[_aid] = True
        return _acls

#
# ACLine history class
#

class ACLineLog(conobject.ConstructionObjectLog):
    def __init__(self, a):
        if not isinstance(a, ACLine):
            raise TypeError, "Argument not an ACLine: " + `type(a)`
        super(ACLineLog, self).__init__(a)
        a.connect('keypoint_changed', self._keypointChange)
        a.connect('rotated', self._rotateACLine)

    def _rotateACLine(self, a, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _angle = args[0]
        if not isinstance(_angle, float):
            raise TypeError, "Unexpected type for angle: " + `type(_angle)`
        self.saveUndoData('rotated', _angle)

    def _keypointChange(self, a, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Argument not a Point: " + `type(_old)`
        self.saveUndoData('keypoint_changed', _old.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _a = self.getObject()
        _p = _a.getLocation()
        _op = args[0]
        if _op == 'rotated':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _angle = args[1]
            if not isinstance(_angle, float):
                raise TypeError, "Unexpected type for angle: " + `type(_angle)`
            _sdata = _a.getAngle()
            self.ignore(_op)
            try:
                if undo:
                    _a.startUndo()
                    try:
                        _a.setAngle(_angle)
                    finally:
                        _a.endUndo()
                else:
                    _a.startRedo()
                    try:
                        _a.setAngle(_angle)
                    finally:
                        _a.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'keypoint_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _parent = _a.getParent()
            if _parent is None:
                raise ValueError, "ACLine has no parent - cannot undo"
            _pt = _parent.getObject(_oid)
            if _pt is None or not isinstance(_pt, point.Point):
                raise ValueError, "Keypoint missing: id=%d" % _oid
            _sdata = _p.getID()
            self.ignore(_op)
            try:
                if undo:
                    _a.startUndo()
                    try:
                        _a.setLocation(_pt)
                    finally:
                        _a.endUndo()
                else:
                    _a.startRedo()
                    try:
                        _a.setLocation(_pt)
                    finally:
                        _a.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(ACLineLog, self).execute(undo, *args)
