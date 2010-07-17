#
# Copyright (c) 2002, 2003 Art Haas
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
# a class for maintaining a sorted list
#
# each list holds only a single type of object, and
# the list is organized from smallest to largest
#

from PythonCAD.Generic import baseobject

class TreeItem(baseobject.ModObject):
    """An object stored in a Tree.

A TreeItem object is meant to be a base class for classes
that will have instances stored in a Tree. TreeItem objects
are derived from ModObjects, so they share the same attributes
and methods as those objects.
    """
    def __init__(self):
        """Initialize a TreeItem object.

There are no arguments to this method.
        """
        baseobject.ModObject.__init__(self)
        self.__tree = None # private to the TreeItem

    def _setTree(self, tree):
        """Store a reference to the Tree this TreeItem is stored within.

_setTree(tree)

A TreeItem object can only be kept in one Tree at a time.

This routine is private to the TreeItem implementation.
        """
        if tree is None:
            self.__tree = None
        else:
            if not isinstance(tree, Tree):
                raise TypeError, "Invalid Tree for storage: " + str(tree)
            if self.__tree is not None:
                raise ValueError, "TreeItem already claimed by a tree."
            self.__tree = tree
        
    def modified(self):
        """Set the modified flag value to True.

modified()

This method extends the ModObject::modified() method
        """
        baseobject.ModObject.modified(self)
        if self.__tree is not None:
            self.__tree.markModified(self)

