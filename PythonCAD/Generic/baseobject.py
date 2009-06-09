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
# This file contains simple classes meant to be used as base classes.
#

from PythonCAD.Generic import entity

class ModObject(object):
    """A base class for objects that store a modification state variable.

There are several methods for the modobject class:

isModified(): Test the state of the modified flag
modified(): Set the modified flag to True
reset(): Set the modified flag to False

This class is meant to be used as a base class for more complex
classes.
    """
    def __init__(self):
        """Initialize a modobject instance.

There are no arguments needed for this method.
        """
        self.__modified = False

    def isModified(self):
        """Tests the modified state flag of the modobject.

isModified()
        """
        return self.__modified

    def modified(self):
        """Set the modified state flag value to True.

modified()
        """
        self.__modified = True

    def reset(self):
        """Set the modified state flag value to False.

reset()
        """
        self.__modified = False

class SListObject(object):
    """Base class for objects emulating unidirectional linked lists.

A SListObject has the following attributes:

next: The next object in the list.

A SListObject has the following methods:

{get/set/del}Next(): Get/Set the next object in the list.
    """
    def __init__(self):
        """Initialize a SListObject object.
        """
        self.__next = None

    def getNext(self):
        """Get the object following this object.

getNext()
        """
        return self.__next

    def setNext(self, obj):
        """Set the object that will follow this object.

setNext(obj)

The object must be an instance of a ListObject.
        """
        if obj is not None:
            if not isinstance(obj, SListObject):
                raise TypeError, "Invalid SListObject: " + str(obj)
        self.__next = obj

    def delNext(self):
        """Delete the object that follows this object.

delNext()

This method returns the deleted object.
        """
        _next = self.__next
        if _next is not None:
            self.__next = _next.getNext()
            _next.setNext(None)
        return _next

    next = property(getNext, setNext, delNext, "Accessor to the next object.")

class DListObject(SListObject):
    """Base class for objects emulating doubly linked lists.

A DListObject is derived from a SListObject, so it shares the
attributes and methods of that class. Addtionally it has
the following attributes

prev: The previous object in the list

A DListObject has the following addtional methods:

{get/set/del}Prev(): Get/Set the previous object in the list.
    """
    def __init__(self):
        """Initialize a DListObject object.
        """
        SListObject.__init__(self)
        self.__prev = None

    def getPrev(self):
        """Get the object preceeding this object.

getPrev()
        """
        return self.__prev

    def setPrev(self, obj):
        """Set the object that will precede this object.

setPrev(obj)

The object must be an instance of a DListObject.
        """
        if obj is not None:
            if not isinstance(obj, DListObject):
                raise TypeError, "Invalid DListObject: " + str(obj)
            obj.setNext(self)
        self.__prev = obj

    def delPrev(self):
        """Delete the object preceding this object.

delPrev(obj)

This method returns the previous object.
        """
        _prev = self.__prev
        if _prev is not None:
            _new_prev = _prev.getPrev()
            self.__prev = _new_prev
            if _new_prev is not None:
                _new_prev.setNext(self)
            _prev.__prev = None
            _prev.setNext(None)
        return _prev

    prev = property(getPrev, setPrev, delPrev, "Accessor to preceding object.")

#
# base class for objects that are components of other
# objects
#

