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
#
# a construction line defined by two points
#

from __future__ import generators

import math

from PythonCAD.Generic import conobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import point
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import util

class CLine(conobject.ConstructionObject):
    """A class for construction lines defined by two distinct Points.

A CLine object is derived from the conobject class, so it shares
the functionality of that class. In addition, a CLine instance
has two attributes:

p1: A Point object representing the first keypoint
p2: A Point object representing the second keypoint

A CLine has the following methods:

getKeypoints(): Return the two points the CLine is defined by.
{get/set}P1: Get/Set the first keypoint of the CLine.
{get/set}P2: Get/Set the second keypoint of the CLine.
move(): Move a CLine
mapCoords(): Return the nearest point on a CLine to a coordinate pair.
inRegion(): Return whether the CLine passes through a bounded region.
clone(): Return an identical copy of a CLine.
    """
    __messages = {
        'moved' : True,
        'keypoint_changed' : True
        }
        
    def __init__(self, p1, p2, **kw):
        """Initialize a CLine object.

CLine(p1, p2)

Both arguments are Point objects that the CLine passes through.
        """
        _p1 = p1
        if not isinstance(_p1, point.Point):
            _p1 = point.Point(p1)
        _p2 = p2
        if not isinstance(_p2, point.Point):
            _p2 = point.Point(p2)
        if _p1 is _p2:
            raise ValueError, "A CLine must have two different keypoints."
        super(CLine, self).__init__(**kw)
        self.__p1 = _p1
        _p1.storeUser(self)
        _p1.connect('moved', self.__movePoint)
        _p1.connect('change_pending', self.__pointChangePending)
        _p1.connect('change_complete', self.__pointChangeComplete)
        self.__p2 = _p2
        _p2.storeUser(self)
        _p2.connect('moved', self.__movePoint)
        _p2.connect('change_pending', self.__pointChangePending)
        _p2.connect('change_complete', self.__pointChangeComplete)

    def __eq__(self, obj):
        """Compare one CLine to another for equality.
        """
        if not isinstance(obj, CLine):
            return False
        if obj is self:
            return True
        _sp1, _sp2 = self.getKeypoints()
        _op1, _op2 = obj.getKeypoints()
        _sv = abs(_sp1.x - _sp2.x) < 1e-10
        _sh = abs(_sp1.y - _sp2.y) < 1e-10
        _ov = abs(_op1.x - _op2.x) < 1e-10
        _oh = abs(_op1.y - _op2.y) < 1e-10
        _val = False
        if _sv and _ov: # both vertical
            if abs(_sp1.x - _op1.x) < 1e-10:
                _val = True
        elif _sh and _oh: # both horizontal
            if abs(_sp1.y - _op1.y) < 1e-10:
                _val = True
        else:
            if (not (_sv or _sh)) and (not (_ov or _oh)):
                _sx1, _sy1 = _sp1.getCoords()
                _sx2, _sy2 = _sp2.getCoords()
                _ox1, _oy1 = _op1.getCoords()
                _ox2, _oy2 = _op2.getCoords()
                _ms = (_sy2 - _sy1)/(_sx2 - _sx1)
                _bs = _sy1 - (_ms * _sx1)
                _ty = (_ms * _ox1) + _bs
                if abs(_ty - _oy1) < 1e-10:
                    _ty = (_ms * _ox2) + _bs
                    if abs(_ty - _oy2) < 1e-10:
                        _val = True
        return _val

    def __ne__(self, obj):
        """Compare one CLine to another for inequality.
        """
        if not isinstance(obj, CLine):
            return True
        if obj is self:
            return False
        _sp1, _sp2 = self.getKeypoints()
        _op1, _op2 = obj.getKeypoints()
        _sv = abs(_sp1.x - _sp2.x) < 1e-10
        _sh = abs(_sp1.y - _sp2.y) < 1e-10
        _ov = abs(_op1.x - _op2.x) < 1e-10
        _oh = abs(_op1.y - _op2.y) < 1e-10
        _val = True
        if _sv and _ov: # both vertical
            if abs(_sp1.x - _op1.x) < 1e-10:
                _val = False
        elif _sh and _oh: # both horizontal
            if abs(_sp1.y - _op1.y) < 1e-10:
                _val = False
        else:
            if (not (_sv or _sh)) and (not (_ov or _oh)):
                _sx1, _sy1 = _sp1.getCoords()
                _sx2, _sy2 = _sp2.getCoords()
                _ox1, _oy1 = _op1.getCoords()
                _ox2, _oy2 = _op2.getCoords()
                _ms = (_sy2 - _sy1)/(_sx2 - _sx1)
                _bs = _sy1 - (_ms * _sx1)
                _ty = (_ms * _ox1) + _bs
                if abs(_ty - _oy1) < 1e-10:
                    _ty = (_ms * _ox2) + _bs
                    if abs(_ty - _oy2) < 1e-10:
                        _val = False
        return _val

    def __str__(self):
        return "Construction Line through %s and %s" % (self.__p1, self.__p2)

    def finish(self):
        self.__p1.disconnect(self)
        self.__p1.freeUser(self)
        self.__p2.disconnect(self)
        self.__p2.freeUser(self)
        self.__p1 = self.__p2 = None
        super(CLine, self).finish()

    def getValues(self):
        _data = super(CLine, self).getValues()
        _data.setValue('type', 'cline')
        _data.setValue('p1', self.__p1.getID())
        _data.setValue('p2', self.__p2.getID())
        return _data

    def getKeypoints(self):
        """Return the two keypoints of this CLine.

getKeypoints()
        """
        return self.__p1, self.__p2

    def getP1(self):
        """Return the first keypoint Point of the CLine.

getP1()
        """
        return self.__p1

    def setP1(self, p):
        """Set the first keypoint Point of the CLine.

setP1(p)

Argument 'p' must be a Point.
        """
        if self.isLocked():
            raise RuntimeError, "Setting keypoint not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        if p is self.__p2 or p == self.__p2:
            raise ValueError, "CLines must have two different keypoints."
        _kp = self.__p1
        if _kp is not p:
            _kp.disconnect(self)
            _kp.freeUser(self)
            self.startChange('keypoint_changed')
            self.__p1 = p
            self.endChange('keypoint_changed')
            self.sendMessage('keypoint_changed', _kp, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_kp.x - p.x) > 1e-10 or abs(_kp.y - p.y) > 1e-10:
                _x, _y = self.__p2.getCoords()
                self.sendMessage('moved', _kp.x, _kp.y, _x, _y)
            self.modified()

    p1 = property(getP1, setP1, None, "First keypoint of the CLine.")

    def getP2(self):
        """Return the second keypoint Point of the CLine.

getP2()
        """
        return self.__p2

    def setP2(self, p):
        """Set the second keypoint Point of the CLine.

setP2(p)

Argument 'p' must be a Point.
        """
        if self.isLocked():
            raise RuntimeError, "Setting keypoint not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        if p is self.__p1 or p == self.__p1:
            raise ValueError, "CLines must have two different keypoints."
        _kp = self.__p2
        if _kp is not p:
            _kp.disconnect(self)
            _kp.freeUser(self)
            self.startChange('keypoint_changed')
            self.__p2 = p
            self.endChange('keypoint_changed')
            self.sendMessage('keypoint_changed', _kp, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_kp.x - p.x) > 1e-10 or abs(_kp.y - p.y) > 1e-10:
                _x, _y = self.__p1.getCoords()
                self.sendMessage('moved', _x, _y, _kp.x, _kp.y)
            self.modified()

    p2 = property(getP2, setP2, None, "Second keypoint of the CLine.")

    def move(self, dx, dy):
        """Move a CLine.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked() or self.__p1.isLocked() or self.__p2.isLocked():
            raise RuntimeError, "Moving CLine not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x1, _y1 = self.__p1.getCoords()
            _x2, _y2 = self.__p2.getCoords()
            self.ignore('moved')
            try:
                self.__p1.move(_dx, _dy)
                self.__p2.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _x1, _y1, _x2, _y2)

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the CLine to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to a
actual Point on the CLine. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _sqlen = pow((_x2 - _x1), 2) + pow((_y2 - _y1), 2)
        if _sqlen < 1e-10: # both points the same
            raise RuntimeError, "CLine points coincident."
        _r = ((_x - _x1)*(_x2 - _x1) + (_y - _y1)*(_y2 - _y1))/_sqlen
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        if abs(_px - _x) < _t and abs(_py - _y) < _t:
           return _px, _py
        return None

    def getProjection(self, x, y):
        """Find the projection point of some coordinates on the CLine.

