#
# Copyright (c) 2003, 2004, 2005 Art Haas
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
# quadtree class definition
#
# TODO: Look at using weak references ...

from __future__ import generators

from PythonCAD.Generic import message

class QTreeNode(message.Messenger):
    __messages = {
        'subdivided' : True,
        'reparented' : True,
        'adjusted' : True,
        'full' : True,
        }
    
    NENODE = 1
    NWNODE = 2
    SWNODE = 3
    SENODE = 4
    
    def __init__(self):
        super(QTreeNode, self).__init__()
        self.__subnodes = None
        self.__bounds = None
        self.__parent = None
        self.__threshold = 5
        self.__objects = []

    def __len__(self):
        return len(self.__objects)

    def setBoundary(self, xmin, ymin, xmax, ymax):
        if self.__subnodes is not None or self.__parent is not None:
            raise RuntimeError, "Node cannot have boundary changed."
        _xmin = xmin
        if not isinstance(_xmin, float):
            _xmin = float(xmin)
        _ymin = ymin
        if not isinstance(_ymin, float):
            _ymin = float(ymin)
        _xmax = xmax
        if not isinstance(_xmax, float):
            _xmax = float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = ymax
        if not isinstance(_ymax, float):
            _ymax = float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        self.__bounds = (_xmin, _ymin, _xmax, _ymax)

    def unsetBoundary(self):
        if self.__subnodes is not None or len(self.__objects) != 0:
            raise RuntimeError, "Node cannot have boundary changed."
        self.__bounds = None

    def getBoundary(self):
        return self.__bounds

    def setThreshold(self, count):
        _t = self.__threshold
        _count = count
        if not isinstance(_count, int):
            _count = int(count)
        if _count < 1:
            raise ValueError, "Invalid threshold: %d" % _count
        if _count != _t:
            self.__threshold = _count
            self.sendMessage('adjusted', _t)
            if len(self) >  _count:
                self.sendMessage('full')

    def getThreshold(self):
        return self.__threshold

    def setParent(self, parent):
        _p = self.__parent
        if parent is not None and not isinstance(parent, QTreeNode):
            raise TypeError, "Invalid QTreeNode parent: " + `type(parent)`
        if parent is not _p:
            self.__parent = parent
            self.sendMessage('reparented', _p)

    def getParent(self):
        return self.__parent

    def addObject(self, obj):
        _seen = False
        for _obj in self.__objects:
            if _obj is obj:
                _seen = True
                break
        if not _seen:
            self.__objects.append(obj)
            if self.canSubdivide():
                self.sendMessage('full')

    def getSubnode(self, subnode):
        if self.__subnodes is None:
            raise RuntimeError, "QTreeNode has no subnodes."
        _ne, _nw, _sw, _se = self.__subnodes
        if subnode == QTreeNode.NENODE:
            _sub = _ne
        elif subnode == QTreeNode.NWNODE:
            _sub = _nw
        elif subnode == QTreeNode.SWNODE:
            _sub = _sw
        elif subnode == QTreeNode.SENODE:
            _sub = _se
        else:
            raise ValueError, "Unknown subnode code: %d" % subnode
        return _sub

    def delObject(self, obj):
        for _i in range(len(self.__objects)):
            if obj is self.__objects[_i]:
                del self.__objects[_i]
                break

    def getObjects(self):
        return self.__objects[:]

    def delObjects(self):
        del self.__objects[:]

    def hasSubnodes(self):
        return self.__subnodes is not None

    def getSubnodes(self):
        return self.__subnodes

    def delSubnodes(self):
        if self.__subnodes is None:
            raise RuntimeError, "QTreeNode has no subnodes."
        for _subnode in self.__subnodes:
            _subnode.setParent(None)
        self.__subnodes = None

    def canSubdivide(self):
        if not len(self) > self.__threshold:
            return False
        _objs = self.__objects
        _flag = True
        for _obj in _objs:
            if not hasattr(_obj, '__eq__'):
                _flag = False
                break
        if not _flag:
            return len(self) > self.__threshold
        #
        # _test is an array of booleans:
        # _test[i] is True => object is unique
        # _test[i] is False => object is equal to another in list
        #
        # _test[0] is always True, so test from _test[1] to end
        #
        _test = [True] * len(_objs)
        _max = len(_test)
        for _i in range(_max - 1):
            if _test[_i]: # current object is unique ...
                for _j in range((_i + 1), _max):
                    if _objs[_j] == _objs[_i]:
                        _test[_j] = False
        return _test.count(True) > self.__threshold

    def subdivide(self):
        if len(self) < self.__threshold:
            return
        _xmin, _ymin, _xmax, _ymax = self.__bounds
        _xmid = (_xmin + _xmax)/2.0
        _ymid = (_ymin + _ymax)/2.0
        #
        # NE Node
        #
        _nenode = QTreeNode()
        _nenode.setBoundary(_xmid, _ymid, _xmax, _ymax)
        _nenode.setThreshold(self.__threshold)
        _nenode.setParent(self)
        #
        # NW Node
        #
        _nwnode = QTreeNode()
        _nwnode.setBoundary(_xmin, _ymid, _xmid, _ymax)
        _nwnode.setThreshold(self.__threshold)
        _nwnode.setParent(self)
        #
        # SW Node
        #
        _swnode = QTreeNode()
        _swnode.setBoundary(_xmin, _ymin, _xmid, _ymid)
        _swnode.setThreshold(self.__threshold)
        _swnode.setParent(self)
        #
        # SE Node
        #
        _senode = QTreeNode()
        _senode.setBoundary(_xmid, _ymin, _xmax, _ymid)
        _senode.setThreshold(self.__threshold)
        _senode.setParent(self)
        #
        self.__subnodes = (_nenode, _nwnode, _swnode, _senode)
        self.delObjects()
        self.sendMessage('subdivided')

    def sendsMessage(self, m):
        if m in QTreeNode.__messages:
            return True
        return super(QTreeNode, self).sendsMessage(m)

