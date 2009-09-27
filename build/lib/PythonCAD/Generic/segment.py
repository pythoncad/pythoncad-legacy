#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas 2009 Matteo Boscolo
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
# classes for line segments
#

from __future__ import generators

import math

from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import point
from PythonCAD.Generic import util
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import pyGeoLib
  
class Segment(graphicobject.GraphicObject):
    """A class representing a line segment.

A Segment has two attributes.

p1: A Point object representing the first end point
p2: A Point object representing the second end point

A Segment has the following methods:

getEndpoints(): Return the two endpoints of the Segment.
{get/set}P1: Get/Set the Segment first endpoint.
{get/set}P2: Get/Set the Segment second endpoint.
move(): Move the Segment.
length(): Get the Segment length.
getCoefficients(): Return the segment as ax + by + c = 0
getProjection(): Project a coordinate on to the Segment
mapCoords(): Test if a coordinate pair is within some distance to a Segment.
inRegion(): Test if the Segment is visible in some area.
++Matteo Boscolo
getMiddlePoint(): return the x,y cord of the segment MiddlePoint
--
clone(): Make an identical copy of a Segment.
    """
    __messages = {
        'moved' : True,
        'endpoint_changed' : True
        }

    __defstyle = None

    def __init__(self, p1, p2, st=None, lt=None, col=None, th=None, **kw):
        """Initialize a Segment object.

Segment(p1, p2[, st, lt, col, th])

p1: Segment first endpoint - may be a Point or a two-item tuple of floats.
p2: Segment second endpoint - may be a Point or a two-item tuple of floats.

The following arguments are optional:

st: A Style object
lt: A Linetype object that overrides the linetype in the Style.
col: A Color object that overrides the color in the Style.
th: A float that overrides the line thickness in the Style.
        """

        _p1 = p1
        if not isinstance(_p1, point.Point):
            _p1 = point.Point(p1)
        _p2 = p2
        if not isinstance(_p2, point.Point):
            _p2 = point.Point(p2)
        if _p1 is _p2:
            raise ValueError, "Segments cannot have identical endpoints."
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        super(Segment, self).__init__(_st, lt, col, th, **kw)
        self.__p1 = _p1
        _p1.connect('moved', self.__movePoint)
        _p1.connect('change_pending', self.__pointChangePending)
        _p1.connect('change_complete', self.__pointChangeComplete)
        _p1.storeUser(self)
        self.__p2 = _p2
        _p2.connect('moved', self.__movePoint)
        _p2.connect('change_pending', self.__pointChangePending)
        _p2.connect('change_complete', self.__pointChangeComplete)
        _p2.storeUser(self)

    def __str__(self):
        return "Segment: %s to %s" % (self.__p1, self.__p2)

    def __eq__(self, obj):
        """Compare a Segment to another for equality.
        """
        if not isinstance(obj, Segment):
            return False
        if obj is self:
            return True
        _sp1 = self.__p1
        _sp2 = self.__p2
        _op1, _op2 = obj.getEndpoints()
        return (((_sp1 == _op1) and (_sp2 == _op2)) or
                ((_sp1 == _op2) and (_sp2 == _op1)))

    def __ne__(self, obj):
        """Compare a Segment to another for inequality.
        """
        if not isinstance(obj, Segment):
            return True
        if obj is self:
            return False
        _sp1 = self.__p1
        _sp2 = self.__p2
        _op1, _op2 = obj.getEndpoints()
        return (((_sp1 != _op1) or (_sp2 != _op2)) and
                ((_sp1 != _op2) or (_sp2 != _op1)))

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Default Segment Style',
                             linetype.Linetype(u'Solid', None),
                             color.Color(0xffffff),
                             1.0)
            cls.__defstyle = _s
        return cls.__defstyle

    getDefaultStyle = classmethod(getDefaultStyle)

    def setDefaultStyle(cls, s):
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid style: " + `type(s)`
        cls.__defstyle = s

    setDefaultStyle = classmethod(setDefaultStyle)

    def finish(self):
        self.__p1.disconnect(self)
        self.__p1.freeUser(self)
        self.__p2.disconnect(self)
        self.__p2.freeUser(self)
        self.__p1 = self.__p2 = None
        super(Segment, self).finish()

    def setStyle(self, s):
        """Set the Style of the Segment

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(Segment, self).setStyle(_s)

    def getValues(self):
        """Return values comprising the Segment.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(Segment, self).getValues()
        _data.setValue('type', 'segment')
        _data.setValue('p1', self.__p1.getID())
        _data.setValue('p2', self.__p2.getID())
        return _data

    def getEndpoints(self):
        """Get the endpoints of the Segment.

getEndpoints()

This function returns a tuple containing the two Point objects
that are the endpoints of the segment.
        """
        return self.__p1, self.__p2

    def getP1(self):
        """Return the first endpoint Point of the Segment.

getP1()
        """
        return self.__p1

    def setP1(self, p):
        """Set the first endpoint Point of the Segment.

setP1(p)
        """
        if self.isLocked():
            raise RuntimeError, "Setting endpoint not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid P1 endpoint type: " + `type(p)`
        if p is self.__p2:
            raise ValueError, "Segments cannot have identical endpoints."
        _pt = self.__p1
        if _pt is not p:
            _pt.disconnect(self)
            _pt.freeUser(self)
            self.startChange('endpoint_changed')
            self.__p1 = p
            self.endChange('endpoint_changed')
            self.sendMessage('endpoint_changed', _pt, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_pt.x - p.x) > 1e-10 or abs(_pt.y - p.y) > 1e-10:
                _x, _y = self.__p2.getCoords()
                self.sendMessage('moved', _pt.x, _pt.y, _x, _y)
            self.modified()

    p1 = property(getP1, setP1, None, "First endpoint of the Segment.")

    def getP2(self):
        """Return the second endpoint Point of the Segment.

getP2()
        """
        return self.__p2

    def setP2(self, p):
        """Set the second endpoint Point of the Segment.

setP2(p)
        """
        if self.isLocked():
            raise RuntimeError, "Setting endpoint not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid P2 endpoint type: " + `type(p)`
        if p is self.__p1:
            raise ValueError, "Segments cannot have identical endpoints."
        _pt = self.__p2
        if _pt is not p:
            _pt.disconnect(self)
            _pt.freeUser(self)
            self.startChange('endpoint_changed')
            self.__p2 = p
            self.endChange('endpoint_changed')
            self.sendMessage('endpoint_changed', _pt, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_pt.x - p.x) > 1e-10 or abs(_pt.y - p.y) > 1e-10:
                _x, _y = self.__p1.getCoords()
                self.sendMessage('moved', _x, _y, _pt.x, _pt.y)
            self.modified()

    p2 = property(getP2, setP2, None, "Second endpoint of the Segment.")

    def move(self, dx, dy):
        """Move a Segment.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked() or self.__p1.isLocked() or self.__p2.isLocked():
            raise RuntimeError, "Moving Segment not allowed - object locked."
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

    def length(self):
        """Return the length of the Segment.