getProjection(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _sqlen = pow((_x2 - _x1), 2) + pow((_y2 - _y1), 2)
        _rn = ((_x - _x1) * (_x2 - _x1)) + ((_y - _y1) * (_y2 - _y1))
        _r = _rn/_sqlen
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        return _px, _py

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not a CLine passes through a region.

isRegion(xmin, ymin, xmax, ymax)

The four arguments define the boundary of an area, and the
function returns True if the CLine passes within the area.
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
        if fully:
            return False
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _xdiff = _x2 - _x1
        _ydiff = _y2 - _y1
        _val = False
        if _xmin < _x1 < _xmax and _ymin < _y1 < _ymax:
            _val = True
        elif _xmin < _x2 < _xmax and _ymin < _y2 < _ymax:
            _val = True
        elif abs(_xdiff) < 1e-10: # vertical line
            if _xmin < _x1 < _xmax:
                _val = True
        elif abs(_ydiff) < 1e-10: # horizontal line
            if _ymin < _y1 < _ymax:
                _val = True
        else:
            _slope = _ydiff/_xdiff
            _yint = _y1 - _slope*_x1
            if _ymin < (_slope*_xmin + _yint) < _ymax: # hits left side
                _val = True
            elif _ymin < (_slope*_xmax + _yint) < _ymax: # hits right side
                _val = True
            else: # hits bottom - no need to check top ...
                _xymin = (_ymin - _yint)/_slope
                if _xmin < _xymin < _xmax:
                    _val = True
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
        _plen = len(args)
        if _plen < 2:
            raise ValueError, "Invalid argument count: %d" % _plen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _p1 = self.__p1
        _p2 = self.__p2
        if p is _p1:
            _x1 = _x
            _y1 = _y
            _x2, _y2 = _p2.getCoords()
            if abs(_p1.x - _x2) < 1e-10 and abs(_p1.y - _y2) < 1e-10:
                raise RuntimeError, "CLine points coincident."
        elif p is _p2:
            _x1, y1 = _p1.getCoords()
            _x2 = _x
            _y2 = _y
            if abs(_p2.x - _x1) < 1e-10 and abs(_p2.y - _y1) < 1e-10:
                raise RuntimeError, "CLine points coincident."
        else:
            raise ValueError, "Unexpected CLine keypoint: " + `p`
        self.sendMessage('moved', _x1, _y1, _x2, _y2)

    def clone(self):
        """Create an identical copy of a CLine.

clone()
        """
        _cp1 = self.__p1.clone()
        _cp2 = self.__p2.clone()
        return CLine(_cp1, _cp2)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _p1, _p2 = self.getKeypoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _coords = None
        if abs(_x2 - _x1) < 1e-10: # vertical
            if _xmin < _x1 < _xmax:
                _coords = (_x1, _ymin, _x1, _ymax)
        elif abs(_y2 - _y1) < 1e-10: # horiztonal
            if _ymin < _y1 < _ymax:
                _coords = (_xmin, _y1, _xmax, _y1)
        else:
            #
            # the CLine can be parameterized as
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
            _dx = _x2 - _x1
            _dy = _y2 - _y1
            # print "dx: %g; dy: %g" % (_dx, _dy)
            _P = [-_dx, _dx, -_dy, _dy]
            _q = [(_x1 - _xmin), (_xmax - _x1), (_y1 - _ymin), (_ymax - _y1)]
            _u1 = None
            _u2 = None
            _valid = True
            for _i in range(4):
                # print "i: %d" % _i
                _pi = _P[_i]
                _qi = _q[_i]
                # print "p[i]: %g; q[i]: %g" % (_pi, _qi)
                if abs(_pi) < 1e-10: # this should be caught earlier ...
                    if _qi < 0.0:
                        _valid = False
                        break
                else:
                    _r = _qi/_pi
                    # print "r: %g" % _r
                    if _pi < 0.0:
                        # print "testing u1 ..."
                        if _u2 is not None and _r > _u2:
                            # print "r > u2 (%g)" % _u2
                            _valid = False
                            break
                        if _u1 is None or _r > _u1:
                            # print "setting u1 = r"
                            _u1 = _r
                    else:
                        # print "testing u2 ..."
                        if _u1 is not None and _r < _u1:
                            # print "r < u1 (%g)" % _u1
                            _valid = False
                            break
                        if _u2 is None or _r < _u2:
                            # print "setting u2 = r"
                            _u2 = _r
            if _valid:
                _coords = (((_u1 * _dx) + _x1),
                           ((_u1 * _dy) + _y1),
                           ((_u2 * _dx) + _x1),
                           ((_u2 * _dy) + _y1))
        return _coords

    def sendsMessage(self, m):
        if m in CLine.__messages:
            return True
        return super(CLine, self).sendsMessage(m)
    
    def getMiddlePoint(self):
        _x = (self.__p1.getx() + self.__p2.getx()) / 2
        _y = (self.__p1.gety() + self.__p2.gety()) / 2
        _point = point.Point(_x, _y)
        return _point
        
def intersect_region(cl, xmin, ymin, xmax, ymax):
    if not isinstance(cl, CLine):
        raise TypeError, "Invalid CLine: " + `type(cl)`
    _xmin = util.get_float(xmin)
    _ymin = util.get_float(ymin)
    _xmax = util.get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = util.get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _p1, _p2 = cl.getKeypoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if abs(_p2x - _p1x) < 1e-10: # vertical
        if _xmin < _p1x < _xmax:
            _x1 = _p1x
            _y1 = _ymin
            _x2 = _p1x
            _y2 = _ymax
    elif abs(_p2y - _p1y) < 1e-10: # horiztonal
        if _ymin < _p1y < _ymax:
            _x1 = _xmin
            _y1 = _p1y
            _x2 = _xmax
            _y2 = _p1y
    else:
        _slope = (_p2y - _p1y)/(_p2x - _p1x)
        _yint = _p1y - (_p1x * _slope)
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
# Quadtree CLine storage
#

class CLineQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(CLineQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 4:
            raise ValueError, "Expected 4 arguments, got %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        _h = abs(_y2 - _y1) < 1e-10
        _v = abs(_x2 - _x1) < 1e-10
        if _h and _v: # both coords are identical
            raise ValueError, "CLine singularity - identical coords."
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = False
                if _v:
                    if _x1 < _xmin or _x1 > _xmax:
                        continue
                    if _x1 < _xmid: # cline on left
                        _sw = _nw = True
                    else:
                        _se = _ne = True
                elif _h:
                    if _y1 < _ymin or _y1 > _ymax:
                        continue
                    if _y1 < _ymid: # cline below
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
        if not isinstance(obj, CLine):
            raise TypeError, "Invalid CLine: " + `type(obj)`
        if obj in self:
            return
        _p1, _p2 = obj.getKeypoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _bounds = self.getTreeRoot().getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _sxmin = min(_x1, _x2)
        _sxmax = max(_x1, _x2)
        _symin = min(_y1, _y2)
        _symax = max(_y1, _y2)
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _sxmin - 1.0
            _ymin = _symin - 1.0
            _xmax = _sxmax + 1.0
            _ymax = _symax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _sxmin < _xmin:
                _xmin = _sxmin - 1.0
                _resize = True
            if _sxmax > _xmax:
                _xmax = _sxmax + 1.0
                _resize = True
            if _symin < _ymin:
                _ymin = _symin - 1.0
                _resize = True
            if _symax > _ymax:
                _ymax = _symax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_x1, _y1, _x2, _y2):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(CLineQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveCLine)

    def delObject(self, obj):
        if obj not in self:
            return
        _p1, _p2 = obj.getKeypoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _pdict = {}
        for _node in self.getNodes(_x1, _y1, _x2, _y2):
            _node.delObject(obj) # cline may not be in the node ...
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(CLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        _t = tolerance.TOL
        if _alen > 4:
            _t = tolerance.toltest(args[4])
        _xmin = min(_x1, _x2) - _t
        _ymin = min(_y1, _y2) - _t
        _xmax = max(_x1, _x2) + _t
        _ymax = max(_y1, _y2) + _t
        _clines = []
        for _cline in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _p1, _p2 = _cline.getKeypoints()
            if ((abs(_p1.x - _x1) < _t) and
                (abs(_p1.y - _y1) < _t) and
                (abs(_p2.x - _x2) < _t) and
                (abs(_p2.y - _y2) < _t)):
                _clines.append(_cline)
            elif ((abs(_p1.x - _x2) < _t) and
                (abs(_p1.y - _y2) < _t) and
                (abs(_p2.x - _x1) < _t) and
                (abs(_p2.y - _y1) < _t)):
                _clines.append(_cline)
            else:
                pass
        return _clines

    def _moveCLine(self, obj, *args):
        if obj not in self:
            raise ValueError, "CLine not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        for _node in self.getNodes(_x1, _y1, _x2, _y2):
            _node.delObject(obj) # cline may not be in node ...
        super(CLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _cline = _tsep = None
        _cdict = {}
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _c in _node.getObjects():
                    _cid = id(_c)
                    if _cid not in _cdict:
                        _cx, _cy = _c.getProjection(_x, _y)
                        if abs(_cx - _x) < _t and abs(_cy - _y) < _t:
                            _sep = math.hypot((_cx - _x), (_cy - _y))
                            if _tsep is None:
                                _tsep = _sep
                                _cline = _c
                            else:
                                if _sep < _tsep:
                                    _tsep = _sep
                                    _cline = _c
        return _cline

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _clines = []
        if not len(self):
            return _clines
        _nodes = [self.getTreeRoot()]
        _cdict = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                for _subnode in _node.getSubnodes():
                    _nodes.append(_subnode)
            else:
                for _cline in _node.getObjects():
                    _cid = id(_cline)
                    if _cid not in _cdict:
                        if _cline.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _clines.append(_cline)
                        _cdict[_cid] = True
        return _clines

#
# CLine history class
#

class CLineLog(conobject.ConstructionObjectLog):
    def __init__(self, c):
        if not isinstance(c, CLine):
            raise TypeError, "Invalid CLine: " + `type(c)`
        super(CLineLog, self).__init__(c)
        c.connect('keypoint_changed', self._keypointChange)

    def _keypointChange(self, c, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old keypoint: " + `type(_old)`
        _new = args[1]
        if not isinstance(_new, point.Point):
            raise TypeError, "Invalid new keypoint: " + `type(_new)`
        self.saveUndoData('keypoint_changed', _old.getID(), _new.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _c = self.getObject()
        _p1, _p2 = _c.getKeypoints()
        _op = args[0]
        if _op == 'keypoint_changed':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _nid = args[2]
            _parent = _c.getParent()
            if _parent is None:
                raise ValueError, "CLine has no parent - cannot undo"
            self.ignore(_op)
            try:
                if undo:
                    _pt = _parent.getObject(_oid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "Old keypoint missing: id=%d" % _oid
                    _c.startUndo()
                    try:
                        if _p1.getID() == _nid:
                            _c.setP1(_pt)
                        elif _p2.getID() == _nid:
                            _c.setP2(_pt)
                        else:
                            raise ValueError, "Unexpected keypoint ID: %d" % _nid
                    finally:
                        _c.endUndo()
                else:
                    _pt = _parent.getObject(_nid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "New keypoint missing: id=%d" % _nid
                    _c.startRedo()
                    try:
                        if _p1.getID() == _oid:
                            _c.setP1(_pt)
                        elif _p2.getID() == _oid:
                            _c.setP2(_pt)
                        else:
                            raise ValueError, "Unexpected keypoint ID: %d" % _oid
                    finally:
                        _c.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _oid, _nid)
        else:
            super(CLineLog, self).execute(undo, *args)
