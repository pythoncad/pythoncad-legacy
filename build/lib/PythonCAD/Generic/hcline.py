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
# horizontal construction lines
#

from __future__ import generators

from PythonCAD.Generic import conobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import point
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import util

class HCLine(conobject.ConstructionObject):
    """A base class for horizontal construction lines.
    """
    __messages = {
        'moved' : True,
        'keypoint_changed' : True
        }
    
    def __init__(self, p, **kw):
        """Instantiate an HCLine object.

HCLine(p)
        """
        _p = p
        if not isinstance(p, point.Point):
            _p = point.Point(p)
        super(HCLine, self).__init__(**kw)
        self.__keypoint = _p
        _p.storeUser(self)
        _p.connect('moved', self.__movePoint)
        _p.connect('change_pending', self.__pointChangePending)
        _p.connect('change_complete', self.__pointChangeComplete)

    def __eq__(self, obj):
        """Compare one HCLine to another for equality.
        """
        if not isinstance(obj, HCLine):
            return False
        if obj is self:
            return True
        if abs(self.getLocation().y - obj.getLocation().y) < 1e-10:
            return True
        return False

    def __ne__(self, obj):
        """Compare one HCLine to another for inequality.
        """
        if not isinstance(obj, HCLine):
            return True
        if obj is self:
            return False
        if abs(self.getLocation().y - obj.getLocation().y) < 1e-10:
            return False
        return True

    def __str__(self):
        _x, _y = self.getLocation().getCoords()
        return "Horizontal Construction Line at y = %g" % self.__keypoint.y

    def finish(self):
        self.__keypoint.disconnect(self)
        self.__keypoint.freeUser(self)
        self.__keypoint = None
        super(HCLine, self).finish()

    def getValues(self):
        _data = super(HCLine, self).getValues()
        _data.setValue('type', 'hcline')
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
            _y = _kp.y
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
            if abs(_y - p.y) > 1e-10:
                self.sendMessage('moved', p.x, _y)
            self.sendMessage('modified')

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the HCLine to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required argument:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the HCLine. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _hy = self.__keypoint.y
        if abs(_hy - _y) < _t:
            return _x, _hy
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not an HCLine passes through a region.

inRegion(xmin, ymin, xmax, ymax)

The first four arguments define the boundary. The method
will return True if the HCLine falls between ymin and ymax.
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
        _y = self.__keypoint.y
        return not (_y < _ymin or _y > _ymax)

    def move(self, dx, dy):
        """Move a HCLine

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked() or self.__keypoint.isLocked():
            raise RuntimeError, "Moving HCLine not allowed - object locked."
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
            raise ValueError, "Invalid point for HCLine::movePoint()" + `p`
        if abs(p.y - _y) > 1e-10:
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
        _y = self.__keypoint.y
        if _ymin < _y < _ymax:
            return _xmin, _y, _xmax, _y
        return None

    def clone(self):
        """Create an identical copy of an HCLine.

clone()
        """
        return HCLine(self.__keypoint.clone())

    def sendsMessage(self, m):
        if m in HCLine.__messages:
            return True
        return super(HCLine, self).sendsMessage(m)

#
#
#

def intersect_region(hcl, xmin, ymin, xmax, ymax):
    if not isinstance(hcl, HCLine):
        raise TypeError, "Invalid HCLine: " + `type(hcl)`
    _xmin = util.get_float(xmin)
    _ymin = util.get_float(ymin)
    _xmax = util.get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = util.get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _x, _y = hcl.getLocation().getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if _ymin < _y < _ymax:
        _x1 = _xmin
        _y1 = _y
        _x2 = _xmax
        _y2 = _y
    return _x1, _y1, _x2, _y2

#
# Quadtree HCLine storage
#

class HCLineQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(HCLineQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 1:
            raise ValueError, "Expected 1 arguments, got %d" % _alen
        _y = util.get_float(args[0])
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _bounds = _node.getBoundary()
            _ymin = _bounds[1]
            _ymax = _bounds[3]
            if _y < _ymin or _y > _ymax:
                continue
            if _node.hasSubnodes():
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _y < _ymid: # hcline below
                    _nw = _ne = False
                if _y > _ymid: # hcline above
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
        if not isinstance(obj, HCLine):
            raise TypeError, "Invalid HCLine object: " + `type(obj)`
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
        for _node in self.getNodes(_y):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(HCLineQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveHCLine)

    def delObject(self, obj):
        if obj not in self:
            return
        _pdict = {}
        _x, _y = obj.getLocation().getCoords()
        for _node in self.getNodes(_y):
            _node.delObject(obj)
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(HCLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _y = util.get_float(args[0])
        _t = tolerance.TOL
        if _alen > 1:
            _t = tolerance.toltest(args[1])
        _hclines = []
        _ymin = _y - _t
        _ymax = _y + _t
        return self.getInRegion(0, _ymin, 1, _ymax) # x values arbitrary

    def _moveHCLine(self, obj, *args):
        if obj not in self:
            raise ValueError, "HCLine not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        for _node in self.getNodes(_y):
            _node.delObject(obj) # hcline may not be in node
        super(HCLineQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        return self.find(y, tol)

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _hcls = []
        if not len(self):
            return _hcls
        _nodes = [self.getTreeRoot()]
        _hdict = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                for _subnode in _node.getSubnodes():
                    _bounds = _subnode.getBoundary()
                    _bmin = _bounds[1]
                    _bmax = _bounds[3]
                    if ((_bmin > _ymax) or (_bmax < _ymin)):
                        continue
                    _nodes.append(_subnode)
            else:
                for _hcl in _node.getObjects():
                    _hid = id(_hcl)
                    if _hid not in _hdict:
                        if _hcl.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _hcls.append(_hcl)
                        _hdict[_hid] = True
        return _hcls

#
# HCLine history class
#

class HCLineLog(conobject.ConstructionObjectLog):
    def __init__(self, h):
        if not isinstance(h, HCLine):
            raise TypeError, "Invalid HCLine: " + `type(h)`
        super(HCLineLog, self).__init__(h)
        h.connect('keypoint_changed', self._keypointChange)

    def _keypointChange(self, h, *args):
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
        _h = self.getObject()
        _p = _h.getLocation()
        _op = args[0]
        if _op == 'keypoint_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _parent = _h.getParent()
            if _parent is None:
                raise ValueError, "HCLine has no parent - cannot undo"
            _pt = _parent.getObject(_oid)
            if _pt is None or not isinstance(_pt, point.Point):
                raise ValueError, "Keypoint missing: id=%d" % _oid
            _sdata = _p.getID()
            self.ignore(_op)
            try:
                if undo:
                    _h.startUndo()
                    try:
                        _h.setLocation(_pt)
                    finally:
                        _h.endUndo()
                else:
                    _h.startRedo()
                    try:
                        _h.setLocation(_pt)
                    finally:
                        _h.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(HCLineLog, self).execute(undo, *args)
