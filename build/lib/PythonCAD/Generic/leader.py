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
# classes for leader lines
#

from __future__ import generators

import math
import array

from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import point
from PythonCAD.Generic import util
from PythonCAD.Generic import quadtree

class Leader(graphicobject.GraphicObject):
    """A class representing a leader line.

A leader line is usually used as a visual connector between
some text and an entity in a drawing. Leader lines cannot be
used to define an edge of some shape.

A Leader object has the following attributes:
p1: A Point object representing the first end point.
p2: A Point object representing the leader mid point.
p3: A Point object representing the final end point.
arrowsize: The size of the arrow at the end of the leader line

A Leader object has the following methods:

getPoints(): Return the points defining the Leader
{get/set}P1(): Get/Set the Leader first endpoint.
{get/set}P2(): Get/Set the Leader midpoint
{get/set}P3(): Get/Set the Leader final endpoint
{get/set}ArrowSize(): Get/Set the Leader line arrow size.
calcArrowPoints(): Calculate where the Leader arrow points are.
getArrowPoints(): Return where the Leader arrow points are.
move(): Move the Leader.
mapCoords(): See if a point lies within some distance of a Leader.
inRegion(): Test if the Leader is visible in some area.
clone(): Make an identical copy of a Leader.
    """
    __defstyle = None

    __messages = {
        'moved' : True,
        'point_changed' : True,
        'size_changed' : True,
        }

    def __init__(self, p1, p2, p3, size=1.0,
                 st=None, lt=None, col=None, th=None, **kw):
        """Initialize a Leader object.

Leader(p1, p2, p3[, size, st, lt, col, th])

The following arguments are required:

p1: Leader first endpoint - may be a Point or a two-item tuple of floats
p2: Leader mid point - may be a Point or a two-item tuple of floats
p3: Leader final endpoint - may be a Point or a two-item tuple of floats

Argument size is optional. It gives the size of the arrow at
the end of the leader line, and defaults to 1.0.
        """
        _p1 = p1
        if not isinstance(_p1, point.Point):
            _p1 = point.Point(p1)
        _p2 = p2
        if not isinstance(_p2, point.Point):
            _p2 = point.Point(p2)
        if _p1 is _p2:
            raise ValueError, "Leader points p1 and p2 cannot be identical."
        _p3 = p3
        if not isinstance(_p3, point.Point):
            _p3 = point.Point(_p3)
        if _p1 is _p3:
            raise ValueError, "Leader points p1 and p3 cannot be identical."
        if _p2 is _p3:
            raise ValueError, "Leader points p2 and p3 cannot be identical"
        _size = util.get_float(size)
        if _size < 0.0:
            raise ValueError, "Invalid arrow size: %g" % _size
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        super(Leader, self).__init__(_st, lt, col, th, **kw)
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
        self.__p3 = _p3
        _p3.connect('moved', self.__movePoint)
        _p3.connect('change_pending', self.__pointChangePending)
        _p3.connect('change_complete', self.__pointChangeComplete)
        _p3.storeUser(self)
        self.__size = _size
        self.__arrow_pts = array.array('d', [0.0, 0.0, 0.0, 0.0])
        self.calcArrowPoints()

    def __str__(self):
        return "Leader: %s to %s to %s" % (self.__p1, self.__p2, self.__p3)

    def __eq__(self, obj):
        """Compare two leader lines for equality.
        """
        if not isinstance(obj, Leader):
            return False
        if obj is self:
            return True
        _sp1 = self.__p1
        _sp2 = self.__p2
        _sp3 = self.__p3
        _p1, _p2, _p3 = obj.getPoints()
        if (_sp1 == _p1 and _sp2 == _p2 and _sp3 == _p3):
            return True
        return False

    def __ne__(self, obj):
        """Compare two leader lines for inequality.
        """
        if not isinstance(obj, Leader):
            return True
        if obj is self:
            return False
        _sp1 = self.__p1
        _sp2 = self.__p2
        _sp3 = self.__p3
        _p1, _p2, _p3 = obj.getPoints()
        if (_sp1 == _p1 and _sp2 == _p2 and _sp3 == _p3):
            return False
        return True

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Leader Default Style',
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
        self.__p3.disconnect(self)
        self.__p3.freeUser(self)
        self.__p1 = self.__p2 = self.__p3 = self.__size = None
        super(Leader, self).finish()

    def setStyle(self, s):
        """Set the Style of the Leader.

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(Leader, self).setStyle(_s)

    def getValues(self):
        """Return values comprising the Arc.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(Leader, self).getValues()
        _data.setValue('type', 'leader')
        _data.setValue('p1', self.__p1.getID())
        _data.setValue('p2', self.__p2.getID())
        _data.setValue('p3', self.__p3.getID())
        _data.setValue('size', self.__size)
        return _data

    def getPoints(self):
        """Get the points defining the Leader.

getPoints()

This function returns a tuple containing the three Point objects
that are the defining points of the Leader
        """
        return self.__p1, self.__p2, self.__p3

    def getP1(self):
        """Return the first endpoint Point of the Leader

getP1()
        """
        return self.__p1

    def setP1(self, p):
        """Set the first endpoint Point of the Leader

setP1(p)

The argument 'p' should be a Point.
        """
        if self.isLocked():
            raise RuntimeError, "Setting points not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid P1 point: " + `type(p)`
        if p is self.__p2 or p is self.__p3:
            raise ValueError, "Leader points cannot be identical."
        _pt = self.__p1
        if _pt is not p:
            _pt.disconnect(self)
            _pt.freeUser(self)
            self.startChange('point_changed')
            self.__p1 = p
            self.endChange('point_changed')
            self.sendMessage('point_changed', _pt, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_pt.x - p.x) > 1e-10 or abs(_pt.y - p.y) > 1e-10:
                _x2, _y2 = self.__p2.getCoords()
                _x3, _y3 = self.__p3.getCoords()
                self.sendMessage('moved', _pt.x, _pt.y, _x2, _y2, _x3, _y3)
            self.modified()

    p1 = property(getP1, setP1, None, "First endpoint of the Leader.")

    def getP2(self):
        """Return the midpoint Point of the Leader.

getP2()
        """
        return self.__p2

    def setP2(self, p):
        """Set the midpoint Point of the Leader.

setP2(p)

The argument 'p' should be a Point.
        """
        if self.isLocked():
            raise RuntimeError, "Setting points not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid P2 point: " + `type(p)`
        if p is self.__p1 or p is self.__p3:
            raise ValueError, "Leader points cannot be identical."
        _pt = self.__p2
        if _pt is not p:
            _pt.disconnect(self)
            _pt.freeUser(self)
            self.startChange('point_changed')
            self.__p2 = p
            self.endChange('point_changed')
            self.sendMessage('point_changed', _pt, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_pt.x - p.x) > 1e-10 or abs(_pt.y - p.y) > 1e-10:
                self.calcArrowPoints()
                _x1, _y1 = self.__p1.getCoords()
                _x3, _y3 = self.__p3.getCoords()
                self.sendMessage('moved', _x1, _y1, _pt.x, _pt.y, _x3, _y3)
            self.modified()

    p2 = property(getP2, setP2, None, "Leader midpoint.")

    def getP3(self):
        """Return the final Point of the Leader.

getP3()
        """
        return self.__p3

    def setP3(self, p):
        """Set the final endpoint Point of the Leader.

setP3(p)

The argument 'p' should be a Point.
        """
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid Point for p3 endpoint: " + `p`
        if self.isLocked():
            raise RuntimeError, "Setting points not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid P3 point: " + `type(p)`
        if p is self.__p1 or p is self.__p2:
            raise ValueError, "Leader points cannot be identical."
        _pt = self.__p3
        if _pt is not p:
            _pt.disconnect(self)
            _pt.freeUser(self)
            self.startChange('point_changed')
            self.__p3 = p
            self.endChange('point_changed')
            self.sendMessage('point_changed', _pt, p)
            p.storeUser(self)
            p.connect('moved', self.__movePoint)
            p.connect('change_pending', self.__pointChangePending)
            p.connect('change_complete', self.__pointChangeComplete)
            if abs(_pt.x - p.x) > 1e-10 or abs(_pt.y - p.y) > 1e-10:
                self.calcArrowPoints()
                _x1, _y1 = self.__p1.getCoords()
                _x2, _y2 = self.__p2.getCoords()
                self.sendMessage('moved', _x1, _y1, _x2, _y2, _pt.x, _pt.y)
            self.modified()

    p3 = property(getP3, setP3, None, "Third endpoint of the Leader.")

    def getArrowSize(self):
        """Return the size of the leader line arrow.

getArrowSize()
        """
        return self.__size

    def setArrowSize(self, size):
        """Set the size of the leader line arrow.

setSize(size)

Argument 'size' should be a float greater than or equal to 0.0.
        """
        if self.isLocked():
            raise RuntimeError, "Cannot change arrow size - object locked."
        _size = util.get_float(size)
        if _size < 0.0:
            raise ValueError, "Invalid arrow size: %g" % _size
        _os = self.__size
        if abs(_os - _size) > 1e-10:
            self.startChange('size_changed')
            self.__size = _size
            self.endChange('size_changed')
            self.calcArrowPoints()
            self.sendMessage('size_changed', _os)
            self.modified()

    arrowsize = property(getArrowSize, setArrowSize,
                    None, "Leader line arrow size.")

    def calcArrowPoints(self):
        """Calculate where the Leader arrow points are.

calcArrowPoints()
        """
        _x1, _y1 = self.__p2.getCoords()
        _x2, _y2 = self.__p3.getCoords()
        if abs(_x2 - _x1) < 1e-10: # vertical
            _cosine = 0.0
            if _y2 > _y1:
                _sine = 1.0
            else:
                _sine = -1.0

        elif abs(_y2 - _y1) < 1e-10: # horizontal
            _sine = 0.0
            if _x2 > _x1:
                _cosine = 1.0
            else:
                _cosine = -1.0
        else:
            _angle = math.atan2((_y2 - _y1), (_x2 - _x1))
            _sine = math.sin(_angle)
            _cosine = math.cos(_angle)
        _size = self.__size
        _height = _size/5.0
        # p1 -> (x,y) = (-size, _height)
        self.__arrow_pts[0] = (_cosine * (-_size) - _sine * _height) + _x2
        self.__arrow_pts[1] = (_sine * (-_size) + _cosine * _height) + _y2
        # p2 -> (x,y) = (-size, -_height)
        self.__arrow_pts[2] = (_cosine * (-_size) - _sine *(-_height)) + _x2
        self.__arrow_pts[3] = (_sine * (-_size) + _cosine *(-_height)) + _y2

    def getArrowPoints(self):
        """Return the endpoints of the Leader arrow.

getArrowPoints()

This method returns an array holding four float values.
        """
        return self.__arrow_pts

    def move(self, dx, dy):
        """Move a Leader.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if (self.isLocked() or
            self.__p1.isLocked() or
            self.__p2.isLocked() or
            self.__p3.isLocked()):
            raise RuntimeError, "Moving Leader not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x1, _y1 = self.__p1.getCoords()
            _x2, _y2 = self.__p2.getCoords()
            _x3, _y3 = self.__p3.getCoords()
            self.ignore('moved')
            try:
                self.__p1.move(_dx, _dy)
                self.__p2.move(_dx, _dy)
                self.__p3.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.calcArrowPoints()
            self.sendMessage('moved', _x1, _y1, _x2, _y2, _x3, _y3)

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the Leader to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the Leader. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _x3, _y3 = self.__p3.getCoords()
        _pt = util.map_coords(_x, _y, _x1, _y1, _x2, _y2, _t)
        if _pt is None:
            _pt = util.map_coords(_x, _y, _x2, _y2, _x3, _y3, _t)
        if _pt is not None:
            return _pt
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not a Leader exists within a region.

isRegion(xmin, ymin, xmax, ymax[, fully])

The four arguments define the boundary of an area, and the
method returns True if the Leader lies within that area. If
the optional argument fully is used and is True, then all
the Leader points must lie within the boundary. Otherwise,
the method returns False.
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
        _x3, _y3 = self.__p3.getCoords()
        _pxmin = min(_x1, _x2, _x3)
        _pymin = min(_y1, _y2, _y3)
        _pxmax = max(_x1, _x2, _x3)
        _pymax = max(_y1, _y2, _y3)
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
        if util.in_region(_x1, _y1, _x2, _y2, _xmin, _ymin, _xmax, _ymax):
            return True
        return util.in_region(_x2, _y2, _x3, _y3, _xmin, _ymin, _xmax, _ymax)

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
            if p is self.__p2 or p is self.__p3:
                self.calcArrowPoints()
            self.endChange('moved')

    def __movePoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _p1 = self.__p1
        _p2 = self.__p2
        _p3 = self.__p3
        if p is _p1:
            _x1 = _x
            _y1 = _y
            _x2, _y2 = _p2.getCoords()
            _x3, _y3 = _p3.getCoords()
        elif p is _p2:
            _x1, _y1 = _p1.getCoords()
            _x2 = _x
            _y2 = _y
            _x3, _y3 = _p3.getCoords()
        elif p is _p3:
            _x1, _y1 = _p1.getCoords()
            _x2, _y2 = _p2.getCoords()
            _x3 = _x
            _y3 = _y
        else:
            raise ValueError, "Unexpected Leader endpoint: " + `p`
        self.sendMessage('moved', _x1, _y1, _x2, _y2, _x3, _y3)

    def clone(self):
        """Create an identical copy of a Leader.

