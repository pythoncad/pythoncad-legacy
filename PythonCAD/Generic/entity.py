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
#
# _The_ base class for all objects used in PythonCAD
#

import types

from PythonCAD.Generic import message
from PythonCAD.Generic import logger
from PythonCAD.Generic import util

class Entity(message.Messenger):
    """The base class for PythonCAD entities.

An entity has the following properties:

parent: The parent of an entity - another entity or None

An entity has the following methods:

{set/get}Lock(): Set/Get the locked state on an entity.
isLocked(): Returns the locked state of an entity.
isModified(): Returns the flag indicating the entity has been modified.
modified()/reset(): Set/Unset a flag indicating the entity modified state.
isVisible(): Returns the visibity of the entity.
{set/get}Visibility(): Set/Get the visibility flag on an entity.
{set/get}Parent(): Set/Get the parent entity of an entity.
{add/del}Child(): Add/Remove a child entity to/from another entity.
hasChild(): Test if one entity is a child of another.
hasChildren(): Test if an entity has any children entities.
getChildren(): Return a list of children entities for an entity.

A few short aliases exist for some of these methods:
lock(): Same as setLock(True)
unlock(): Same as setLock(False)
hide(): Same as setVisibility(True)
show()/expose(): Same as setVisibility(False)

The aliases may be removed at some point.
    """
    __messages = {
        'lock_changed' : True,
        'modified' : True,
        'reset' : True,
        # 'parent_changed' : True,
        'visibility_changed' : True,
        'refresh' : True,
        'added_child' : True,
        'removed_child' : True,
        'change_pending' : True,
        'change_complete' : True,
        }

    __idcount = 0

    def __init__(self, **kw):
        _parent = _id = None
        if 'parent' in kw:
            _parent = kw['parent']
            if _parent is not None and not isinstance(_parent, Entity):
                raise TypeError, "Unexpected parent type: " + `type(_parent)`
        if 'id' in kw:
            _id = kw['id']
            if not isinstance(_id, int):
                raise TypeError, "Unexpected ID type: " + `type(_id)`
            if _id < 0 or _id >= Entity.__idcount:
                raise ValueError, "Invalid ID: %d" % _id
        if _id is None:
            _id = Entity.__idcount
            Entity.__idcount = Entity.__idcount + 1
        super(Entity, self).__init__()
        self.__locked = False
        self.__modified = False
        self._visible = True
        self.__parent = None
        self.__children = None
        self.__log = None
        self.__undoing = 0 # 1 => undo, -1 => redo
        self._id = _id
        if _parent is not None:
            Entity.setParent(self, _parent)

    def finish(self):
        if self.__parent is not None:
            print "parent is not None: " + `self`
            print "parent: " + `self.__parent`
        if self.__children is not None:
            print "children is not None: " + `self`
            for _child in self.__children.values():
                print "Child: " + `_child`
        super(Entity, self).finish()

    def getValues(self):
        """Return values comprising the Entity.

getValues()

This method returns an EntityData instance.
        """
        _data = EntityData()
        _data.setValue('id', self._id)
        _pid = None
        if self.__parent is not None:
            _pid = self.__parent.getID()
        _data.setValue('pid', _pid)
        return _data

    values = property(getValues, None, None, "Entity values")

    def getID(self):
        """Return the unique integer identifier for the entity.

getID()
        """
        return self._id

    id = property(getID, None, None, "Entity ID")

    def isLocked(self):
        """Test if the entity has been locked.

isLocked()

This method returns a boolean.
        """
        return self.__locked

    def lock(self):
        """Set the entity so that its attributes cannot be changed.

lock()
        """
        Entity.setLock(self, True)

    def unlock(self):
        """Set the entity so that its attributes can be changed.

unlock()
        """
        Entity.setLock(self, False)

    def getLock(self):
        """Return the locked status of an entity.

getLock()        
        """
        return self.__locked
    
    def setLock(self, lock):
        """Set the locked status on an entity.

setLock(lock)

Argument 'lock' can be True or False.
        """
        util.test_boolean(lock)
        _l = self.__locked
        if _l is not lock:
            self.__locked = lock
            self.sendMessage('lock_changed', _l)
            self.modified()
        
    def isModified(self):
        """Test if the entity has been altered in some form.

isModified()

This method returns a boolean.
        """
        return self.__modified

    def startChange(self, msg):
        """Enter the modification state of an entity.

startChange(msg)

Argument 'msg' is the message the entity will send at the completion
of the modification.
        """
        if not self.sendsMessage(msg):
            raise ValueError, "Unknown message: %s" % msg
        self.sendMessage('change_pending', msg)

    def endChange(self, msg):
        """Complete the modification state of an entity.

endChange(msg)

This method is meant to complete the notification process begun
by the startChange() method.
        """
        if not self.sendsMessage(msg):
            raise ValueError, "Unknown message: %s" % msg
        self.sendMessage('change_complete', msg)
        
    def modified(self):
        """Indicate that the entity has been altered.

modified()
        """
        if not self.__modified:
            self.__modified = True
        self.sendMessage('modified')

    def reset(self):
        """Indicate that the entity is no longer altered.

reset()
        """
        if self.__modified:
            self.__modified = False
        self.sendMessage('reset')

    def isVisible(self):
        """Test to see if the entity can be seen.

isVisible()

This method returns a boolean.
        """
        return self._visible is True

    def getVisibility(self):
        """Return the visibility flag of an entity.

getVisibility()        
        """
        return self._visible
    
    def setVisibility(self, vis):
        """Set the visibility of the entity.

setVisibility(vis)

Argument 'vis' must be either True or False.
        """
        util.test_boolean(vis)
        _v = self._visible
        if _v is not vis:
            self.startChange('visibility_changed')
            self._visible = vis
            self.endChange('visibility_changed')
            self.sendMessage('visibility_changed', _v)
            self.modified()

    def hide(self):
        """Mark the entity invisible.

hide()
        """
        Entity.setVisibility(self, False)

    def show(self):
        """Mark the entity as visible.

show()
        """
        Entity.setVisibility(self, True)

    def expose(self):
        """Mark the entity as visible.

expose()

This method is identical to show().
        """
        Entity.setVisibility(self, True)

    def canParent(self, obj):
        """Test if an Entity can be the parent of another Entity.

canParent(obj)

Subclasses should override this method if the ability to be
the parent of another entity needs refinement.
        """
        return True

    def setParent(self, parent):
        """Store the parent of the entity.

setParent(parent)

Argument 'parent' must be another entity, and the parent
entity is tested to ensure that it can have children entities.
        """
        if parent is not None:
            if not isinstance(parent, Entity):
                raise TypeError, "Unexpected parent type: " + `type(parent)`
            if not parent.canParent(self):
                raise ValueError, "Invalid parent for Entity: " + `parent`
        _oldparent = self.__parent
        if _oldparent is not parent:
            if _oldparent is not None:
                Entity.__delChild(_oldparent, self)
            self.__parent = parent
            if parent is not None:
                Entity.__addChild(parent, self)
            #
            # fixme - re-examine sending (or not) the 'parent_changed'
            # and 'modified' messages when this method is invoked as this
            # method invocation is often called as part of an add/delete
            # operation that and as such can be thought of as a "side-effect"
            #
            # self.sendMessage('parent_changed', _oldparent)
            # self.modified()

    def getParent(self):
        """Return the parent entity of an entity.

getParent()

This method returns an Entity instance, or None of no
parent has been set.
        """
        return self.__parent

    parent = property(getParent, setParent, None, "Parent of an Entity.")

    def __addChild(self, child):
        """Take an entity as a child.

addChild(child)

This method is private to the Entity class.
        """
        if not isinstance(child, Entity):
            raise TypeError, "Unexpected child type: " + `type(child)`
        if child.getParent() is not self:
            raise ValueError, "Invalid parent: " + `child`
        if self.__children is None:
            self.__children = {}
        _cid = id(child)
        if _cid in self.__children:
            raise ValueError, "Child entity already stored: " + `child`
        self.__children[_cid] = child
        self.sendMessage('added_child', child)
        self.modified()

    def __delChild(self, child):
        """Remove an entity as a child.

delChild(child)

This method is private to the Entity class.
        """
        if child.getParent() is not self:
            raise ValueError, "Invalid parent for child: " + `child`
        if self.__children is None:
            raise ValueError, "Entity has no children: " + `self`
        _cid = id(child)
        if _cid not in self.__children:
            raise ValueError, "Child entity not stored: " + `child`
        del self.__children[_cid]
        if len(self.__children) == 0:
            self.__children = None
        self.sendMessage('removed_child', child)
        self.modified()

    def hasChild(self, child):
        """Test if an entity is a stored as a child.

hasChild(child)
        """
        return self.__children is not None and id(child) in self.__children

    def hasChildren(self):
        """Test if an entity has children entities.

hasChildren()

This method returns a boolean.
        """
        return self.__children is not None

    def getChildren(self):
        """Return any children entities of an entity.

getChildren()

This method returns a list of children entities.
        """
        if self.__children is not None:
            return self.__children.values()
        return []

    def sendsMessage(self, m):
        """Test if an entity can send a type of message.

sendsMessage(m)

Argument 'm' should be a string giving the message name.
This method returns a boolean.
        """
        if m in Entity.__messages:
            return True
        return super(Entity, self).sendsMessage(m)

    def clone(self):
        """Return an identical copy of an entity.

clone()
        """
        return Entity(parent=self.__parent)

    def inRegion(self, xmin, ymin, xmax, ymax, all=False):
        """Test if an entity is found in a spatial region.

inRegion(xmin, ymin, xmax, ymax[, all])

Arguments 'xmin', 'ymin', 'xmax', and 'ymax' should all be
floats. Argument 'all' is a boolean, with the default set
to False. If 'all' is true, then the entire entity must
lie within the boundary.
        """
        return False

    def getLog(self):
        """Return the history log for an entity.

getLog()

This method returns a Logger instance, or None if no log
has been assigned to the entity.
        """
        return self.__log

    def setLog(self, log):
        """Assign a Logger instance to an entity.

setLog(log)

Argument 'log' should be a Logger instance, or None.
        """
        if log is not None:
            if not isinstance(log, logger.Logger):
                raise TypeError, "Unexpected log type: " + `type(log)`
            if self.__log is not None:
                raise ValueError, "Entity already contains a log."
        self.__log = log

    def delLog(self):
        """Remove a Logger instance from an entity.

delLog()
        """
        if self.__log is not None:
            self.__log.clear()
        self.__log = None

    def undo(self):
        """Undo an action.

undo()

Using undo() requires a Logger instance to be assigned to the entity.
        """
        if self.__log is not None:
            self.__log.undo()

    def startUndo(self, mute=False):
        """Store an indication that an undo operation is commencing.

startUndo([mute])

Optional argument 'mute' must be a boolean. By default it is False, and
when True the entity will be muted during the undo operation.
        """
        _state = self.__undoing
        if _state != 0:
            if _state == -1:
                raise RuntimeError, "Object in redo state: " + `self`
            elif _state == 1:
                raise RuntimeError, "Object already in undo state: " + `self`
            else:
                raise ValueError, "Unexpected undo/redo state: %d" % _state
        if mute and False:
            self.mute()
        self.__undoing = 1

    def endUndo(self):
        """Set the entity to the state of undo operation completion.

endUndo()
        """
        _state = self.__undoing
        if _state != 1:
            if _state == -1:
                raise RuntimeError, "Object in redo state: " + `self`
            elif _state == 0:
                raise RuntimeError, "Object not in undo state: " + `self`
            else:
                raise ValueError, "Unexpected undo/redo state: %d" % _state
        self.__undoing = 0

    def inUndo(self):
        """Test if the entity is currently in an undo operation.

inUndo()

This method returns a boolean.
        """
        return self.__undoing == 1

    def redo(self):
        """Redo an action.

redo()

Using redo() requires a Logger instance to be assigned to the entity.
        """
        if self.__log is not None:
            self.__log.redo()

    def startRedo(self):
        """Store an indication that an redo operation is commencing.

startRedo()

        """
        _state = self.__undoing
        if _state != 0:
            if _state == 1:
                raise RuntimeError, "Object in undo state: " + `self`
            elif _state == -1:
                raise RuntimeError, "Object already in redo state: " + `self`
            else:
                raise ValueError, "Unexpected undo/redo state: %d" % _state
        self.__undoing = -1

    def endRedo(self):
        """Set the entity to the state of redo operation completion.

endRedo()
        """
        _state = self.__undoing
        if _state != -1:
            if _state == 1:
                raise RuntimeError, "Object in undo state: " + `self`
            elif _state == 0:
                raise RuntimeError, "Object not in redo state: " + `self`
            else:
                raise ValueError, "Unexpected undo/redo state: %d" % _state
        self.__undoing = 0

    def inRedo(self):
        """Test if the entity is currently in a redo operation.

inRedo()

This method returns a boolean.
        """
        return self.__undoing == -1