length()
        """
        return self.__p1 - self.__p2

    def getCoefficients(self):
        """Express the line segment as a function ax + by + c = 0

getCoefficients()

This method returns a tuple of three floats: (a, b, c)
        """
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _a = _y2 - _y1
        _b = _x1 - _x2
        _c = (_x2 * _y1) - (_x1 * _y2)
        return _a, _b, _c
#++ Matteo Boscolo
    def getMiddlePoint(self):
        """Return the middle point of the segment
"""
        _p1,_p2=self.getEndpoints()
        _x1=util.get_float(_p1.x)
        _x2=util.get_float(_p2.x)
        _y1=util.get_float(_p1.y)
        _y2=util.get_float(_p2.y)
        _deltax=abs(_x1-_x2)/2.0
        _deltay=abs(_y1-_y2)/2.0
        if(_x1<_x2):
            retX=_x1+_deltax
        else:
            retX=_x2+_deltax
        if(_y1<_y2):
            retY=_y1+_deltay
        else:
            retY=_y2+_deltay
        return retX,retY
#--
    def getProjection(self, x, y):
        """Find the projection point of some coordinates on the Segment.

getProjection(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _sqlen = pow((_x2 - _x1), 2) +  pow((_y2 - _y1), 2)
        if _sqlen < 1e-10: # coincident points
            return None
        _rn = ((_x - _x1) * (_x2 - _x1)) + ((_y - _y1) * (_y2 - _y1))
        _r = _rn/_sqlen
        if _r < 0.0 or _r > 1.0:
            return None
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        return _px, _py
    
    def GetLineProjection(self,x,y):
        """
            get Projection of the point x,y in the line 
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()        
        p1=point.Point(_x1, _y1)
        p2=point.Point(_x2, _y2)
        p3=point.Point(_x, _y)
        v=pyGeoLib.Vector(p1,p2)
        v1=pyGeoLib.Vector(p1,p3)
        xp,yp=v1.Point().getCoords()
        pjPoint=v.Map(xp,yp).Point()
        #print("point",str(_x),str(_y))
        #print("segment" ,str(_x1),str( _y1),str(_x2),str( _y2))
        x,y =pjPoint.getCoords()
        x=x+_x1
        y=y+_y1
        #print("prjPoint",str(x),str(y))
        return x,y
        
    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the Segment to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.

This function is used to map a possibly near-by coordinate pair to an
actual Point on the Segment. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        return util.map_coords(_x, _y, _x1, _y1, _x2, _y2, _t)

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not a Segment exists within a region.

inRegion(xmin, ymin, xmax, ymax[, fully])

The four arguments define the boundary of an area, and the
method returns True if the Segment lies within that area. If
the optional argument fully is used and is True, then both
endpoints of the Segment must lie within the boundary.
Otherwise, the method returns False.
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
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _pxmin = min(_x1, _x2)
        _pymin = min(_y1, _y2)
        _pxmax = max(_x1, _x2)
        _pymax = max(_y1, _y2)
        if ((_pxmax < _xmin) or
            (_pymax < _ymin) or
            (_pxmin > _xmax) or
            (_pymin > _ymax)):
            return False
        if fully:
            if ((_pxmin > _xmin) and
                (_pymin > _ymin) and
                (_pxmax < _xmax) and
                (_pymax < _ymax)):
                return True
            return False
        return util.in_region(_x1, _y1, _x2, _y2, _xmin, _ymin, _xmax, _ymax)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        """Clip the Segment using the Liang-Barsky Algorithm.

clipToRegion(xmin, ymin, xmax, ymax)
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        #
        # simple tests to reject line
        #
        if ((max(_x1, _x2) < _xmin) or
            (max(_y1, _y2) < _ymin) or
            (min(_x1, _x2) > _xmax) or
            (min(_y1, _y2) > _ymax)):
            return None
        #
        # simple tests to accept line
        #
        _coords = None
        if (_xmin < _x1 < _xmax and
            _xmin < _x2 < _xmax and
            _ymin < _y1 < _ymax and
            _ymin < _y2 < _ymax):
            _coords = (_x1, _y1, _x2, _y2)
        else:
            #
            # the Segment can be parameterized as
            #
            # x = u * (x2 - x1) + x1
            # y = u * (y2 - y1) + y1
            #
            # for u = 0, x => x1, y => y1
            # for u = 1, x => x2, y => y2
            #
            # The following is the Liang-Barsky Algorithm
            # for segment clipping
            #
            _dx = _x2 - _x1
            _dy = _y2 - _y1
            _P = [-_dx, _dx, -_dy, _dy]
            _q = [(_x1 - _xmin), (_xmax - _x1), (_y1 - _ymin), (_ymax - _y1)]
            _u1 = 0.0
            _u2 = 1.0
            _valid = True
            for _i in range(4):
                _pi = _P[_i]
                _qi = _q[_i]
                if abs(_pi) < 1e-10:
                    if _qi < 0.0:
                        _valid = False
                        break
                else:
                    _r = _qi/_pi
                    if _pi < 0.0:
                        if _r > _u2:
                            _valid = False
                            break
                        if _r > _u1:
                            _u1 = _r
                    else:
                        if _r < _u1:
                            _valid = False
                            break
                        if _r < _u2:
                            _u2 = _r
            if _valid:
                _coords = (((_u1 * _dx) + _x1),
                           ((_u1 * _dy) + _y1),
                           ((_u2 * _dx) + _x1),
                           ((_u2 * _dy) + _y1))
        return _coords

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
        if p is self.__p1:
            _x1 = _x
            _y1 = _y
            _x2, _y2 = self.__p2.getCoords()
        elif p is self.__p2:
            _x1, _y1 = self.__p1.getCoords()
            _x2 = _x
            _y2 = _y
        else:
            raise ValueError, "Unexpected Segment endpoint: " + `p`
        self.sendMessage('moved', _x1, _y1, _x2, _y2)

    def clone(self):
        """Create an identical copy of a Segment.

clone()
        """
        _cp1 = self.__p1.clone()
        _cp2 = self.__p2.clone()
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Segment(_cp1, _cp2, _st, _lt, _col, _th)

    def sendsMessage(self, m):
        if m in Segment.__messages:
            return True
        return super(Segment, self).sendsMessage(m)

#
# Quadtree Segment storage
#

class SegmentQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(SegmentQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 4:
            raise ValueError, "Expected 4 arguments, got %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        _sxmin = min(_x1, _x2)
        _sxmax = max(_x1, _x2)
        _symin = min(_y1, _y2)
        _symax = max(_y1, _y2)
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_sxmin > _xmax) or
                (_sxmax < _xmin) or
                (_symin > _ymax) or
                (_symax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _sxmax < _xmid: # seg on left side
                    _ne = _se = False
                if _sxmin > _xmid: # seg on right side
                    _nw = _sw = False
                if _symax < _ymid: # seg below
                    _nw = _ne = False
                if _symin > _ymid: # seg above
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
        if not isinstance(obj, Segment):
            raise TypeError, "Invalid Segment object: " + `obj`
        if obj in self:
            return
        _p1, _p2 = obj.getEndpoints()
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
        super(SegmentQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveSegment)

    def delObject(self, obj):
        if obj not in self:
            return
        _p1, _p2 = obj.getEndpoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _pdict = {}
        for _node in self.getNodes(_x1, _y1, _x2, _y2):
            _node.delObject(obj)
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(SegmentQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)
        #
        # test
        #
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _obj in _node.getObjects():
                    if _obj is obj:
                        raise ValueError, "object still in tree" + `obj`

    def find(self, *args):
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = args[0]
        if not isinstance(_x1, float):
            _x1 = float(args[0])
        _y1 = args[1]
        if not isinstance(_y1, float):
            _y1 = float(args[1])
        _x2 = args[2]
        if not isinstance(_x2, float):
            _x2 = float(args[2])
        _y2 = args[3]
        if not isinstance(_y2, float):
            _y2 = float(args[3])
        _t = tolerance.TOL
        if _alen > 4:
            _t = tolerance.toltest(args[4])
        _xmin = min(_x1, _x2) - _t
        _ymin = min(_y1, _y2) - _t
        _xmax = max(_x1, _x2) + _t
        _ymax = max(_y1, _y2) + _t
        _segs = []
        for _seg in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _p1, _p2 = _seg.getEndpoints()
            if ((abs(_x1 - _p1.x) < _t) and
                (abs(_y1 - _p1.y) < _t) and
                (abs(_x2 - _p2.x) < _t) and
                (abs(_y2 - _p2.y) < _t)):
                _segs.append(_seg)
            elif ((abs(_x2 - _p1.x) < _t) and
                (abs(_y2 - _p1.y) < _t) and
                (abs(_x1 - _p2.x) < _t) and
                (abs(_y1 - _p2.y) < _t)):
                _segs.append(_seg)
            else:
                pass
        return _segs

    def _moveSegment(self, obj, *args):
        if obj not in self:
            raise ValueError, "Segment not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        for _node in self.getNodes(_x1, _y1, _x2, _y2):
            _node.delObject(obj) # segment may not be in node ...
        super(SegmentQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _seg = _tsep = None
        _bailout = False
        _sdict = {}
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
                for _s in _node.getObjects():
                    _sid = id(_s)
                    if _sid not in _sdict:
                        _p1, _p2 = _s.getEndpoints()
                        _px, _py = _p1.getCoords()
                        if ((abs(_px - _x) < 1e-10) and
                            (abs(_py - _y) < 1e-10)):
                            _seg = _s
                            _bailout = True
                            break
                        _px, _py = _p2.getCoords()
                        if ((abs(_px - _x) < 1e-10) and
                            (abs(_py - _y) < 1e-10)):
                            _seg = _s
                            _bailout = True
                            break
                        _sdict[_sid] = True
                    _pt = _s.mapCoords(_x, _y, _t)
                    if _pt is not None:
                        _px, _py = _pt
                        _sep = math.hypot((_px - _x), (_py - _y))
                        if _tsep is None:
                            _tsep = _sep
                            _seg = _s
                        else:
                            if _sep < _tsep:
                                _tsep = _sep
                                _seg = _s
            if _bailout:
                break
        return _seg

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _segs = []
        if not len(self):
            return _segs
        _nodes = [self.getTreeRoot()]
        _sdict = {}
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
                for _seg in _node.getObjects():
                    _sid = id(_seg)
                    if _sid not in _sdict:
                        if _seg.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _segs.append(_seg)
                        _sdict[_sid] = True
        return _segs

#
# Segment history class
#

class SegmentLog(graphicobject.GraphicObjectLog):
    def __init__(self, s):
        if not isinstance(s, Segment):
            raise TypeError, "Invalid segment: " + `s`
        super(SegmentLog, self).__init__(s)
        s.connect('endpoint_changed', self.__endpointChanged)

    def __endpointChanged(self, s, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old endpoint: " + `_old`
        _new = args[1]
        if not isinstance(_new, point.Point):
            raise TypeError, "Invalid new endpoint: " + `_new`
        self.saveUndoData('endpoint_changed', _old.getID(), _new.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _s = self.getObject()
        _p1, _p2 = _s.getEndpoints()
        _op = args[0]
        if _op == 'endpoint_changed':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _nid = args[2]
            _parent = _s.getParent()
            if _parent is None:
                raise ValueError, "Segment has no parent - cannot undo"
            self.ignore(_op)
            try:
                if undo:
                    _pt = _parent.getObject(_oid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "Old endpoint missing: id=%d" % _oid
                    _s.startUndo()
                    try:
                        if _p1.getID() == _nid:
                            _s.setP1(_pt)
                        elif _p2.getID() == _nid:
                            _s.setP2(_pt)
                        else:
                            raise ValueError, "Unexpected endpoint ID: %d" % _nid
                    finally:
                        _s.endUndo()
                else:
                    _pt = _parent.getObject(_nid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "New endpoint missing: id=%d" % _nid
                    _s.startRedo()
                    try:
                        if _p1.getID() == _oid:
                            _s.setP1(_pt)
                        elif _p2.getID() == _oid:
                            _s.setP2(_pt)
                        else:
                            raise ValueError, "Unexpected endpoint ID: %d" % _oid
                    finally:
                        _s.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _oid, _nid)
        else:
            super(SegmentLog, self).execute(undo, *args)