class Tree(list):
    """A class for Trees.

The Tree class is similar to a list, but it stores the
objects in a sorted order. A Tree object can be iterated
over, and there is a several method for scanning objects
held in the tree.

An object stored in the tree must be derived from the TreeItem
class.

A Tree has several methods:

clear(): Remove all objects from the tree.
store(obj): Store some object in the tree.
remove(obj): Remove an object from the tree
binscan(obj): Search the tree for the object using a binary search
scan(obj): Search the tree for the object using a linear search.
isModified(): An object stored in the Tree has its modified flag set to True
getModified(): Return the objects in the Tree that are modified
clean(): Sort the objects stored in the Tree, and remove any duplicates.

Trees also have a modified __add__ method that allows
you to add trees together, and a __contains__ method
for doing "obj in tree" or "obj not in tree" operations.

Also, a Tree supports indexed retrival similar to a list,
but not allow indexed assignment or indexed deletion.
    """
    def __init__(self, t):
        """Initialize a Tree.

Tree(t)

A Tree takes a single parameter t which is the
type of object stored within the tree. Any Tree
will only hold one type of object, and that object
type cannot be None.
        """
        if not issubclass(t, TreeItem):
            raise ValueError, "Invalid object for Tree storage: " + `t`
        list.__init__(self)
        self.__type = t
        self.__iter_index = 0
        self.__modified = []

    def __iter__(self):
        """Make a Tree iterable.
        """
        if len(self.__modified):
            raise ValueError, "Tree in modified state."
        self.__iter_index = 0
        return self

    def next(self):
        """This method is used for iteration.
        """
        _index = self.__iter_index
        _next = _index + 1
        if _next > len(self):
            raise StopIteration
        self.__iter_index = _next
        return self[_index]
    
    def __setitem__(self, index, value):
        raise StandardError, "Tree::__setitem__() is not supported."

    def __delitem__(self, index):
        raise StandardError, "Tree::__delitem__() is not supported."

    def __setslice__(self, i, j, vals):
        raise StandardError, "Tree::__setslice__() is not supported."

    def __delslice__(self, i, j):
        raise StandardError, "Tree::__delslice__() is not supported."

    def append(self, obj):
        raise StandardError, "Tree::append() is not supported."

    def insert(self, index, obj):
        raise StandardError, "Tree::insert() is not supported."

    def extend(self, objlist):
        raise StandardError, "Tree::extend() is not supported."

    def pop(self, idx=-1):
        raise StandardError, "Tree::pop() is not supported."

    def reverse(self):
        raise StandardError, "Tree::reverse() is not supported."

    def __contains__(self, obj):
        """Test if an object is in a Tree.

This method uses a binary search to find if an object
is in a Tree. It _should_ always be faster than a simple
linear search from first object to the last.
        """
        if not isinstance(obj, self.__type):
            raise TypeError, "Invalid object for inclusion test: " + `obj`
        if len(self.__modified):
            raise ValueError, "Tree in modified state."
        _lo = 0
        _hi = len(self)
        _scanlist = []
        _seen = False
        while _lo < _hi:
            _mid = (_hi+_lo)//2
            if _mid in _scanlist:
                break
            _scanlist.append(_mid)
            _res = cmp(self[_mid], obj)
            if _res == -1:
                _lo = _mid + 1
            elif _res == 1:
                _hi = _mid
            else:
                _seen = True
                break
        return _seen
        
    def clear(self):
        """Empty the Tree.

clear()
        """
        del self.__modified[:]
        list.__delslice__(self, 0, len(self))

    def markModified(self, treeitem):
        """Store a reference to a modified TreeItem object.

markModified(treeitem)

This routine is private to the Tree implementation.
        """
        self.__modified.append(treeitem)
        
    def store(self, obj):
        """Store an object in the Tree.

store(obj)

The object must be the same as was given when the tree
was instantiated. A TypeError is raised if another
object type is stored.

The objects in the Tree are searched by using the cmp()
function. Any class that will be stored in a Tree should
provide a suitable __cmp__ method.
        """
        if not isinstance(obj, self.__type):
            raise TypeError, "Invalid object for storage: " + `obj`
        obj._setTree(self)
        if len(self.__modified):
            raise ValueError, "Tree in modified state."
        _lo = 0
        _hi = len(self)
        _scanlist = []
        while _lo < _hi:
            _mid = (_hi+_lo)//2
            if _mid in _scanlist:
                break
            _scanlist.append(_mid)
            _res = cmp(self[_mid], obj)
            if _res == -1:
                _lo = _mid + 1
            elif _res == 1:
                _hi = _mid
            else:
                raise ValueError, "Equivalent object already in tree: " + `obj`
        list.insert(self, _lo, obj)
        assert _is_sorted(self), "Tree is not sorted: " + `self`

    def remove(self, obj):
        """Remove an object from a Tree.

remove(obj)

Delete the object from the Tree.
        """
        if not isinstance(obj, self.__type):
            raise TypeError, "Invalid object for removal: " + `obj`
        if len(self.__modified):
            raise ValueError, "Tree in modified state."
        obj._setTree(None)
        _lo = 0
        _hi = len(self)
        _scanlist = []
        while _lo < _hi:
            _mid = (_hi+_lo)//2
            if _mid in _scanlist:
                break
            _scanlist.append(_mid)
            _res = cmp(self[_mid], obj)
            if _res == -1:
                _lo = _mid + 1
            elif _res == 1:
                _hi = _mid
            else:
                list.__delitem__(self, _mid)
                break
    
    def binscan(self, obj, tol=0):
        """Scan the Tree for the an object using a binary search.

binscan(obj)

This method looks for an object in a Tree utilizing a simple
binary search. If the object is found within the tree, the
index of the object is returned. Otherwise, the function returns
None.
        """
        if not isinstance(obj, self.__type):
            raise TypeError, "Invalid object for binscan: " + `obj`
        if len(self.__modified):
            raise ValueError, "Tree in modified state."
        _lo = 0
        _hi = len(self)
        _scanlist = []
        _ro = None
        while _lo < _hi:
            _mid = (_hi+_lo)//2
            if _mid in _scanlist:
                break
            _scanlist.append(_mid)
            _res = cmp(self[_mid], obj)
            if _res == -1:
                _lo = _mid + 1
            elif _res == 1:
                _hi = _mid
            else:
                _ro = self[_mid]
                break
        return _ro

    def scan(self, obj, tol=0):
        """Scan the Tree for the an object from first to last.

scan(obj)

This method looks for an object in a Tree from the first object
to the last. It stops searching at the first instance which is
greater than the object, or the first instance where one object
is equal to the other.

The function returns None if no object in the Tree is found
equal to the object being compared against.
        """
        if not isinstance(obj, self.__type):
            raise TypeError, "Invalid object for scan: " + `obj`
        if len(self.__modified):
            raise ValueError, "Tree in modified state."
        _ro = None
        for _sobj in self:
            _res = cmp(_sobj, obj)
            if _res == 1:
                break
            if _res == 0:
                _ro = _sobj
                break
        return _ro

    def isModified(self):
        """Returns True if an object in the tree has the modified flag to True.

isModified()        
        """
        return len(self.__modified) != 0

    def getModified(self):
        """Return any objects in the tree that have the modified flag to True.

getModified()        
        """
        return self.__modified[:]
    
    def clean(self):
        """Sort the objects in the tree, and remove duplicated entities.

clean()

This function returns any duplicated entities found in the Tree.
It is up to the caller to deal with any returned objects.
        """
        _dups = []
        if len(self.__modified):
            self.sort()
            _pobj = self[0]
            _dlist = []
            for _i in range(1, len(self)):
                _obj = self[_i]
                if _obj == _pobj:
                    _dlist.append(_i)
                else:
                    _pobj = _obj
            if len(_dlist):
                _dlist.reverse()
                for _i in _dlist:
                    _dups.append(self[_i])
                    list.__delitem__(self, _i)
            for _obj in self.__modified:
                if _obj not in _dups:
                    _obj.reset()
            del self.__modified[:]
        return _dups

#
# this is a function used for assertion testing
#

def _is_sorted(tree):
    _res = True
    for _i in range(1, len(tree)):
        _tp = tree[_i-1]
        _ti = tree[_i]
        if _tp >= _ti:
            _res = False
            break
    return _res