class Quadtree(message.Messenger):
    __messages = { }
    def __init__(self):
        super(Quadtree, self).__init__()
        self.__objects = {}
        self.__queued = []
        self.__splitnode = None
        self.__splitting = False
        self.__node = QTreeNode()
        self.__node.connect('full', self._splitTreeNode)

    def __nonzero__(self):
        return len(self.__objects) != 0

    def __len__(self):
        return len(self.__objects)

    def __contains__(self, obj):
        _oid = id(obj)
        return _oid in self.__objects

    def getTreeRoot(self):
        return self.__node

    def getNodes(self, *args):
        _nodes = [self.__node]
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                yield _node                
        
    def addObject(self, obj):
        _oid = id(obj)
        if _oid not in self.__objects:
            self.__objects[_oid] = obj
        if self.__splitnode is not None and not self.__splitting:
            self.__splitting = True
            _node = self.__splitnode
            _objs = _node.getObjects()
            _node.subdivide()
            for _subnode in _node.getSubnodes():
                _subnode.connect('full', self._splitTreeNode)
            _root = self.__node
            self.__node = self.__splitnode
            try:
                for _obj in _objs:
                    _oid = id(_obj)
                    if _oid not in self.__objects:
                        raise ValueError, "Lost object: " + str(_obj)
                    del self.__objects[_oid]
                    self.addObject(_obj)
                    if _oid not in self.__objects:
                        raise ValueError, "self.addObject() failed: " + str(_obj)
            finally:
                self.__node = _root
            self.__splitnode = None
            self.__splitting = False
        # set to False for Quadtree consistency testing
        if True or self.__splitnode is not None:
            return
        _objcount = len(self.__objects)
        _nodes = [self.__node]
        _nobj = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _obj in _node.getObjects():
                    _oid = id(_obj)
                    if _oid not in _nobj:
                        _nobj[_oid] = True
        _nc = len(_nobj)
        if _nc > _objcount:
            print "Count inconsistency: %d > %d" % (_nc, _objcount)
            print "Quadtree objects:"
            for _obj in self.__objects.values():
                print "obj: " + str(_obj)
            _bounds = self.__node.getBoundary()
            print "tree bounds: " + str(_bounds)
            _nodes = [self.__node]
            _nobj = {}
            while len(_nodes):
                _node = _nodes.pop()
                _bounds = _node.getBoundary()
                if _node.hasSubnodes():
                    print "Node with subnodes: " + str(_bounds)
                    _nodes.extend(_node.getSubnodes())
                else:
                    print "Base node: " + str(_bounds)
                    for _obj in _node.getObjects():
                        print "obj: " + str(_obj)
                        _oid = id(_obj)
                        if _oid not in _nobj:
                            _nobj[_oid] = _obj
                        if _oid not in self.__objects:
                            print "###Object lost###"
            raise RuntimeError, "Inconsistent quadtree"

    def getObject(self, obj):
        _oid = id(obj)
        return self.__objects.get(_oid) # returns None if _oid not found

    def getObjects(self):
        return self.__objects.values()

    def delObject(self, obj):
        _oid = id(obj)
        if _oid in self.__objects:
            del self.__objects[_oid]

    def delObjects(self):
        _nodes = [self.__node]
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
                _node.delSubnodes()
            else:
                for _obj in _node.getObjects():
                    _obj.disconnect(self)
                _node.delObjects()
                if _node.getParent() is not None:
                    _node.setParent(None)
                    _node.disconnect(self)
        self.__objects.clear()
        self.__node.unsetBoundary()

    def queueObject(self, obj):
        _oid = id(obj)
        if _oid in self.__objects:
            raise ValueError, "Object already stored in Quadtree: " + `obj`
        self.__queued.append(obj)

    def emptyQueue(self):
        _objs = self.__queued[:]
        del self.__queued[:]
        return _objs

    def find(self, *params):
        return []

    def getClosest(self, x, y, tol):
        return None

    def getInRegion(self, xmin, ymin, xmax, ymax):
        return []

    def resize(self, xmin, ymin, xmax, ymax):
        _xmin = xmin
        if not isinstance(_xmin, float):
            _xmin = float(xmin)
        _ymin = ymin
        if not isinstance(_ymin, float):
            _ymin = float(ymin)
        _xmax = xmax
        if not isinstance(_xmax, float):
            _xmax = float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = ymax
        if not isinstance(_ymax, float):
            _ymax = float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _root = self.__node
        if _root is not self.__splitnode:
            if not _root.hasSubnodes():
                _root.setBoundary(_xmin, _ymin, _xmax, _ymax)
            else:
                _objs = self.__objects.values()
                self.delObjects()
                _root.setBoundary(_xmin, _ymin, _xmax, _ymax)
                for _obj in _objs:
                    self.addObject(_obj)

    def _splitTreeNode(self, node, *args):
        if self.__splitnode is None:
            self.__splitnode = node
        
    def purgeSubnodes(self, node):
        if not isinstance(node, QTreeNode):
            raise TypeError, "Invalid node: " + `type(node)`
        _tmpnode = node
        _parent = node.getParent()
        while _parent is not None:
            _tmpnode = _parent
            _parent = _tmpnode.getParent()
        if self.__node is not _tmpnode:
            raise ValueError, "Node not in tree."
        if node.hasSubnodes():
            _flag = True
            _count = 0
            for _subnode in node.getSubnodes():
                if _subnode.hasSubnodes():
                    _flag = False
                    break
                _count = _count + len(_subnode)
            if _flag and _count < node.getThreshold():
                _objs = []
                for _subnode in node.getSubnodes():
                    _objs.extend(_subnode.getObjects())
                node.delSubnodes()
                for _obj in _objs:
                    Quadtree.delObject(self, _obj)
                    self.addObject(_obj)

    def sendsMessage(self, m):
        if m in Quadtree.__messages:
            return True
        return super(Quadtree, self).sendsMessage(m)

