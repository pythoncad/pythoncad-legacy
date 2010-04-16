#
# Copyright (c) 2003, 2004, 2005, 2006 Art Haas
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
# classes for polyline objects
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

class Polyline(graphicobject.GraphicObject):
    """A class representing a polyline. A polyline is essentially
a number of segments that connect end to end.

A Polyline has the following methods:

getPoints(): Return the points of the Polyline.
{get/set}Point(): Get/Set one of the points of the Polyline
addPoint(): Add a new point into the Polyline.
delPoint(): Remove a point from the Polyline.
move(): Move the Polyline.
length(): Get the Polyline length.
mapCoords(): Test if a coordinate pair is within some distance to a Polyline.
inRegion(): Test if the Polyline is visible in some area.
clone(): Make an identical copy of a Polyline.
    """

    __defstyle = None

    __messages = {
        'moved' : True,
        'point_changed' : True,
        'added_point' : True,
        'deleted_point' : True,
        }

    def __init__(self, plist, st=None, lt=None, col=None, th=None, **kw):
        """Initialize a Polyline object.

Polyline(plist)

The argument 'plist' is a tuple or list containing Point objects.
There should be two or more Points in the list.
        """
        if not isinstance(plist, (tuple, list)):
            raise TypeError, "Invalid Point list/tuple: " + `type(plist)`
        _pts = []
        _count = len(plist)
        if _count < 2:
            raise ValueError, "Invalid list count: %d" % _count
        for _i in range(_count):
            _obj = plist[_i]
            if not isinstance(_obj, point.Point):
                _obj = point.Point(plist[_i])
            _pts.append(_obj)
        _plist = []
        for _pt in _pts:
            try: # no exception means an equal point already found
                _i = _plist.index(_pt)
                _plist.append(_plist[_i])
            except: # no equal point found
                _plist.append(_pt)
        if len(_plist) < 2:
            raise ValueError, "Invalid point list: " + str(plist)
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        super(Polyline, self).__init__(_st, lt, col, th, **kw)
        self.__pts = _plist
        for _pt in _plist:
            _pt.connect('moved', self.__movePoint)
            _pt.connect('change_pending', self.__pointChangePending)
            _pt.connect('change_complete', self.__pointChangeComplete)
            _pt.storeUser(self)

    def __len__(self):
        return len(self.__pts)

    def __str__(self):
        return "Polyline" # fixme

    def __eq__(self, obj):
        """Compare two Polyline objects for equality.
        """
        if not isinstance(obj, Polyline):
            return False
        if obj is self:
            return True
        _val = False
        _ppts = obj.getPoints()
        _pcount = len(_ppts)
        _spts = self.__pts
        _scount = len(_spts)
        if _pcount == _scount:
            _val = True
            for _i in range(_scount):
                if _ppts[_i] != _spts[_i]:
                    _val = False
                    break
            if not _val: # check reversed point list of second polyline
                _val = True
                _ppts.reverse()
                for _i in range(_scount):
                    if _ppts[_i] != _spts[_i]:
                        _val = False
                        break
        return _val

    def __ne__(self, obj):
        """Compare two Polyline objects for inequality.
        """
        if not isinstance(obj, Polyline):
            return True
        if obj is self:
            return False
        _val = True
        _ppts = obj.getPoints()
        _pcount = len(_ppts)
        _spts = self.__pts
        _scount = len(_spts)
        if _pcount == _scount:
            _val = False
            for _i in range(_scount):
                if _ppts[_i] != _spts[_i]:
                    _val = True
                    break
            if _val: # check reversed point list of second polyline
                _val = False
                _ppts.reverse()
                for _i in range(_scount):
                    if _ppts[_i] != _spts[_i]:
                        _val = True
                        break
        return _val

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Polyline Default Style',
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
        for _pt in self.__pts:
            _pt.disconnect(self)
            _pt.freeUser(self)
        self.__pts = None
        super(Polyline, self).finish()

    def setStyle(self, s):
        """Set the Style of the Polyline.

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(Polyline, self).setStyle(_s)

    def getValues(self):
        """Return values comprising the Polyline.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(Polyline, self).getValues()
        _data.setValue('type', 'polyline')
        _pts = []
        for _pt in self.__pts:
            _pts.append(_pt.getID())
        _data.setValue('points', _pts)
        return _data

    def getPoints(self):
        """Get the points of the Polyline.

getPoints()

This function returns a list containing all the Point
objects that define the Polyline.
        """
        return self.__pts[:]

    def getNumPoints(self):
        """Return the number of Point objects defining the Polyline.

getNumPoints()
        """
        return len(self)

    def getPoint(self, i):
        """Return a single Point object used for defining the Polyline.

getPoint(i)

The argument 'i' must be an integer, and its value represents
the i'th Point used to define the Polyline.
        """
        return self.__pts[i]

    def setPoint(self, i, p):
        """Set a Point of the Polyline.

setPoint(i, p)

The argument 'i' must be an integer, and its value represents
the i'th Point used to define the Polyline. Argument 'p'
must be a Point.
        """
        if self.isLocked():
            raise RuntimeError, "Setting point not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid Point for Polyline point: " + `type(p)`
        _pt = self.__pts[i]
        if _pt is not p:
            _pt.disconnect(self)
            _pt.freeUser(self)
            self.startChange('point_changed')
            self.__pts[i] = p
            self.endChange('point_changed')
            self.sendMessage('point_changed', _pt, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_pt.x - p.x) > 1e-10 or abs(_pt.y - p.y) > 1e-10:
                _pts = []
                for _p in self.__pts:
                    if _p is p: # the new point
                        _pts.append((_pt.x, _pt.y))
                    else: # existing points
                        _pts.append((_p.x, _p.y))
                self.sendMessage('moved', _pts)
            self.modified()

    def addPoint(self, i, p):
        """Add a Point to the Polyline.

addPoint(i, p)

The argument 'i' must be an integer, and argument 'p' must be a
Point. The Point is added into the list of points comprising
the Polyline as the i'th point.
        """
        if self.isLocked():
            raise RuntimeError, "Adding point not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid Point for Polyline point: " + `type(p)`
        self.startChange('added_point')
        self.__pts.insert(i, p)
        self.endChange('added_point')
        self.sendMessage('added_point', i, p)
        p.storeUser(self)
        p.connect('moved', self.__movePoint)
        p.connect('change_pending', self.__pointChangePending)
        p.connect('change_complete', self.__pointChangeComplete)
        _pts = []
        for _p in self.__pts:
            if _p is not p: # skip the new point
                _pts.append((_p.x, _p.y))
        self.sendMessage('moved', _pts)
        self.modified()

    def delPoint(self, i):
        """Remove a Point from the Polyline.

delPoint(i)

The argument i represents the index of the point to remove from
the list of points defining the Polyline. The point will be
removed only if the polyline will still have at least two Points.
        """
        if self.isLocked():
            raise RuntimeError, "Deleting point not allowed - object locked."
        if len(self.__pts) > 2:
            _p = self.__pts[i]
            _pts = []
            for _pt in self.__pts:
                _pts.append((_pt.x, _pt.y))
            self.startChange('deleted_point')
            del self.__pts[i]
            self.endChange('deleted_point')
            _p.freeUser(self)
            _p.disconnect(self)
            self.sendMessage('deleted_point', i, _p)
            self.modified()

    def move(self, dx, dy):
        """Move a Polyline.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        _locked = self.isLocked()
        if not _locked:
            for _pt in self.__pts:
                if _pt.isLocked():
                    _locked = True
                    break
        if _locked:
            raise RuntimeError, "Moving polyline not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _coords = []
            self.ignore('moved')
            try:
                for _pt in self.__pts:
                    _coords.append(_pt.getCoords())
                    _pt.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _coords)

    def length(self):
        """Return the length of the Polyline.

