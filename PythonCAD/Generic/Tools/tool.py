#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
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
# tool stuff
#

import math
import types
import array

from PythonCAD.Generic import util
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic import dimension
from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic import tangent
from PythonCAD.Generic import intersections 
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import pyGeoLib 
from PythonCAD.Generic.snap import SnapPointStr

from PythonCAD.Generic import error


class Tool(object):
    """
    A generic tool object.

    This class is meant to be a base class for tools.
    A Tool instance the following attributes:

    list: A list the tool can use to store objects
    handlers: A dictionary used to store functions

    A Tool object has the following methods:

    {set/get/del/has}Handler(): Store/retrive/delete/test a handler for an event.
    clearHandlers(): Unset all the handlers in the tool.
    reset(): Restore the tool to a a default state.
    initialize(): Retore the tool to its original state.
    {set/get}Filter(): Set/Get a filtering procedure for object testing.
    {set/get}Location(): Store/retrieve an image-based coordinate pair.
    {set/get}CurrentPoint(): Store/retrieve a screen-based coordinate pair.
    clearCurrentPoint(): Set the screen-based coordinate to None.
    create(): Instantiate the object the tool is designed to create.
    """
    #---------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Instantiate a Tool.
        t = Tool()
        """
        super(Tool, self).__init__()
        self.__objlist = []
        self.__objtype = None
        self.__fproc = None
        self.__handlers = {}
        self.__location = None
        self.__curpoint = None
        self.__points = []
        self.__xpts = array.array('d')
        self.__ypts = array.array('d')
        self.__shift = None
        self.__SnapObj=None

    #---------------------------------------------------------------------------------------------------------
    def __len__(self):
        """Return the number of objects in the list via len().
        """
        return len(self.__objlist)

    #---------------------------------------------------------------------------------------------------------
    def __iter__(self):
        """Make the Tool iterable.
        """
        return iter(self.__objlist)

    #---------------------------------------------------------------------------------------------------------
    def getList(self):
        """Return the Tool's object list.

getList()
        """
        return self.__objlist

    list = property(getList, None, None, "Tool object list.")

    #---------------------------------------------------------------------------------------------------------
    def reset(self):
        """Restore the Tool to its initial state.

reset()

This function purges the Tool's object list and handler dictionary.
        """
        del self.__objlist[:]
        self.__handlers.clear()
        self.__location = None
        self.__curpoint = None
        del self.__points[:]
        del self.__xpts[:]
        del self.__ypts[:]
        self.__shift = None

    #---------------------------------------------------------------------------------------------------------
    def initialize(self):
        self.reset()

    #---------------------------------------------------------------------------------------------------------
    def setHandler(self, key, func):
        """
            Set a handler for the Tool.
            There are two arguments for this function:
            key: A string used to identify a particular action
            func: A function object
            There are no restrictions on what the function 'func' does,
            the argument count, etc. Any call to setHandler() with
            a key that is already stored replaces the old 'func' argument
            with the new one. The function argument may be None, and
            the key argument must be a string.
        """
        if key is None:
            raise ValueError, "Key value cannot be None."
        if not isinstance(key, str):
            raise TypeError, "Invalid key type: " + `type(key)`
        if func and not isinstance(func, types.FunctionType):
            raise TypeError, "Invalid function type: " + `type(func)`
        self.__handlers[key] = func

    #---------------------------------------------------------------------------------------------------------
    def getHandler(self, key):
        """
            Return the function for a particular key.
            Given argument 'key', the function associated with it is
            returned. A KeyError is raised if the argument 'key' had
            not be used to store a function.
        """
        if not isinstance(key, str):
            raise TypeError, "Invalid key type: " + `type(key)`
        if not self.__handlers.has_key(key):
            raise KeyError, "Invalid key '%s'" % key
        return self.__handlers[key]

    #---------------------------------------------------------------------------------------------------------    
    def delHandler(self, key):
        """Delete the handler associated with a particular key

delHandler(key)

The argument 'key' should be a string.
        """
        if self.__handlers.has_key(key):
            del self.__handlers[key]

    #---------------------------------------------------------------------------------------------------------
    def hasHandler(self, key):
        """Check if there is a handler stored for a given key.

hasHandler(key)