clone()
        """
        _cp1 = self.__p1.clone()
        _cp2 = self.__p2.clone()
        _cp3 = self.__p3.clone()
        _size = self.__size
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Leader(_cp1, _cp2, _cp3, _size, _st, _lt, _col, _th)

    def sendsMessage(self, m):
        if m in Leader.__messages:
            return True
        return super(Leader, self).sendsMessage(m)

#
# Quadtree Leader storage
#

class LeaderQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(LeaderQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 4:
            raise ValueError, "Expected 4 arguments, got %d" % _alen
        _lxmin = util.get_float(args[0])
        _lymin = util.get_float(args[1])
        _lxmax = util.get_float(args[2])
        if not _lxmax > _lxmin:
            raise ValueError, "xmax not greater than xmin"
        _lymax = util.get_float(args[3])        
        if not _lymax > _lymin:
            raise ValueError, "ymax not greater than ymin"
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_lxmin > _xmax) or
                (_lxmax < _xmin) or
                (_lymin > _ymax) or
                (_lymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _lxmax < _xmid: # leader on left side
                    _ne = _se = False
                if _lxmin > _xmid: # leader on right side
                    _nw = _sw = False
                if _lymax < _ymid: # leader below
                    _nw = _ne = False
                if _lymin > _ymid: # leader above
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
        if not isinstance(obj, Leader):
            raise TypeError, "Invalid Leader object: " + `obj`
        if obj in self:
            return
        _p1, _p2, _p3 = obj.getPoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _x3, _y3 = _p3.getCoords()
        _bounds = self.getTreeRoot().getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _lxmin = min(_x1, _x2, _x3)
        _lxmax = max(_x1, _x2, _x3)
        _lymin = min(_y1, _y2, _y3)
        _lymax = max(_y1, _y2, _y3)
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _lxmin - 1.0
            _ymin = _lymin - 1.0
            _xmax = _lxmax + 1.0
            _ymax = _lymax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _lxmin < _xmin:
                _xmin = _lxmin - 1.0
                _resize = True
            if _lxmax > _xmax:
                _xmax = _lxmax + 1.0
                _resize = True
            if _lymin < _ymin:
                _ymin = _lymin - 1.0
                _resize = True
            if _lymax > _ymax:
                _ymax = _lymax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_lxmin, _lymin, _lxmax, _lymax):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(LeaderQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveLeader)

    def delObject(self, obj):
        if obj not in self:
            return
        _p1, _p2, _p3 = obj.getPoints()
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _x3, _y3 = _p3.getCoords()
        _lxmin = min(_x1, _x2, _x3)
        _lxmax = max(_x1, _x2, _x3)
        _lymin = min(_y1, _y2, _y3)
        _lymax = max(_y1, _y2, _y3)
        _pdict = {}
        for _node in self.getNodes(_lxmin, _lymin, _lxmax, _lymax):
            _node.delObject(obj) # leader may not be in the node ...
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(LeaderQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 6:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        _x3 = util.get_float(args[4])
        _y3 = util.get_float(args[5])
        _t = tolerance.TOL
        if _alen > 6:
            _t = tolerance.toltest(args[6])
        _xmin = min(_x1, _x2, _x3) - _t
        _xmax = max(_x1, _x2, _x3) + _t
        _ymin = min(_y1, _y2, _y3) - _t
        _ymax = max(_y1, _y2, _y3) + _t
        _leaders = []
        for _leader in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _p1, _p2, _p3 = _leader.getPoints()
            if ((abs(_p1.x - _x1) < _t) and
                (abs(_p1.y - _y1) < _t) and
                (abs(_p2.x - _x2) < _t) and
                (abs(_p2.y - _y2) < _t) and
                (abs(_p3.x - _x3) < _t) and
                (abs(_p3.y - _y3) < _t)):
                _leaders.append(_leader)
        return _leaders

    def _moveLeader(self, obj, *args):
        if obj not in self:
            raise ValueError, "Leader not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 6:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        _x3 = util.get_float(args[4])
        _y3 = util.get_float(args[5])
        _lxmin = min(_x1, _x2, _x3)
        _lxmax = max(_x1, _x2, _x3)
        _lymin = min(_y1, _y2, _y3)
        _lymax = max(_y1, _y2, _y3)
        for _node in self.getNodes(_lxmin, _lymin, _lxmax, _lymax):
            _node.delObject(obj) # leader may not be in node ...
        super(LeaderQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _leader = _tsep = None
        _bailout = False
        _ldict = {}
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
                for _l in _node.getObjects():
                    _lid = id(_l)
                    _p1, _p2, _p3 = _l.getPoints()
                    if _lid not in _ldict:
                        _px, _py = _p1.getCoords()
                        if ((abs(_px - _x) < 1e-10) and
                            (abs(_py - _y) < 1e-10)):
                            _leader = _l
                            _bailout = True
                            break
                        _px, _py = _p2.getCoords()
                        if ((abs(_px - _x) < 1e-10) and
                            (abs(_py - _y) < 1e-10)):
                            _leader = _l
                            _bailout = True
                            break
                        _px, _py = _p3.getCoords()
                        if ((abs(_px - _x) < 1e-10) and
                            (abs(_py - _y) < 1e-10)):
                            _leader = _l
                            _bailout = True
                            break
                        _ldict[_lid] = True
                    _pt = _l.mapCoords(_x, _y, _t)
                    if _pt is not None:
                        _px, _py = _pt
                        _sep = math.hypot((_px - _x), (_py - _y))
                        if _tsep is None:
                            _tsep = _sep
                            _leader = _l
                        else:
                            if _sep < _tsep:
                                _tsep = _sep
                                _leader = _l
            if _bailout:
                break
        return _leader

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _leaders = []
        if not len(self):
            return _leaders
        _nodes = [self.getTreeRoot()]
        _ldict = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                for _subnode in _node.getSubnodes():
                    _lxmin, _lymin, _lxmax, _lymax = _subnode.getBoundary()
                    if ((_lxmin > _xmax) or
                        (_lymin > _ymax) or
                        (_lxmax < _xmin) or
                        (_lymax < _ymin)):
                        continue
                    _nodes.append(_subnode)
            else:
                for _l in _node.getObjects():
                    _lid = id(_l)
                    if _lid not in _ldict:
                        if _l.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _leaders.append(_l)
                        _ldict[_lid] = True
        return _leaders

#
# Leader history class
#

class LeaderLog(graphicobject.GraphicObjectLog):
    def __init__(self, l):
        if not isinstance(l, Leader):
            raise TypeError, "Invalid leader: " + `l`
        super(LeaderLog, self).__init__(l)
        l.connect('point_changed', self.__pointChanged)
        l.connect('size_changed', self.__sizeChanged)

    def __pointChanged(self, l, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old endpoint: " + `_old`
        _new = args[1]
        if not isinstance(_new, point.Point):
            raise TypeError, "Invalid new endpoint: " + `_new`
        self.saveUndoData('point_changed', _old.getID(), _new.getID())

    def __sizeChanged(self, l, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _size = args[0]
        if not isinstance(_size, float):
            raise TypeError, "Unexpected type for size: " + `type(_size)`
        self.saveUndoData('size_changed', _size)

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _l = self.getObject()
        _op = args[0]
        if _op == 'point_changed':
            if _alen < 3:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _nid = args[2]
            _p1, _p2, _p3 = _l.getPoints()
            _parent = _l.getParent()
            if _parent is None:
                raise ValueError, "Leader has no parent - cannot undo"
            self.ignore(_op)
            try:
                if undo:
                    _pt = _parent.getObject(_oid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "Old point missing: id=%d" % _oid
                    _l.startUndo()
                    try:
                        if _p1.getID() == _nid:
                            _l.setP1(_pt)
                        elif _p2.getID() == _nid:
                            _l.setP2(_pt)
                        elif _p3.getID() == _nid:
                            _l.setP3(_pt)
                        else:
                            raise ValueError, "Unexpected point ID: %d" % _nid
                    finally:
                        _l.endUndo()
                else:
                    _pt = _parent.getObject(_nid)
                    if _pt is None or not isinstance(_pt, point.Point):
                        raise ValueError, "New point missing: id=%d" % _nid
                    _l.startRedo()
                    try:
                        if _p1.getID() == _oid:
                            _l.setP1(_pt)
                        elif _p2.getID() == _oid:
                            _l.setP2(_pt)
                        elif _p3.getID() == _oid:
                            _l.setP3(_pt)
                        else:
                            raise ValueError, "Unexpected point ID: %d" % _oid
                    finally:
                        _l.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _oid, _nid)
        elif _op == 'size_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _size = args[1]
            if not isinstance(_size, float):
                raise TypeError, "Unexpected type for size: " + `type(_size)`
            _sdata = _l.getArrowSize()
            self.ignore(_op)
            try:
                if undo:
                    _l.startUndo()
                    try:
                        _l.setArrowSize(_size)
                    finally:
                        _l.endUndo()
                else:
                    _l.startRedo()
                    try:
                        _l.setArrowSize(_size)
                    finally:
                        _l.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(LeaderLog, self).execute(undo, *args)