length()

The length is the sum of the lengths of all the sub-segments
in the Polyline
        """
        _length = 0.0
        _pts = self.__pts
        _count = len(_pts) - 1
        for _i in range(_count):
            _sublength = _pts[_i + 1] - _pts[_i]
            _length = _length + _sublength
        return _length

    def getBounds(self):
        """Return the bounding rectangle around a Polyline.

getBounds()

This method returns a tuple of four values:

(xmin, ymin, xmax, ymax)
        """
        _pts = self.__pts
        _pxmin = None
        _pymin = None
        _pxmax = None
        _pymax = None
        for _pt in _pts:
            _px, _py = _pt.getCoords()
            if _pxmin is None or _px < _pxmin:
                _pxmin = _px
            if _pymin is None or _py < _pymin:
                _pymin = _py
            if _pxmax is None or _px > _pxmax:
                _pxmax = _px
            if _pymax is None or _py > _pymax:
                _pymax = _py
        return _pxmin, _pymin, _pxmax, _pymax

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the Polyline by the x/y coordinates.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to a
Point object on the Polyline. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this method returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _count = len(self.__pts) - 1
        for _i in range(_count):
            _x1, _y1 = self.__pts[_i].getCoords()
            _x2, _y2 = self.__pts[_i + 1].getCoords()
            _pt = util.map_coords(_x, _y, _x1, _y1, _x2, _y2, _t)
            if _pt is not None:
                return _pt
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not a Polyline exists within a region.

isRegion(xmin, ymin, xmax, ymax[, fully])

The four arguments define the boundary of an area, and the
method returns True if the Polyline lies within that area. If
the optional argument 'fully' is used and is True, then both
endpoints of the Polyline must lie within the boundary.
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
        _pxmin, _pymin, _pxmax, _pymax = self.getBounds()
        if ((_pxmax < _xmin) or
            (_pxmin > _xmax) or
            (_pymax < _ymin) or
            (_pymin > _ymax)):
            return False
        if fully:
            if ((_pxmin > _xmin) and
                (_pymin > _ymin) and
                (_pxmax < _xmax) and
                (_pymax < _ymax)):
                return True
            return False
        _pts = self.__pts
        for _i in range(len(_pts) - 1):
            _x1, _y1 = _pts[_i].getCoords()
            _x2, _y2 = _pts[_i + 1].getCoords()
            if util.in_region(_x1, _y1, _x2, _y2, _xmin, _ymin, _xmax, _ymax):
                return True
        return False

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
        _seen = False
        _coords = []
        for _pt in self.__pts:
            if p is _pt:
                _coords.append((_x, _y))
                _seen = True
            else:
                _coords.append(_pt.getCoords())
        if not _seen:
            raise ValueError, "Unexpected Polyline point: " + `p`
        self.sendMessage('moved', _coords)

    def clone(self):
        """Create an identical copy of a Polyline.

