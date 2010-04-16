#
# Copyright (c) 2004, 2005, 2006 Art Haas
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
# quadtree storage for dimension objects
#

import math

from PythonCAD.Generic import dimension
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import point
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import util

#
# Dimension storage
#

class DimQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(DimQuadtree, self).__init__()

    def addObject(self, obj):
        if not isinstance(obj, dimension.Dimension):
            raise TypeError, "Invalid Dimension object: " + `obj`
        if obj in self:
            return
        _dxmin, _dymin, _dxmax, _dymax = obj.getBounds()
        _node = self.getTreeRoot()
        _bounds = _node.getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _dxmin - 1.0
            _ymin = _dymin - 1.0
            _xmax = _dxmax + 1.0
            _ymax = _dymax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _dxmin < _xmin:
                _xmin = _dxmin - 1.0
                _resize = True
            if _dxmax > _xmax:
                _xmax = _dxmax + 1.0
                _resize = True
            if _dymin < _ymin:
                _ymin = _dymin - 1.0
                _resize = True
            if _dymax > _ymax:
                _ymax = _dymax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
            _node = self.getTreeRoot()
        _nodes = [_node]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_dxmin > _xmax) or
                (_dymin > _ymax) or
                (_dxmax < _xmin) or
                (_dymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _dxmax < _xmid: # dim on left side
                    _ne = _se = False
                if _dxmin > _xmid: # dim on right side
                    _nw = _sw = False
                if _dymax < _ymid: # dim below
                    _nw = _ne = False
                if _dymin > _ymid: # dim above
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
                if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                    _node.addObject(obj)
        super(DimQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveDim)

    def delObject(self, obj):
        if obj not in self:
            return
        _dxmin, _dymin, _dxmax, _dymax = obj.getBounds()
        _xmin = _ymin = _xmax = _ymax = None
        _pdict = {}
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_dxmin > _xmax) or
                (_dxmax < _xmin) or
                (_dymin > _ymax) or
                (_dymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _dxmax < _xmid: # dim on left side
                    _ne = _se = False
                if _dxmin > _xmid: # dim on right side
                    _nw = _sw = False
                if _dymax < _ymid: # dim below
                    _nw = _ne = False
                if _dymin > _ymid: # dim above
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
                _node.delObject(obj) # dim may not be in the node ...
                _parent = _node.getParent()
                if _parent is not None:
                    _pid = id(_parent)
                    if _pid not in _pdict:
                        _pdict[_pid] = _parent
        super(DimQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _p1 = args[0]
        if not isinstance(_p1, point.Point):
            raise TypeError, "Invalid point: " + `type(_p1)`
        _p2 = args[1]
        if not isinstance(_p2, point.Point):
            raise TypeError, "Invalid point: " + `type(_p2)`
        _dims = []
        if len(self) > 0:
            _l1 = _p1.getParent()
            _l2 = _p2.getParent()
            for _dim in self.getObjects():
                _dp1, _dp2 = _dim.getDimPoints()
                _dl1 = _dp1.getParent()
                _dl2 = _dp2.getParent()
                if ((_l1 is _dl1) and
                    (_p1 is _dp1) and
                    (_l2 is _dl2) and
                    (_p2 is _dp2)):
                    _dims.append(_dim)
                if ((_l1 is _dl2) and
                    (_p1 is _dp2) and
                    (_l2 is _dl1) and
                    (_p2 is _dp1)):
                    _dims.append(_dim)
        return _dims

    def _moveDim(self, obj, *args):
        if obj not in self:
            raise ValueError, "Dimension not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _dxmin = util.get_float(args[0])
        _dymin = util.get_float(args[1])
        _dxmax = util.get_float(args[2])
        _dymax = util.get_float(args[3])
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_dxmin > _xmax) or
                (_dxmax < _xmin) or
                (_dymin > _ymax) or
                (_dymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _dxmax < _xmid: # dim on left side
                    _ne = _se = False
                if _dxmin > _xmid: # dim on right side
                    _nw = _sw = False
                if _dymax < _ymid: # dim below
                    _nw = _ne = False
                if _dymin > _ymid: # dim above
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
                _node.delObject(obj) # dim may not be in node ...
        super(DimQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _dim = _tsep = None
        _bailout = False
        _ddict = {}
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
                for _d in _node.getObjects():
                    _did = id(_d)
                    if _did not in _ddict:
                        _pt = _d.mapCoords(_x, _y, _t)
                        if _pt is not None:
                            _px = _py = _pt
                            _sep = math.hypot((_px - _x), (_py - _y))
                            if _tsep is None:
                                _tsep = _sep
                                _dim = _d
                            else:
                                if _sep < _tsep:
                                    _tsep = _sep
                                    _dim = _d
                            if _dim is not None and _sep < 1e-10:
                                _bailout = True
                                break
            if _bailout:
                break
        return _dim

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _dims = []
        if not len(self):
            return _dims
        _nodes = [self.getTreeRoot()]
        _ddict = {}
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
                for _dim in _node.getObjects():
                    _dimid = id(_dim)
                    if _dimid not in _ddict:
                        if _dim.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _dims.append(_dim)
                        _ddict[_dimid] = True
        return _dims

#
# LinearDimension Quadtree
#

class LDimQuadtree(DimQuadtree):
    def __init__(self):
        super(LDimQuadtree, self).__init__()

    def addObject(self, obj):
        if not isinstance(obj, dimension.LinearDimension):
            raise TypeError, "Invalid LinearDimension object: " + `obj`
        super(LDimQuadtree, self).addObject(obj)

#
# HorizontalDimension Quadtree
#

class HDimQuadtree(DimQuadtree):
    def __init__(self):
        super(HDimQuadtree, self).__init__()

    def addObject(self, obj):
        if not isinstance(obj, dimension.HorizontalDimension):
            raise TypeError, "Invalid HorizontalDimension object: " + `obj`
        super(HDimQuadtree, self).addObject(obj)

#
# VerticalDimension Quadtree
#

class VDimQuadtree(DimQuadtree):
    def __init__(self):
        super(VDimQuadtree, self).__init__()

    def addObject(self, obj):
        if not isinstance(obj, dimension.VerticalDimension):
            raise TypeError, "Invalid VerticalDimension object: " + `obj`
        super(VDimQuadtree, self).addObject(obj)

#
# RadialDimension Quadtree
#

class RDimQuadtree(DimQuadtree):
    def __init__(self):
        super(RDimQuadtree, self).__init__()

    def addObject(self, obj):
        if not isinstance(obj, dimension.RadialDimension):
            raise TypeError, "Invalid RadalDimension object: " + `obj`
        super(RDimQuadtree, self).addObject(obj)

    def find(self, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _c1 = args[1]
        if not isinstance(_c1, (circle.Circle, arc.Arc)):
            raise TypeError, "Invalid circle/arc: " + `type(_c1)`
        _dims = []
        if len(self) > 0:
            _l1 = _c1.getParent()
            for _rdim in self.getObjects():
                _rc = _rdim.getDimCircle()
                _rl = _rc.getParent()
                if _rl is _l1 and _rc is _c1:
                    _dims.append(_dim)
        return _dims

#
# AngularDimension Quadtree
#

class ADimQuadtree(DimQuadtree):
    def __init__(self):
        super(ADimQuadtree, self).__init__()

    def addObject(self, obj):
        if not isinstance(obj, dimension.AngularDimension):
            raise TypeError, "Invalid AngularDimension object: " + `obj`
        super(ADimQuadtree, self).addObject(obj)

    def find(self, *args):
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _vp = args[0]
        if not isinstance(_vp, point.Point):
            raise TypeError, "Invalid point: " + `type(_vp)`
        _p1 = args[1]
        if not isinstance(_p1, point.Point):
            raise TypeError, "Invalid point: " + `type(_p1)`
        _p2 = args[2]
        if not isinstance(_p2, point.Point):
            raise TypeError, "Invalid point: " + `type(_p2)`
        _dims = []
        if len(self) > 0:
            _vl = _vp.getParent()
            _l1 = _p1.getParent()
            _l2 = _p2.getParent()
            for _adim in self.getObjects():
                _avp, _ap1, _ap2 = _adim.getDimPoints()
                _avl = _avp.getParent()
                _al1 = _ap1.getParent()
                _al2 = _ap2.getParent()
                if ((_vl is _avl) and
                    (_vp is _avp) and
                    (_l1 is _al1) and
                    (_p1 is _ap1) and
                    (_l2 is _al2) and
                    (_p2 is _ap2)):
                    _dims.append(_dim)
                if ((_vl is _avl) and
                    (_vp is _avp) and
                    (_l1 is _al2) and
                    (_p1 is _ap2) and
                    (_l2 is _al1) and
                    (_p2 is _ap1)):
                    _dims.append(_dim)
        return _dims