The 'key' argument must be a string. The function returns 1
if there is a handler for that key, 0 otherwise.
        """
        _k = key
        if not isinstance(_k, str):
            raise TypeError, "Invalid key type: " + `type(key)`
        return self.__handlers.has_key(_k)

    #---------------------------------------------------------------------------------------------------------
    def clearHandlers(self):
        """Unset all the handlers for the tool.

clearHandlers()

This function does not alter the Tool's object list.
        """
        self.__handlers.clear()

    #---------------------------------------------------------------------------------------------------------    
    def setObjtype(self, objtype):
        """Store the type of objects on which the tool operates.

setObjtype(objtype)

Argument 'objtype' can be a single type, a tuple of types, or 'None'.
        """
        if not isinstance(objtype, (tuple, types.NoneType, types.TypeType)):
            raise TypeError, "Invalid objtype: " + `type(objtype)`
        if objtype is not None:
            if isinstance(objtype, tuple):
                for _obj in objtype:
                    if not isinstance(_obj, types.TypeType):
                        raise TypeError, "Invalid objtype: " + `type(_obj)`
        self.__objtype = objtype

    #---------------------------------------------------------------------------------------------------------
    def getObjtype(self):
        """Return the type of object on which the tool operates.

getObjtype()

This method returns the value set in a setObjtype(), or None if
no object types have been specified.
        """
        return self.__objtype

    #---------------------------------------------------------------------------------------------------------
    def setFilter(self, proc):
        """Store a procedure used to examine selected objects.

setFilter(proc)

Argument 'proc' must be a callable procedure.
        """
        if not callable(proc):
            raise TypeError, "Invalid filter procedure: " + `type(proc)`
        self.__fproc = proc

    #---------------------------------------------------------------------------------------------------------
    def getFilter(self):
        """Return a stored procedure.

getFilter()

This method returns the procedure stored vai setFilter() or None.
        """
        return self.__fproc

    #---------------------------------------------------------------------------------------------------------
    def pushObject(self, obj):
        """Add an object to the Tool's object list.

pushObject(obj)
        """
        self.__objlist.append(obj)

    #---------------------------------------------------------------------------------------------------------
    def popObject(self):
        """Remove the last object on the Tool's object list.

popObject()

If the object list is empty, this function returns None.
        """
        _obj = None
        if len(self.__objlist):
            _obj = self.__objlist.pop()
        return _obj

    #---------------------------------------------------------------------------------------------------------    
    def delObjects(self):
        """Remove all objects from the Tool's object list.

delObjects()

This function does not alter the Tool's handlers.
        """
        del self.__objlist[:]

    #---------------------------------------------------------------------------------------------------------
    def getObject(self, idx):
        """Access an object in the tool.

getObject(idx)

The argument 'idx' is the index into the list of
stored objects.
        """
        return self.__objlist[idx]

    #---------------------------------------------------------------------------------------------------------
    def setLocation(self, x, y):
        """
        Store an x/y location in the tool.

        Store an x-y coordinate in the tool. Both arguments
        should be floats
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__location = (_x,_y)

    #---------------------------------------------------------------------------------------------------------
    def setLocation(self, point):
        """
        Store an point location in the tool.

        point is of type Point
        """
        self.__location = point

        #---------------------------------------------------------------------------------------------------------    
    def getLocation(self):
        """
        Return the stored location in the tool
        getLocation()
        """
        return self.__location

    #---------------------------------------------------------------------------------------------------------
    def clearLocation(self):
        """
        Reset the location to an empty value.
        """
        self.__location = None

    #---------------------------------------------------------------------------------------------------------
    def setCurrentPoint(self, point):
        """
        Set the tool's current point.
        Store an point object in the tool.
        Argument should not be None.
        """
        if point is not None and isinstance(point, Point):
            self.__curpoint = point

    #---------------------------------------------------------------------------------------------------------
    def getCurrentPoint(self):
        """
        Return the tool's current point value.
        """
        return self.__curpoint

    #---------------------------------------------------------------------------------------------------------
    def clearCurrentPoint(self):
        """
        Reset the current point to an empty value
        """
        self.__curpoint = None

    #---------------------------------------------------------------------------------------------------------
    def create(self, image):
        """
        Create an object the tool is designed to construct.
        The argument 'image' is an image in which the newly created object
        will be added. In the Tool class, this method does nothing. It is
        meant to be overriden in classed using the Tool class as a base
        class.
        """
        pass # override