#
# Entity history class
#

class EntityLog(logger.Logger):
    def __init__(self, obj):
        if not isinstance(obj, Entity):
            raise TypeError, "Unexpected entity type: " + `type(obj)`
        super(EntityLog, self).__init__()
        self.__obj = obj
        obj.connect('visibility_changed', self.__visibilityChanged)
        obj.connect('lock_changed', self.__lockChanged)
        # obj.connect('parent_changed', self.__parentChanged)

    def detatch(self):
        self.__obj.disconnect(self)
        self.__obj = None

    def getObject(self):
        """Return the object stored in the log.

getEntity()        
        """
        return self.__obj
    
    def __visibilityChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _vis = args[0]
        util.test_boolean(_vis)
        self.saveUndoData('visibilty_changed', _vis)

    def __lockChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _lock = args[0]
        util.test_boolean(_lock)
        self.saveUndoData('lock_changed', _lock)
        
    def __parentChanged(self, obj, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _parent = args[0]
        if _parent is not None and not isinstance(_parent, Entity):
            raise TypeError, "Unexpected parent type: " + `type(_parent)`
        _pid = None
        if _parent is not None:
            _pid = _parent.getID()
        self.saveUndoData('parent_changed', _pid)

    def execute(self, undo, *args):
        # print "EntityLog::execute() ..."
        # print args
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _obj = self.__obj
        _op = args[0]
        if _op == 'visibility_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _obj.getVisibility()
            self.ignore(_op)
            try:
                _vis = args[1]
                if undo:
                    _obj.startUndo()
                    try:
                        _obj.setVisibility(_vis)
                    finally:
                        _obj.endUndo()
                else:
                    _obj.startRedo()
                    try:
                        _obj.setVisibility(_vis)
                    finally:
                        _obj.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'lock_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _obj.isLocked()
            self.ignore(_op)
            try:
                _lock = args[1]
                if undo:
                    _obj.startUndo()
                    try:
                        _obj.setLock(_lock)
                    finally:
                        _obj.endUndo()
                else:
                    _obj.startRedo()
                    try:
                        _obj.setLock(_lock)
                    finally:
                        _obj.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            raise ValueError, "Unexpected operation: %s" % _op

    def saveData(self, undo, op, *args):
        util.test_boolean(undo)
        if undo:
            self.saveRedoData(op, *args)
        else:
            self.saveUndoData(op, *args)

#
# property storage class
#

class EntityData(object):
    def __init__(self):
        self.__values = {}
        self.__locked = False

    def keys(self):
        return self.__values.keys()

    def values(self):
        return self.__values.values()

    def lock(self):
        self.__locked = True

    def unlock(self):
        self.__locked = False

    def isLocked(self):
        return self.__locked is True

    def setValue(self, key, value):
        if self.__locked:
            raise RuntimeError, "EntityData instance is locked: " + `self`
        if not isinstance(key, types.StringTypes):
            raise TypeError, "Invalid key type: " + `type(key)`
        if not EntityData._testValueType(self, value):
            raise TypeError, "Invalid value type: " + `type(value)`
        self.__values[key] = value

    def _testValueType(self, value):
        _pass = isinstance(value, (types.StringTypes, types.NoneType, int, float, EntityData))
        if not _pass:
            if isinstance(value, (tuple, list)):
                for _v in value:
                    _pass = EntityData._testValueType(self, _v)
                    if not _pass:
                        break
            elif isinstance(value, dict):
                for _k, _v in value.items():
                    _pass = isinstance(_k, types.StringTypes)
                    if not _pass:
                        break
                    _pass = EntityData._testValueType(self, _v)
                    if not _pass:
                        break
            else:
                _pass = False
        return _pass

    def getValue(self, key):
        return self.__values[key]

    def get(self, key):
        return self.__values.get(key)
