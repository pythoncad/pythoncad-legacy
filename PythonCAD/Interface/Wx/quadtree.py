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

from Interface.Wx.basetree import BaseTree

#from PythonCAD.Generic import tolerance
#from PythonCAD.Generic import util
#from PythonCAD.Generic import baseobject
#from PythonCAD.Generic import quadtree
#from PythonCAD.Generic import entity

#
# Quadtree storage
#

class Quadtree(Basetree):
    def __init__(self):
        super(Quadtree, self).__init__()

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