class Subpart(entity.Entity):
    """A base class for objects that store references to other objects.

The Subpart class is meant to be a base class for other classes defining
simple objects that will be used in other objects but are not subclasses
of those other objects. The Subpart objects that are in those classes
can be used to store references to the larger object. The Subpart
class has the following methods:

storeUser(): Save a reference to some object.
freeUser(): Release a reference to some object
getUsers(): Return the list of objects that have been stored.
hasUsers(): Test if the subpart has any 
    """
    __messages = {
        'added_user' : True,
        'removed_user' : True,
        }
    
    def __init__(self, **kw):
        super(Subpart, self).__init__(**kw)
        self.__users = None

    def finish(self):
        if self.__users is not None:
            print "%d refs in users" % len(self.__users)
            for _user in self.__users:
                print "stray object reference to: " + `_user`
        super(Subpart, self).finish()
        
    def storeUser(self, obj):
        """Save a reference to another object.

storeObject(obj)

Argument 'obj' can be any type of object.
        """
        if self.__users is None:
            self.__users = []
        _users = self.__users
        _seen = False
        for _user in _users:
            if _user is obj:
                _seen = True
                break
        if not _seen:
            self.startChange('added_user')
            _users.append(obj)
            self.endChange('added_user')
            self.sendMessage('added_user', obj)

    def freeUser(self, obj):
        """Release a reference to another object.

freeObject(obj)

This method does nothing if the Component object has not
stored references to any object or if the argument 'obj'
had not been stored with storeObject().
        """
        if self.__users is not None:
            _users = self.__users
            for _i in range(len(_users)):
                if obj is _users[_i]:
                    self.startChange('removed_user')
                    del _users[_i]
                    self.endChange('removed_user')
                    self.sendMessage('removed_user', obj)
                    break
            if not len(_users):
                self.__users = None

    def getUsers(self):
        """Return the list of stored objects.

getObjects()

This method returns a list of references stored by
calling the storeObject() method.
        """
        if self.__users is not None:
            return self.__users[:]
        return []

    def countUsers(self):
        """Return the number of stored objects.

countUsers()        
        """
        _count = 0
        if self.__users is not None:
            _count = len(self.__users)
        return _count

    def hasUsers(self):
        """Test if the Subpart has any users.

hasUsers()

This method returns True if there are any users of this Subpart,
otherwise this method returns False.
        """
        return self.__users is not None

    def canParent(self, obj):
        """Test if an Entity can be the parent of another Entity.

canParent(obj)

This method overrides the Entity::canParent() method
        """
        return False

    def getValues(self):
        """Return values comprising the Subpart.

getValues()

This method extends the Entity::getValues() method.
        """
        return super(Subpart, self).getValues()
    
    def sendsMessage(self, m):
        if m in Subpart.__messages:
            return True
        return super(Subpart, self).sendsMessage(m)

#
# TypedDict Class
#
# The TypedDict class is built from the dict object. A TypedDict
# instance has a defined object type for a key and value and will
# only allow objects of that type to be used for these dictionary
# fields.
#

class TypedDict(dict):
    def __init__(self, keytype=None, valtype=None):
        super(TypedDict, self).__init__()
        self.__keytype = keytype
        self.__valtype = valtype
        
    def __setitem__(self, key, value):
        _kt = self.__keytype
        if _kt is not None:
            if not isinstance(key, _kt):
                raise TypeError, "Invalid key type %s" % type(key)
        _vt = self.__valtype
        if _vt is not None:
            if not isinstance(value, _vt):
                raise TypeError, "Invalid value type %s" % type(value)
        super(TypedDict, self).__setitem__(key, value)

#
# ConstDict class
#
# The ConstDict class is a TypedDict based class that allows
# the setting of a key only once and does not permit the
# deletion of the key. The idea with a ConstDict class is to
# store a non-modifiable set of key/value pairs.
#

class ConstDict(TypedDict):
    def __init__(self, keytype=None, valtype=None):
        super(ConstDict, self).__init__(keytype, valtype)

    def __setitem__(self, key, value):
        if key in self:
            raise KeyError, "Key already used: " + key
        super(ConstDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        pass # raise an exception?

#
# LockedDict class
#
# The LockedDict class is a TypedDict based class that allows
# the setting of keys/values until the dictionary is locked.
# After then the dictionary is cannot be altered. There is
# not an unlock method to allow changing the LockedDict object
# once it has been locked.
#

class LockedDict(TypedDict):
    def __init__(self, keytype=None, valtype=None):
        super(LockedDict, self).__init__(keytype, valtype)
        self.__locked = False

    def __setitem__(self, key, value):
        if self.__locked:
            raise KeyError, "LockedDict object is locked: " + `self`
        super(LockedDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        if self.__locked:
            raise KeyError, "LockedDict object is locked: " + `self`
        super(LockedDict, self).__delitem__(key)

    def lock(self):
        self.__locked = True
        
#
# TypedList Class
#
#
# The TypedList class is built from the list object. A TypedList
# instance has a defined object type for a occupant in the list and
# will only allow objects of that type to be stored.
#

class TypedList(list):
    def __init__(self, listtype=None):
        super(TypedList, self).__init__()
        self.__listtype = listtype

    def __setitem__(self, key, value):
        _lt = self.__listtype
        if _lt is not None:
            if not isinstance(value, _lt):
                raise TypeError, "Invalid list member %s" % type(value)
        super(TypedList, self).__setitem__(key, value)

    def append(self, obj):
        _lt = self.__listtype
        if _lt is not None:
            if not isinstance(obj, _lt):
                raise TypeError, "Invalid list member %s" % type(obj)
        super(TypedList, self).append(obj)

    def insert(self, idx, obj):
        _lt = self.__listtype
        if _lt is not None:
            if not isinstance(obj, _lt):
                raise TypeError, "Invalid list member %s" % type(obj)
        super(TypedList, self).insert(idx, obj)
