#
# Copyright (c) 2002, 2004, 2005 Art Haas
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
# a class for storing selected objects
#

from PythonCAD.Generic import entity

class Selection(object):
    """A class used for storing selected objects.

A Selection object has the following methods:

storeObject(): Store a reference to some object.
getObjects(): Return all the objects held within the Selection object.
reset(): Empty the Selection object.

A Selection can have any number of objects added to it, and the
contents of a Selection can be retrieved any number of times.
Once the Selection has had its contents retrieved, however,
the addition of a new object will purge the current contents
of the selection.
    """
    def __init__(self):
        """Initialize a Selection object.

There are no arguments needed for this method.        
        """
        self.__image = None
        self.__objs = []
        self.__retrieved = False

    def hasObjects(self):
        """Test if there are objects stored in the Selection.

hasObjects()        
        """
        return len(self.__objs) > 0
    
    def storeObject(self, obj):
        """Store a reference to an object.

storeObject(obj)

Argument 'obj' can be an instance of the Entity class.
        """
        if not isinstance(obj, entity.Entity):
            raise TypeError, "Invalid object: " + `type(obj)`
        _layer = obj.getParent()
        if _layer is None:
            raise ValueError, "Object parent is None"
        _image = _layer.getParent()
        if _image is None:
            raise ValueError, "Object not stored in an Image"
        if (self.__retrieved or
            (self.__image is not None and _image is not self.__image)):
            self.reset()
        self.__image = _image
        _seen = False
        for _obj in self.__objs:
            if _obj is obj:
                _seen = True
                break
        if not _seen:
            self.__objs.append(obj)
        
    def getObjects(self):
        """Return all the currently selected objects.

getObjects()

This method returns a list.
        """
        self.__retrieved = True
        return self.__objs[:]
        
    def reset(self):
        """Reset the Selection object to empty.

reset()        
        """
        self.__image = None
        del self.__objs[:]
        self.__retrieved = False