clone()
        """
        _cpts = []
        for _pt in self.__pts:
            _cpts.append(_pt.clone())
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Polyline(_cpts, _st, _lt, _col, _th)

    def sendsMessage(self, m):
        if m in Polyline.__messages:
            return True
        return super(Polyline, self).sendsMessage(m)

#
# Quadtree Polyline storage
#

class PolylineQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(PolylineQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 4:
            raise ValueError, "Expected 4 arguments, got %d" % _alen
        _pxmin = util.get_float(args[0])
        _pymin = util.get_float(args[1])
        _pxmax = util.get_float(args[2])
        if not _pxmax > _pxmin:
            raise ValueError, "xmax not greater than xmin"
        _pymax = util.get_float(args[3])        
        if not _pymax > _pymin:
            raise ValueError, "ymax not greater than ymin"
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_pxmin > _xmax) or
                (_pxmax < _xmin) or
                (_pymin > _ymax) or
                (_pymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _pxmax < _xmid: # polyline on left side
                    _ne = _se = False
                if _pxmin > _xmid: # polyline on right side
                    _nw = _sw = False
                if _pymax < _ymid: # polyline below
                    _nw = _ne = False
                if _pymin > _ymid: # polyline above
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
        if not isinstance(obj, Polyline):
            raise TypeError, "Invalid Polyline object: " + `type(obj)`
        if obj in self:
            return
        _pxmin, _pymin, _pxmax, _pymax = obj.getBounds()
        _bounds = self.getTreeRoot().getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _pxmin - 1.0
            _ymin = _pymin - 1.0
            _xmax = _pxmax + 1.0
            _ymax = _pymax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _pxmin < _xmin:
                _xmin = _pxmin - 1.0
                _resize = True
            if _pxmax > _xmax:
                _xmax = _pxmax + 1.0
                _resize = True
            if _pymin < _ymin:
                _ymin = _pymin - 1.0
                _resize = True
            if _pymax > _ymax:
                _ymax = _pymax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_pxmin, _pymin, _pxmax, _pymax):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(PolylineQuadtree, self).addObject(obj)
        obj.connect('moved', self._movePolyline)

    def delObject(self, obj):
        if obj not in self:
            return
        _pxmin, _pymin, _pxmax, _pymax = obj.getBounds()
        _pdict = {}
        for _node in self.getNodes(_pxmin, _pymin, _pxmax, _pymax):
            _node.delObject(obj) # polyline may not be in the node ...
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(PolylineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if not isinstance(args[0], list):
            raise TypeError, "Invalid coordinate list: " + `type(args[0])`
        _coords = []
        _xmin = _xmax = _ymin = _ymax = None
        for _arg in args[0]:
            if not isinstance(_arg, tuple):
                raise TypeError, "Invalid coordinate tuple: " + `type(_arg)`
            if len(_arg) != 2:
                raise ValueError, "Invalid coodinate tuple: " + str(_arg)
            _x = util.get_float(_arg[0])
            _y = util.get_float(_arg[1])
            _coords.append((_x, _y))
            if _xmin is None or _x < _xmin:
                _xmin = _x
            if _xmax is None or _x > _xmax:
                _xmax= _x
            if _ymin is None or _y < _ymin:
                _ymin = _y
            if _ymax is None or _y > _ymax:
                _ymax = _y
        _t = tolerance.TOL
        if _alen > 1:
            _t = tolerance.toltest(args[1])
        _xmin = _xmin - _t
        _ymin = _ymin - _t
        _xmax = _xmax + _t
        _ymax = _ymax + _t
        _plines = []
        for _pline in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pts = _pline.getPoints()
            if len(_pts) != len(_coords):
                continue
            _hit = False
            for _i in range(len(_pts)):
                _px, _py = _pts[_i].getCoords()
                if ((abs(_px - _coords[_i][0]) > _t) or
                    (abs(_py - _coords[_i][1]) > _t)):
                    continue
                _hit = True
            if not _hit:
                _pts.reverse()
                for _i in range(len(_pts)):
                    _px, _py = _pts[_i].getCoords()
                    if ((abs(_px - _coords[_i][0]) > _t) or
                        (abs(_py - _coords[_i][1]) > _t)):
                        continue
                    _hit = True
            if _hit:
                _plines.append(_pline)
        return _plines

    def _movePolyline(self, obj, *args):
        if obj not in self:
            raise ValueError, "Polyline not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if not isinstance(args[0], list):
            raise TypeError, "Invalid coordinate list: " + `type(args[0])`
        _pxmin = _pxmax = _pymin = _pymax = None
        for _arg in args[0]:
            if not isinstance(_arg, tuple):
                raise TypeError, "Invalid coordinate tuple: " + `type(_arg)`
            if len(_arg) != 2:
                raise ValueError, "Invalid coodinate tuple: " + str(_arg)
            _x = util.get_float(_arg[0])
            _y = util.get_float(_arg[1])
            if _pxmin is None or _x < _pxmin:
                _pxmin = _x
            if _pxmax is None or _x > _pxmax:
                _pxmax= _x
            if _pymin is None or _y < _pymin:
                _pymin = _y
            if _pymax is None or _y > _pymax:
                _pymax = _y
        for _node in self.getNodes(_pxmin, _pymin, _pxmax, _pymax):
            _node.delObject(obj) # polyline may not be in node ...
        super(PolylineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _polyline = _tsep = None
        _bailout = False
        _pdict = {}
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
                for _p in _node.getObjects():
                    _pid = id(_p)
                    if _pid not in _pdict:
                        for _pt in _p.getPoints():
                            _px, _py = _pt.getCoords()
                            if ((abs(_px - _x) < 1e-10) and
                                (abs(_py - _y) < 1e-10)):
                                _polyline = _p
                                _bailout = True
                                break
                        _pdict[_pid] = True
                    if _bailout:
                        break
                    _pt = _p.mapCoords(_x, _y, _t)
                    if _pt is not None:
                        _px, _py = _pt
                        _sep = math.hypot((_px - _x), (_py - _y))
                        if _tsep is None:
                            _tsep = _sep
                            _polyline = _p
                        else:
                            if _sep < _tsep:
                                _tsep = _sep
                                _polyline = _p
            if _bailout:
                break
        return _polyline

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _polylines = []
        if not len(self):
            return _polylines
        _nodes = [self.getTreeRoot()]
        _pdict = {}
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
                for _p in _node.getObjects():
                    _pid = id(_p)
                    if _pid not in _pdict:
                        if _p.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _polylines.append(_p)
                        _pdict[_pid] = True
        return _polylines

#
# Polyline history class
#

class PolylineLog(graphicobject.GraphicObjectLog):
    def __init__(self, p):
        if not isinstance(p, Polyline):
            raise TypeError, "Invalid polyline: " + `type(p)`
        super(PolylineLog, self).__init__(p)
        p.connect('point_changed', self.__pointChanged)
        p.connect('added_point', self.__addedPoint)
        p.connect('deleted_point', self.__deletedPoint)


    def __pointChanged(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old endpoint: " + `type(_old)`
        _new = args[1]
        if not isinstance(_new, point.Point):
            raise TypeError, "Invalid new endpoint: " + `type(_new)`
        self.saveUndoData('point_changed', _old.getID(), _new.getID())

    def __addedPoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _idx = args[0]
        if not isinstance(_idx, int):
            raise TypeError, "Invalid point index: " + `type(_idx)`
        _p = args[1]
        if not isinstance(_p, point.Point):
            raise TypeError, "Invalid point: " + `type(_p)`
        self.saveUndoData('added_point', _idx, _p.getID())

    def __deletedPoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _idx = args[0]
        if not isinstance(_idx, int):
            raise TypeError, "Invalid point index: " + `type(_idx)`
        _p = args[1]
        if not isinstance(_p, point.Point):
            raise TypeError, "Invalid point: " + `type(_p)`
        self.saveUndoData('deleted_point', _idx, _p.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _p = self.getObject()
        _op = args[0]
        _pts = _p.getPoints()
        if _op == 'point_changed':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _nid = args[2]
            _parent = _p.getParent()
            if _parent is None:
                raise ValueError, "Polyline has no parent - cannot undo"
            self.ignore(_op)
            try:
                if undo:
                    _setpt = _parent.getObject(_oid)
                    if _setpt is None or not isinstance(_setpt, point.Point):
                        raise ValueError, "Old endpoint missing: id=%d" % _oid
                    _p.startUndo()
                    try:
                        _seen = False
                        for _i in range(len(_pts)):
                            _pt = _pts[_i]
                            if _pt.getID() == _nid:
                                _p.setPoint(_i, _setpt)
                                _seen = True
                                break
                        if not _seen:
                            raise ValueError, "Unexpected point ID: %d" % _nid
                    finally:
                        _p.endUndo()
                else:
                    _setpt = _parent.getObject(_nid)
                    if _setpt is None or not isinstance(_setpt, point.Point):
                        raise ValueError, "New point missing: id=%d" % _nid
                    _pts = _p.getPoints()
                    _p.startRedo()
                    try:
                        _seen = False
                        for _i in range(len(_pts)):
                            _pt = _pts[_i]
                            if _pt.getID() == _oid:
                                _p.setPoint(_i, _setpt)
                                _seen = True
                                break
                        if not _seen:
                            raise ValueError, "Unexpected point ID: %d" % _nid
                    finally:
                        _p.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _oid, _nid)
        elif _op == 'added_point':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _idx = args[1]
            _pid = args[2]
            self.ignore(_op)
            try:
                if undo:
                    self.ignore('deleted_point')
                    try:
                        _p.startUndo()
                        try:
                            _p.delPoint(_idx)
                        finally:
                            _p.endUndo()
                    finally:
                        self.receive('deleted_point')
                else:
                    _parent = _p.getParent()
                    if _parent is None:
                        raise ValueError, "Polyline has no parent - cannot undo"
                    _pt = _parent.getObject(_pid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "Point missing: id=%d" % _pid
                    _p.startRedo()
                    try:
                        _p.addPoint(_idx, _pt)
                    finally:
                        _p.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _idx, _pid)
        elif _op == 'deleted_point':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _idx = args[1]
            _pid = args[2]
            self.ignore(_op)
            try:
                if undo:
                    _parent = _p.getParent()
                    if _parent is None:
                        raise ValueError, "Polyline has no parent - cannot undo"
                    _pt = _parent.getObject(_pid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "Point missing: id=%d" % _pid
                    self.ignore('added_point')
                    try:
                        _p.startUndo()
                        try:
                            _p.addPoint(_idx, _pt)
                        finally:
                            _p.endUndo()
                    finally:
                        self.receive('added_point')
                else:
                    _p.startRedo()
                    try:
                        _p.delPoint(_idx)
                    finally:
                        _p.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _idx, _pid)
        else:
            super(PolylineLog, self).execute(undo, *args)
