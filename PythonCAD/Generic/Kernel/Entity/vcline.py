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
# vertical construction lines
#

from __future__ import generators

import math

from acline             import ACLine
from tolerance          import *
from util               import *
from point              import Point

class VCLine(ACLine):
    """
        A base class for horizontal construction lines.
    """
    def __init__(self, p):
        """
            Instantiate an VCLine object.
        """
        super(ACLine, self).__init__(p, math.pi/2)
        self.__keypoint = _p
    # Todo: finish the conversion from here

    def __eq__(self, obj):
        """Compare one VCLine to another for equality.
        """
        if not isinstance(obj, VCLine):
            return False
        if obj is self:
            return True
        if abs(self.getLocation().x - obj.getLocation().x) < 1e-10:
            return True
        return False

    def __ne__(self, obj):
        """Compare one VCLine to another for inequality.
        """
        if not isinstance(obj, VCLine):
            return True
        if obj is self:
            return False
        if abs(self.getLocation().x - obj.getLocation().x) < 1e-10:
            return False
        return True

    def __str__(self):
        _x, _y = self.getLocation().getCoords()
        return "Vertical Construction Line at x = %g" % self.__keypoint.x

    def finish(self):
        self.__keypoint.disconnect(self)
        self.__keypoint.freeUser(self)
        self.__keypoint = None
        super(VCLine, self).finish()

    def getValues(self):
        _data = super(VCLine, self).getValues()
        _data.setValue('type', 'vcline')
        _data.setValue('keypoint', self.__keypoint.getID())
        return _data

    def getLocation(self):
        return self.__keypoint

    def setLocation(self, p):
        if self.isLocked():
            raise RuntimeError, "Setting keypoint not allowed - object locked."
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        _kp = self.__keypoint
        if p is not _kp:
            _x = _kp.x
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
            if abs(_x - p.x) > 1e-10:
                self.sendMessage('moved', _x, p.y)
            self.sendMessage('modified')

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the VCLine to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required argument:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the VCLine. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _vx = self.__keypoint.x
        if abs(_vx - x) < _t:
            return _vx, _y
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not an VCLine passes through a region.

inRegion(xmin, ymin, xmax, ymax)

The first four arguments define the boundary. The method
will return True if the VCLine falls between xmin and xmax.
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
        _x = self.__keypoint.x
        return not (_x < _xmin or _x > _xmax)

    def move(self, dx, dy):
        """Move a VCLine

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked() or self.__keypoint.isLocked():
            raise RuntimeError, "Moving VCLine not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x, _y = self.__keypoint.getCoords()
            self.ignore('moved')
            try:
                self.__keypoint.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _x, _y)

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
            raise ValueError, "Invalid point for VCLine::movePoint()" + `p`
        if abs(p.x - _x) > 1e-10:
            self.sendMessage('moved', _x, _y)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _x = self.__keypoint.x
        if _xmin < _x < _xmax:
            return _x, _ymin, _x, _ymax
        return None

    def clone(self):
        """Create an identical copy of an VCLine.

clone()
        """
        return VCLine(self.__keypoint.clone())

    def sendsMessage(self, m):
        if m in VCLine.__messages:
            return True
        return super(VCLine, self).sendsMessage(m)
    def getProjection(self,x,y):
        """
            Get the projection of the point in to the line
        """
        VCLinePoint=self.getLocation()
        x1,y1=VCLinePoint.getCoords()
        y1=y
        return x1,y1
    
def intersect_region(vcl, xmin, ymin, xmax, ymax):
    if not isinstance(vcl, VCLine):
        raise TypeError, "Invalid VCLine: " + `type(vcl)`
    _xmin = util.get_float(xmin)
    _ymin = util.get_float(ymin)
    _xmax = util.get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = util.get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _x, _y = vcl.getLocation().getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if _xmin < _x < _xmax:
        _x1 = _x
        _y1 = _ymin
        _x2 = _x
        _y2 = _ymax
    return _x1, _y1, _x2, _y2

#
# Quadtree VCLine storage
#

class VCLineQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(VCLineQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 1:
            raise ValueError, "Expected 1 arguments, got %d" % _alen
        _x = util.get_float(args[0])
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _bounds = _node.getBoundary()
            _xmin = _bounds[0]
            _xmax = _bounds[2]
            if _x < _xmin or _x > _xmax:
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ne = _nw = _sw = _se = True
                if _x < _xmid: # vcline to left
                    _ne = _se = False
                if _x > _xmid: # vcline to right
                    _nw = _sw = False
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
        if not isinstance(obj, VCLine):
            raise TypeError, "Invalid VCLine object: " + `type(obj)`
        if obj in self:
            return
        _x, _y = obj.getLocation().getCoords()
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
        for _node in self.getNodes(_x):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(VCLineQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveVCLine)

    def delObject(self, obj):
        if obj not in self:
            return
        _pdict = {}
        _x, _y = obj.getLocation().getCoords()
        for _node in self.getNodes(_x):
            _node.delObject(obj)
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(VCLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _t = tolerance.TOL
        if _alen > 1:
            _t = tolerance.toltest(args[1])
        _xmin = _x - _t
        _xmax = _x + _t
        return self.getInRegion(_xmin, 0, _xmax, 1) # y values arbitrary

    def _moveVCLine(self, obj, *args):
        if obj not in self:
            raise ValueError, "VCLine not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        for _node in self.getNodes(_x):
            _node.delObject(obj) # vcline may not be in node
        super(VCLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        return self.find(x, tol)

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _vcls = []
        if not len(self):
            return _vcls
        _nodes = [self.getTreeRoot()]
        _vdict = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                for _subnode in _node.getSubnodes():
                    _bounds = _subnode.getBoundary()
                    _bmin = _bounds[0]
                    _bmax = _bounds[2]
                    if ((_bmin > _xmax) or (_bmax < _xmin)):
                        continue
                    _nodes.append(_subnode)
            else:
                for _vcl in _node.getObjects():
                    _vid = id(_vcl)
                    if _vid not in _vdict:
                        if _vcl.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _vcls.append(_vcl)
                        _vdict[_vid] = True
        return _vcls

#
# VCLine history class
#

class VCLineLog(conobject.ConstructionObjectLog):
    def __init__(self, v):
        if not isinstance(v, VCLine):
            raise TypeError, "Invalid VCLine: " + `type(v)`
        super(VCLineLog, self).__init__(v)
        v.connect('keypoint_changed', self._keypointChange)

    def _keypointChange(self, v, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old endpoint: " + `type(_old)`
        self.saveUndoData('keypoint_changed', _old.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _v = self.getObject()
        _p = _v.getLocation()
        _op = args[0]
        if _op == 'keypoint_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _parent = _v.getParent()
            if _parent is None:
                raise ValueError, "VCLine has no parent - cannot undo"
            _pt = _parent.getObject(_oid)
            if _pt is None or not isinstance(_pt, point.Point):
                raise ValueError, "Keypoint missing: id=%d" % _oid
            _sdata = _p.getID()
            self.ignore(_op)
            try:
                if undo:
                    _v.startUndo()
                    try:
                        _v.setLocation(_pt)
                    finally:
                        _v.endUndo()
                else:
                    _v.startRedo()
                    try:
                        _v.setLocation(_pt)
                    finally:
                        _v.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(VCLineLog, self).execute(undo, *args)
