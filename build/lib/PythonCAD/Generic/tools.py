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

class Tool(object):
    """A generic tool object.

This class is meant to be a base class for tools. A Tool
instance the following attributes:

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
    def __init__(self):
        """Instantiate a Tool.

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

    def __len__(self):
        """Return the number of objects in the list via len().
        """
        return len(self.__objlist)

    def __iter__(self):
        """Make the Tool iterable.
        """
        return iter(self.__objlist)

    def getList(self):
        """Return the Tool's object list.

getList()
        """
        return self.__objlist

    list = property(getList, None, None, "Tool object list.")

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

    def initialize(self):
        self.reset()

    def setHandler(self, key, func):
        """Set a handler for the Tool.

setHandler(key, func)

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

    def getHandler(self, key):
        """Return the function for a particular key.

getHandler(key)

Given argument 'key', the function associated with it is
returned. A KeyError is raised if the argument 'key' had
not be used to store a function.
        """
        if not isinstance(key, str):
            raise TypeError, "Invalid key type: " + `type(key)`
        if not self.__handlers.has_key(key):
            raise KeyError, "Invalid key '%s'" % key
        return self.__handlers[key]

    def delHandler(self, key):
        """Delete the handler associated with a particular key

delHandler(key)

The argument 'key' should be a string.
        """
        if self.__handlers.has_key(key):
            del self.__handlers[key]

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

    def clearHandlers(self):
        """Unset all the handlers for the tool.

clearHandlers()

This function does not alter the Tool's object list.
        """
        self.__handlers.clear()

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

    def getObjtype(self):
        """Return the type of object on which the tool operates.

getObjtype()

This method returns the value set in a setObjtype(), or None if
no object types have been specified.
        """
        return self.__objtype

    def setFilter(self, proc):
        """Store a procedure used to examine selected objects.

setFilter(proc)

Argument 'proc' must be a callable procedure.
        """
        if not callable(proc):
            raise TypeError, "Invalid filter procedure: " + `type(proc)`
        self.__fproc = proc

    def getFilter(self):
        """Return a stored procedure.

getFilter()

This method returns the procedure stored vai setFilter() or None.
        """
        return self.__fproc
    
    def pushObject(self, obj):
        """Add an object to the Tool's object list.

pushObject(obj)
        """
        self.__objlist.append(obj)

    def popObject(self):
        """Remove the last object on the Tool's object list.

popObject()

If the object list is empty, this function returns None.
        """
        _obj = None
        if len(self.__objlist):
            _obj = self.__objlist.pop()
        return _obj

    def delObjects(self):
        """Remove all objects from the Tool's object list.

delObjects()

This function does not alter the Tool's handlers.
        """
        del self.__objlist[:]

    def getObject(self, idx):
        """Access an object in the tool.

getObject(idx)

The argument 'idx' is the index into the list of
stored objects.
        """
        return self.__objlist[idx]

    def setLocation(self, x, y):
        """Store an x/y location in the tool.

setLocation(x,y)

Store an x-y coordinate in the tool. Both arguments
should be floats
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__location = (_x,_y)

    def getLocation(self):
        """Return the stored location in the tool

getLocation()
        """
        return self.__location

    def clearLocation(self):
        """Reset the location to an empty value.

clearLocation()
        """
        self.__location = None

    def setCurrentPoint(self, x, y):
        """Set the tool's current point.

setCurrentPoint(x,y)

Store an x-y coordinate in the tool. Both arguments
should be int.
        """
        _x = x
        if not isinstance(_x, int):
            _x = int(x)
        _y = y
        if not isinstance(_y, int):
            _y = int(y)
        self.__curpoint = (_x, _y)

    def getCurrentPoint(self):
        """Return the tool's current point value.

getCurrentPoint()
        """
        return self.__curpoint

    def clearCurrentPoint(self):
        """Reset the current point to an empty value

clearCurrentPoint()
        """
        self.__curpoint = None

    def create(self, image):
        """Create an object the tool is designed to construct.

create(image)

The argument 'image' is an image in which the newly created object
will be added. In the Tool class, this method does nothing. It is
meant to be overriden in classed using the Tool class as a base
class.
        """
        pass # override

#
# The ZoomTool, PasteTool, SelectTool, and DeselectTool classes are
# subclasses of the Tool class but with no additional functionality (yet)
class ZoomPan(Tool):
    pass
class ZoomTool(Tool):
    pass

class PasteTool(Tool):
    pass

class SelectTool(Tool):
    pass

class DeselectTool(Tool):
    pass

class PointTool(Tool):
    """A specialized tool for drawing Point objects.

The PointTool class is derived from the Tool class, so it
shares the methods and attributes of that class. The PointTool
class has the following additional methods:

{get/set}Point(): Get/Set a x/y coordinate in the tool.
    """
    def __init__(self):
        super(PointTool, self).__init__()
        self.__point = None

    def setPoint(self, x, y):
        """Store an x/y coordinate in the tool

setPoint(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__point = (_x, _y)

    def getPoint(self):
        """Get the stored x/y coordinates from the tool.

getPoint()

This method returns a tuple containing the values passed in
with the setPoint() method, or None if that method has not
been invoked.
        """
        return self.__point

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(PointTool, self).reset()
        self.__point = None

    def create(self, image):
        """Create a new Point and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if self.__point is not None:
            _active_layer = image.getActiveLayer()
            _x, _y = self.__point
            _p = Point(_x, _y)
            _active_layer.addObject(_p)
            self.reset()

class SegmentTool(Tool):
    """A Specialized tool for drawing Segment objects.

The SegmentTool class is derived from the Tool class, so
it shares the attributes and methods of that class. The
SegmentTool class has the following additional methods:

{get/set}FirstPoint(): Get/Set the first point of the Segment.
{get/set}SecondPoint(): Get/Set the second point of the Segment.
    """
    def __init__(self):
        super(SegmentTool, self).__init__()
        self.__first_point = None
        self.__second_point = None

    def setFirstPoint(self, x, y):
        """Store the first point of the Segment.

setFirstPoint(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__first_point = (_x, _y)

    def getFirstPoint(self):
        """Get the first point of the Segment.

getFirstPoint()

This method returns a tuple holding the coordinates stored
by invoking the setFirstPoint() method, or None if that method
has not been invoked.
        """
        return self.__first_point

    def setSecondPoint(self, x, y):
        """Store the second point of the Segment.

setSecondPoint(x, y)

Arguments 'x' and 'y' should be floats. If the
tool has not had the first point set with setFirstPoint(),
a ValueError exception is raised.
        """
        if self.__first_point is None:
            raise ValueError, "SegmentTool first point is not set."
        print("x: %s y: %s"%(str(x),str(y)))
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__second_point = (_x, _y)

    def getSecondPoint(self):
        """Get the second point of the Segment.

getSecondPoint()

This method returns a tuple holding the coordinates stored
by invoking the setSecondPoint() method, or None if that method
has not been invoked.
        """
        return self.__second_point

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(SegmentTool, self).reset()
        self.__first_point = None
        self.__second_point = None

    def create(self, image):
        """Create a new Segment and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if (self.__first_point is not None and
            self.__second_point is not None):
            _active_layer = image.getActiveLayer()
            _x1, _y1 = self.__first_point
            _x2, _y2 = self.__second_point
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x2, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _seg = Segment(_p1, _p2, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _seg.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _seg.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _seg.setThickness(_t)
            _active_layer.addObject(_seg)
            self.reset()

class RectangleTool(SegmentTool):
    """A Specialized tool for drawing rectangles.

The RectangleTool is derived from the SegmentTool, so it
shares all the methods and attributes of that class. A
RectangleTool creates four Segments in the shape of
a rectangle in the image.
    """
    def __init__(self):
        super(RectangleTool, self).__init__()

    def create(self, image):
        """Create Segments and add them to the image.

create(image)

This method overrides the SegmentTool::create() method.
        """
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        if _p1 is not None and _p2 is not None:
            _x1, _y1 = _p1
            _x2, _y2 = _p2
            _active_layer = image.getActiveLayer()
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x1, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x1, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p3 = Point(_x2, _y2)
                _active_layer.addObject(_p3)
            else:
                _p3 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y1)
            if len(_pts) == 0:
                _p4 = Point(_x2, _y1)
                _active_layer.addObject(_p4)
            else:
                _p4 = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _l = image.getOption('LINE_TYPE')
            if _l == _s.getLinetype():
                _l = None
            _c = image.getOption('LINE_COLOR')
            if _c == _s.getColor():
                _c = None
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) < 1e-10:
                _t = None
            _seg = Segment(_p1, _p2, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            _seg = Segment(_p2, _p3, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            _seg = Segment(_p3, _p4, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            _seg = Segment(_p4, _p1, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            self.reset()

class CircleTool(Tool):
    """A Specialized tool for drawing Circle objects.

The CircleTool is derived from the Tool class, so it shares
all the methods and attributes of that class. The CircleTool
class has the following addtional methods:

{set/get}Center(): Set/Get the center point location of the circle.
{set/get}Radius(): Set/Get the radius of the circle.
    """
    def __init__(self):
        super(CircleTool, self).__init__()
        self.__center = None
        self.__radius = None

    def setCenter(self, x, y):
        """Set the center point location of the circle.

setCenter(x, y)

The arguments 'x' and 'y' give the location for the center
of the circle.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__center = (_x, _y)

    def getCenter(self):
        """Get the center point location of the circle.

getCenter()

This method returns the coordinates stored with the setCenter()
method, or None if that method has not been called.
        """
        return self.__center

    def setRadius(self, radius):
        """Set the radius of the circle.

setRadius(radius)

The argument 'radius' must be a float value greater than 0.0
        """
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        self.__radius = _r

    def getRadius(self):
        """Get the radius of the circle.

getRadius()

This method returns the value specified from the setRadius()
call, or None if that method has not been invoked.
        """
        return self.__radius

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(CircleTool, self).reset()
        self.__center = None
        self.__radius = None

    def create(self, image):
        """Create a new Circle and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if (self.__center is not None and
            self.__radius is not None):
            _active_layer = image.getActiveLayer()
            _x, _y = self.__center
            _r = self.__radius
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _cp = Point(_x, _y)
                _active_layer.addObject(_cp)
            else:
                _cp = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _circle = Circle(_cp, _r, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _circle.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _circle.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _circle.setThickness(_t)
            _active_layer.addObject(_circle)
            self.reset()

class TwoPointCircleTool(CircleTool):
    """A specialized class for drawing Circles between two points.

The TwoPointCircleTool class is derived from the CircleTool
class, so it shares all the methods and attributes of that
class. The TwoPointCircleTool class has the following addtional
methods:

{set/get}FirstPoint(): Set/Get the first point used to define the circle.
{set/get}SecondPoint(): Set/Get the second point used to define the circle.
    """
    def __init__(self):
        super(TwoPointCircleTool, self).__init__()
        self.__first_point = None
        self.__second_point = None

    def setFirstPoint(self, x, y):
        """Set the first point used to define the location of the circle.

setFirstPoint(x, y)

Arguments 'x' and 'y' give the location of a point.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__first_point = (_x, _y)

    def getFirstPoint(self):
        """Get the first point used to define the location of the circle.

getFirstPoint()

This method returns a tuple holding the values used when the
setFirstPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__first_point

    def setSecondPoint(self, x, y):
        """Set the second point used to define the location of the circle.

setSecondPoint(x, y)

Arguments 'x' and 'y' give the location of a point. Invoking
this method before the setFirstPoint() method will raise a
ValueError.
        """
        if self.__first_point is None:
            raise ValueError, "First point is not set"
        _x = util.get_float(x)
        _y = util.get_float(y)
        _x1, _y1 = self.__first_point
        _xc = (_x + _x1)/2.0
        _yc = (_y + _y1)/2.0
        _radius = math.hypot((_x - _x1), (_y - _y1))/2.0
        self.setCenter(_xc, _yc)
        self.setRadius(_radius)
        self.__second_point = (_x, _y)

    def getSecondPoint(self):
        """Get the second point used to define the location of the circle.

getSecondPoint()

This method returns a tuple holding the values used when the
setSecondPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__second_point

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends CircleTool::reset().
        """
        super(TwoPointCircleTool, self).reset()
        self.__first_point = None
        self.__second_point = None

class ArcTool(CircleTool):
    """A specialized tool for drawing Arc objects.

The ArcTool is Derived from the CircleTool class, so it shares
all the attributes and methods of that class. The ArcTool class
has the following addtional methods:

{set/get}StartAngle(): Set/Get the start angle of the arc
{set/get}EndAngle(): Set/Get the end angle of the arc.
    """
    def __init__(self):
        super(ArcTool, self).__init__()
        self.__start_angle = None
        self.__end_angle = None

    def setStartAngle(self, angle):
        """Set the start angle of the arc.

setStartAngle(angle)

The argument 'angle' should be a float value between 0.0 and 360.0
        """
        _angle = util.make_c_angle(angle)
        self.__start_angle = _angle

    def getStartAngle(self):
        """Return the start angle of the arc.

getStartAngle()

This method returns the value defined in the previous setStartAngle()
call, or None if that method has not been called.
        """
        return self.__start_angle

    def setEndAngle(self, angle):
        """Set the start angle of the arc.

setStartAngle(angle)

The argument 'angle' should be a float value between 0.0 and 360.0
        """
        _angle = util.make_c_angle(angle)
        self.__end_angle = _angle

    def getEndAngle(self):
        """Return the end angle of the arc.

getEndAngle()

This method returns the value defined in the previous setEndAngle()
call, or None if that method has not been called.
        """
        return self.__end_angle

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends CircleTool::reset().
        """
        super(ArcTool, self).reset()
        self.__start_angle = None
        self.__end_angle = None

    def create(self, image):
        """Create a new Arc and add it to the image.

create(image)

This method overrides the CircleTool::create() method.
        """
        _center = self.getCenter()
        _radius = self.getRadius()
        _sa = self.__start_angle
        _ea = self.__end_angle
        if (_center is not None and
            _radius is not None and
            _sa is not None and
            _ea is not None):
            _active_layer = image.getActiveLayer()
            _x, _y = _center
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _cp = Point(_x, _y)
                _active_layer.addObject(_cp)
            else:
                _cp = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _arc = Arc(_cp, _radius, _sa, _ea, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _arc.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _arc.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _arc.setThickness(_t)
            for _ep in _arc.getEndpoints():
                _ex, _ey = _ep
                _pts = _active_layer.find('point', _ex, _ey)
                if len(_pts) == 0:
                    _lp = Point(_ex, _ey)
                    _active_layer.addObject(_lp)
            _active_layer.addObject(_arc)
            self.reset()

#
# The ChamferTool and FilletTool class are subclasses of
# the Tool class but have no additional functionality (yet)
#

class ChamferTool(Tool):
    pass
        
class FilletTool(Tool):
    """
     A specifie tool for drawing Fillet used to manage radius imput
    """
    def __init__(self):
        super(FilletTool, self).__init__()
        self.__Radius=None
    def GetRadius(self):
        """
            get the fillet radius
        """
        return self.__Radius
    def SetRadius(self,rad):
        """
            set the fillet radius
        """
        self.__Radius=rad
        
    rad=property(GetRadius,SetRadius,None,"Get The Fillet Radius.")

class FilletTwoLineTool(FilletTool):
    """
        A specifie tool for drawing fillet using two segment
    """
    def __init__(self):
        super(FilletTwoLineTool, self).__init__()
        self.__FirstLine=None
        self.__SecondLine=None
        self.__SecondPoint=None
        self.__FirstPoint=None
        self.__TrimMode='b'
    def GetFirstLine(self):
        return self.__FirstLine
    def SetFirstLine(self,obj):
        if obj==None:
            raise "None Object"        
        if not isinstance(obj,Segment):
            raise "Invalid object Need Segment or CLine"
        self.__FirstLine=obj
    def GetSecondLine(self):
        return self.__SecondLine
    def SetSecondtLine(self,obj):
        if obj==None:
            raise "None Object"
        if not isinstance(obj,Segment):
            raise "Invalid object Need Segment or CLine"
        self.__SecondLine=obj            
    FirstLine=property(GetFirstLine,SetFirstLine,None,"Set first line object in the tool")
    SecondLine=property(GetSecondLine,SetSecondtLine,None,"Set second line object in the tool")
    def GetFirstPoint(self):
        """
            Return the first toolpoint
        """
        return self.__FirstPoint
    def SetFirstPoint(self,point):
        """
            Set the first toolpoint
        """
        if point==None:
            raise "None Object"
        if not isinstance(point,Point):
            raise "Invalid object Need Point"
        self.__FirstPoint=point
    def GetSecondPoint(self):
        """
            Return the second toolpoint
        """
        return self.__SecondPoint
    def SetSecondPoint(self,point):
        """
            Set the second toolpoint
        """
        if point==None:
            raise "None Object"
        if not isinstance(point,Point):
            raise "Invalid object Need Point"
        self.__SecondPoint=point
    FirstPoint=property(GetFirstPoint,SetFirstPoint,None,"First line object in the tool")
    SecondPoint=property(GetSecondPoint,SetSecondPoint,None,"Second line object in the tool")
    def SetTrimMode(self,mode):
        """
            set the trim mode
        """
        self.__TrimMode=mode
    def GetTrimMode(self):
        """
            get the trim mode
        """
        return self.__TrimMode
    TrimMode=property(GetTrimMode,SetTrimMode,None,"Trim Mode")
    
    def Create(self,image):
        """
            Create the Fillet
        """
        interPnt=[]
        if self.FirstLine != None and self.SecondLine != None :
            intersections._seg_seg_intersection(interPnt,self.__FirstLine,self.__SecondLine)
        else:
            if self.FirstLine==None:
                raise "tools.fillet.Create: First  obj is null"
            if self.SecondLine==None:
                raise "tools.fillet.Create: Second  obj is null"
        if(len(interPnt)):
            _active_layer = image.getActiveLayer() 
            _s = image.getOption('LINE_STYLE')
            _l = image.getOption('LINE_TYPE')
            _c = image.getOption('LINE_COLOR')
            _t = image.getOption('LINE_THICKNESS')
            p1,p2=self.FirstLine.getEndpoints() 
            p1=Point(p1.getCoords())           
            p2=Point(p2.getCoords())
            p11,p12=self.SecondLine.getEndpoints()  
            p11=Point(p11.getCoords())           
            p12=Point(p12.getCoords())          
            #
            interPoint1=Point(interPnt[0]) 
            _active_layer.addObject(interPoint1)    
            interPoint2=Point(interPnt[0]) 
            _active_layer.addObject(interPoint2)  
            # 
            # new function for calculating the new 2 points
            #
            self.setRightPoint(image,self.FirstLine,self.FirstPoint,interPoint1)                   
            self.setRightPoint(image,self.SecondLine,self.SecondPoint,interPoint2)
            _fillet=Fillet(self.FirstLine, self.SecondLine,self.rad, _s)
            if _l != _s.getLinetype():
                _fillet.setLinetype(_l)
            if _c != _s.getColor():
                _fillet.setColor(_c)
            if abs(_t - _s.getThickness()) > 1e-10:
                _fillet.setThickness(_t)             
            _active_layer.addObject(_fillet)    
            #
            # Adjust the lines
            #
            if self.TrimMode=='f' or self.TrimMode=='n': 
                image.delObject(self.SecondLine.p1)
                image.delObject(self.SecondLine.p2)               
                self.SecondLine.p1=p11
                self.SecondLine.p2=p12
                _active_layer.addObject(p11)
                _active_layer.addObject(p12)
            if self.TrimMode=='s' or self.TrimMode=='n':
                image.delObject(self.FirstLine.p1)
                image.delObject(self.FirstLine.p2)               
                self.FirstLine.p1=p1
                self.FirstLine.p2=p2       
                _active_layer.addObject(p1)
                _active_layer.addObject(p2)         
            
    def setRightPoint(self,image,objSegment,objPoint,objInterPoint):
        """
            Get the point used for the trim
        """
        _p1 , _p2 = objSegment.getEndpoints()            
        _x,_y = objPoint.getCoords()
        opjPoint=Point(objSegment.GetLineProjection(_x,_y))
        pickIntVect=pyGeoLib.Vector(objInterPoint,opjPoint).Mag()            
        p1IntVect=pyGeoLib.Vector(objInterPoint,_p1).Mag()            
        if(pickIntVect==p1IntVect):
            objSegment.p2=objInterPoint
            image.delObject(_p2)
            return
        p2IntVect=pyGeoLib.Vector(objInterPoint,_p2).Mag()
        if(pickIntVect==p2IntVect):
            objSegment.p1=objInterPoint
            image.delObject(_p1)
            return
        ldist=interPoint1.Dist(_p1)
        if(ldist<interPoint1.Dist_(p2)):
            self.FirstLine.p1=objInterPoint
            image.delObject(_p1)
        else:
            self.FirstLine.p2=objInterPoint
            image.delObject(_p2)
    
class LeaderTool(Tool):
    """A specialized tool for drawing Leader objects.

The LeaderTool class is derived from the Tool class, so it
shares the methods and attributes of that class. The LeaderTool
class has the following addtional methods:

{set/get}FirstPoint(): Set/Get the first point of the Leader.
{set/get}MidPoint(): Set/Get the second point of the Leader.
{set/get}FinalPoint(): Set/Get the final point of the Leader.
    """
    def __init__(self):
        super(LeaderTool, self).__init__()
        self.__start_point = None
        self.__mid_point = None
        self.__end_point = None

    def setFirstPoint(self, x, y):
        """Set the first point used to define the Leader.

setFirstPoint(x, y)

Arguments 'x' and 'y' give the location of a point.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__start_point = (_x, _y)

    def getFirstPoint(self):
        """Get the first point used to define the Leader.

getFirstPoint()

This method returns a tuple holding the values used when the
setFirstPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__start_point

    def setMidPoint(self, x, y):
        """Set the second point used to define the Leader.

setMidPoint(x, y)

Arguments 'x' and 'y' give the location of a point. If the
first point has not been set this method raises a ValueError.
        """
        if self.__start_point is None:
            raise ValueError, "First point not set in LeaderTool."
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__mid_point = (_x, _y)

    def getMidPoint(self):
        """Get the second point used to define the Leader.

getMidPoint()

This method returns a tuple holding the values used when the
setMidPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__mid_point

    def setFinalPoint(self, x, y):
        """Set the first point used to final point of the Leader.

setFinalPoint(x, y)

Arguments 'x' and 'y' give the location of a point. This method
raises an error if the first point or second point have not been
set.
        """
        if self.__start_point is None:
            raise ValueError, "First point not set in LeaderTool."
        if self.__mid_point is None:
            raise ValueError, "Second point not set in LeaderTool."
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__end_point = (_x, _y)

    def getFinalPoint(self):
        """Get the third point used to define the Leader.

getFinalPoint()

This method returns a tuple holding the values used when the
setFinalPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__end_point

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(LeaderTool, self).reset()
        self.__start_point = None
        self.__mid_point = None
        self.__end_point = None

    def create(self, image):
        """Create a new Leader and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if (self.__start_point is not None and
            self.__mid_point is not None and
            self.__end_point is not None):
            _active_layer = image.getActiveLayer()
            _x1, _y1 = self.__start_point
            _x2, _y2 = self.__mid_point
            _x3, _y3 = self.__end_point
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x2, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _pts = _active_layer.find('point', _x3, _y3)
            if len(_pts) == 0:
                _p3 = Point(_x3, _y3)
                _active_layer.addObject(_p3)
            else:
                _p3 = _pts[0]
            _size = image.getOption('LEADER_ARROW_SIZE')
            _s = image.getOption('LINE_STYLE')
            _leader = Leader(_p1, _p2, _p3, _size, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _leader.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _leader.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _leader.setThickness(_t)
            _active_layer.addObject(_leader)
            self.reset()

class PolylineTool(Tool):
    """A specialized tool for drawing Polyline objects.

The PolylineTool class is derived from the Tool class, so it
shares all the attributes and methods of that class. The PolylineTool
class has the following addtional methods:

storePoint(): Store a point used to define the Polyline.
getPoint(): Retrieve a point used to define the Polyline.
getLastPoint(): Retrieve the last point used to define the Polyline.
getPoints(): Get the list of points that define the Polyline.
    """
    def __init__(self):
        super(PolylineTool, self).__init__()
        self.__points = []

    def __len__(self):
        return len(self.__points)

    def storePoint(self, x, y):
        """Store a point that will define a Polyline.

storePoint(x, y)

The arguments 'x' and 'y' should be float values. There is
no limit as to how long a Polyline should be, so each invocation
of this method appends the values to the list of stored points.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__points.append((_x, _y))

    def getPoint(self, i):
        """Retrieve a point used to define a Polyline.

getPoint(i)

Argument 'i' represents the index in the list of points that
defines the polyline. Negative indicies will get points from
last-to-first. Using an invalid index will raise an error.

This method returns a tuple holding the x/y coordinates.
        """
        return self.__points[i]

    def getPoints(self):
        """Get all the points that define the Polyline.

getPoints()

This method returns a list of tuples holding the x/y coordinates
of all the points that define the Polyline.
        """
        return self.__points[:]

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(PolylineTool, self).reset()
        del self.__points[:]

    def create(self, image):
        """Create a new Polyline and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if len(self.__points):
            _pts = []
            _active_layer = image.getActiveLayer()
            for _pt in self.__points:
                _x, _y = _pt
                _lpts = _active_layer.find('point', _x, _y)
                if len(_lpts) == 0:
                    _p = Point(_x, _y)
                    _active_layer.addObject(_p)
                    _pts.append(_p)
                else:
                    _pts.append(_lpts[0])
            _s = image.getOption('LINE_STYLE')
            _pline = Polyline(_pts, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _pline.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _pline.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _pline.setThickness(_t)
            _active_layer.addObject(_pline)
            self.reset()

class PolygonTool(Tool):
    """A specialized to for creating Polygons from Segments.

The PolygonTool will create an uniformly sized polygon from Segment
entities. The minimum number of sides is three, creating an equilateral
triangle. There is no maximum number of sides, though realistically any
polygon with more than 20 or so sides is unlikely to be drawn. As
the PolygonTool is derived from the Tool class, it shares all the attributes
and method of that class. The PolygonTool has the following additional
methods:

{get/set}SideCount(): Get/Set the number of sides in the polygon.
{get/set}External() Get/Set if the polygon is drawn inside or outside a circle.
{get/set}Center(): Get/Set the center location of the polygon.
getCoords(): Get the coordinates of the polygon corners.
    """
    def __init__(self):
        super(PolygonTool, self).__init__()
        self.__nsides = None
        self.__increment = None
        self.__external = False
        self.__center = None
        self.__xpts = array.array("d")
        self.__ypts = array.array("d")

    def setSideCount(self, count):
        """Set the number of sides of the polygon to create.

setSideCount(count)

Argument "count" should be an integer value greater than 2.
        """
        _count = count
        if not isinstance(_count, int):
            _count = int(count)
        if _count < 3:
            raise ValueError, "Invalid count: %d" % _count
        self.__nsides = _count
        self.__increment = (360.0/float(_count)) * (math.pi/180.0)
        for _i in range(_count):
            self.__xpts.insert(_i, 0.0)
            self.__ypts.insert(_i, 0.0)

    def getSideCount(self):
        """Get the number of sides of the polygon to be created.

getSideCount()

A ValueError exception is raised if the side count has not been
set with setSideCount()
        """
        if self.__nsides is None:
            raise ValueError, "No side count defined."
        return self.__nsides

    def setExternal(self):
        """Create the polygon on the outside of a reference circle.

setExternal()

By default the polygon is drawing completely contained within a
circle. Invoking this method will created the polygon so that all
sides are outside the circle.
        """
        self.__external = True

    def getExternal(self):
        """Test if the polygon will be created outside a circle.

getExternal()

If the setExternal() method has been called, this method will
return True. By default this method will return False.
        """
        return self.__external

    def setCenter(self, x, y):
        """Define the center of the polygon.

setCenter(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__center = (_x, _y)

    def getCenter(self):
        """Retrieve the center of the polygon to be created.

getCenter()

This method returns a tuple holding two float values containing
the 'x' and 'y' coordinates of the polygon center. A ValueError
is raised if the center has not been set with a prior call to setCenter().
        """
        if self.__center is None:
            raise ValueError, "Center is undefined."
        return self.__center

    def getCoord(self, i):
        """Get one of the coordinates of the polygon corners.

getCoord(i)

Argument "i" should be an integer value such that:

0 <= i <= number of polygon sides
        """
        _x = self.__xpts[i]
        _y = self.__ypts[i]
        return _x, _y

    def setLocation(self, x, y):
        """Set the tool location.

setLocation(x, y)

This method extends Tool::setLocation() and calculates the polygon
points.
        """
        super(PolygonTool, self).setLocation(x, y)
        _x, _y = self.getLocation()
        _count = self.__nsides
        _inc = self.__increment
        if self.__external:
            _offset = _inc/2.0
        else:
            _offset = 0.0
        _cx, _cy = self.__center
        _xsep = _x - _cx
        _ysep = _y - _cy
        _angle = math.atan2(_ysep, _xsep) + _offset
        _rad = math.hypot(_xsep, _ysep)/math.cos(_offset)
        _xp = self.__xpts
        _yp = self.__ypts
        for _i in range(_count):
            _xp[_i] = _cx + (_rad * math.cos(_angle))
            _yp[_i] = _cy + (_rad * math.sin(_angle))
            _angle = _angle + _inc

    def create(self, image):
        """Create a Polygon from Segments and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if len(self.__xpts):
            _active_layer = image.getActiveLayer()
            _s = image.getOption('LINE_STYLE')
            _l = image.getOption('LINE_TYPE')
            if _l == _s.getLinetype():
                _l = None
            _c = image.getOption('LINE_COLOR')
            if _c == _s.getColor():
                _c = None
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) < 1e-10:
                _t = None
            _count = self.__nsides
            _xp = self.__xpts
            _yp = self.__ypts
            _x = _xp[0]
            _y = _yp[0]
            #
            # find starting point ...
            #
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _p0 = Point(_x, _y)
                _active_layer.addObject(_p0)
            else:
                _p0 = _pts[0]
            #
            # make segments for all the points ...
            #
            _p1 = _p0
            for _i in range(1, _count):
                _x = _xp[_i]
                _y = _yp[_i]
                _pts = _active_layer.find('point', _x, _y)
                if len(_pts) == 0:
                    _pi = Point(_x, _y)
                    _active_layer.addObject(_pi)
                else:
                    _pi = _pts[0]
                _seg = Segment(_p1, _pi, _s, linetype=_l, color=_c, thickness=_t)
                _active_layer.addObject(_seg)
                _p1 = _pi
            #
            # now add closing segment ...
            #
            _seg = Segment(_p1, _p0, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            self.reset()

    def reset(self):
        """Restore the PolygonTool to its original state.

reset()

This method extends Tool::reset()
        """
        super(PolygonTool, self).reset()
        # self.__nsides = None
        # self.__increment = None
        # self.__external = False # make this adjustable?
        self.__center = None
        for _i in range(self.__nsides):
            self.__xpts[_i] = 0.0
            self.__ypts[_i] = 0.0

class HCLineTool(PointTool):
    """A specialized tool for drawing HCLine objects.

The HCLineTool class is derived from the PointTool class
so it shares all the attributes and methods of that class.

There are no additional methods for this class.
    """
    def __init__(self):
        super(HCLineTool, self).__init__()

    def create(self, image):
        """Create a new HCLine and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _p = self.getPoint()
        if _p is not None:
            _active_layer = image.getActiveLayer()
            _x, _y = _p
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _pt = Point(_x, _y)
                _active_layer.addObject(_pt)
            else:
                _pt = _pts[0]
            _hcl = HCLine(_pt)
            _active_layer.addObject(_hcl)
            self.reset()

class VCLineTool(PointTool):
    """A specialized tool for drawing VCLine objects.

The VCLineTool class is derived from the PointTool class
so it shares all the attributes and methods of that class.

There are no additional methods for this class.
    """
    def __init__(self):
        super(VCLineTool, self).__init__()

    def create(self, image):
        """Create a new VCLine and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _p = self.getPoint()
        if _p is not None:
            _active_layer = image.getActiveLayer()
            _x, _y = _p
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _pt = Point(_x, _y)
                _active_layer.addObject(_pt)
            else:
                _pt = _pts[0]
            _vcl = VCLine(_pt)
            _active_layer.addObject(_vcl)
            self.reset()

class ACLineTool(PointTool):
    """A specialized tool for drawing ACLine objects.

The ACLineTool class is derived from the PointTool class
so it shares all the attributes and methods of that class.
The ACLineTool class has the following addtional methods:

{set/get}Angle(): Set/Get the angle of the ACLine.
    """
    def __init__(self):
        super(ACLineTool, self).__init__()
        self.__angle = None

    def setLocation(self, x, y):
        """Set the location of the Tool.

setLocation(x, y)

This method extends the Tool::setLocation() method.
        """
        super(ACLineTool, self).setLocation(x, y)
        _loc = self.getLocation()
        if _loc is None:
            return
        _x, _y = _loc
        _x1, _y1 = self.getPoint()
        if abs(_y - _y1) < 1e-10: # horizontal
            self.__angle = 0.0
        elif abs(_x - _x1) < 1e-10: # vertical
            self.__angle = 90.0
        else:
            _slope = 180.0/math.pi * math.atan2((_y - _y1), (_x - _x1))
            self.__angle = util.make_angle(_slope)

    def setAngle(self, angle):
        """Set the angle for the ACLine.

setAngle(angle)

The argument 'angle' should be a float where -90.0 < angle < 90.0
        """
        _angle = util.make_angle(angle)
        self.__angle = _angle

    def getAngle(self):
        """Get the angle for the ACLine.

getAngle()

This method returns a float.
        """
        return self.__angle

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends PointTool::reset().
        """
        super(ACLineTool, self).reset()
        self.__angle = None

    def create(self, image):
        """Create a new ACLine and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _p = self.getPoint()
        if (_p is not None and
            self.__angle is not None):
            _active_layer = image.getActiveLayer()
            _x, _y = _p
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _pt = Point(_x, _y)
                _active_layer.addObject(_pt)
            else:
                _pt = _pts[0]
            _acl = ACLine(_pt, self.__angle)
            _active_layer.addObject(_acl)
            self.reset()

class CLineTool(SegmentTool):
    """A specialized tool for drawing CLine objects.

The CLineTool class is derived from the SegmentTool class,
so it shares all the attributes and methods of that class.

There are no extra methods for the CLineTool class.
    """
    def __init__(self):
        super(CLineTool, self).__init__()

    def create(self, image):
        """Create a new CLine and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        if _p1 is not None and _p2 is not None:
            _active_layer = image.getActiveLayer()
            _x1, _y1 = _p1
            _x2, _y2 = _p2
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x2, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _cline = CLine(_p1, _p2)
            _active_layer.addObject(_cline)
            self.reset()

class CCircleTool(CircleTool):
    """A specialized tool for drawing CCircle objects.

The CCircleTool class is derived from the CircleTool class,
so it shares all the attributes and methods of that class.

There are no additional methods for the CCircleTool class.
    """
    def __init__(self):
        super(CCircleTool, self).__init__()

    def create(self, image):
        """Create a new CCircle and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _active_layer = image.getActiveLayer()
        _x, _y = self.getCenter()
        _radius = self.getRadius()
        _pts = _active_layer.find('point', _x, _y)
        if len(_pts) == 0:
            _cp = Point(_x, _y)
            _active_layer.addObject(_cp)
        else:
            _cp = _pts[0]
        _ccircle = CCircle(_cp, _radius)
        _active_layer.addObject(_ccircle)
        self.reset()

class TwoPointCCircleTool(TwoPointCircleTool):
    """A specialized tool for drawing CCircle objects between two points.

The TwoPointCCircleTool class is derived from the TwoPointCircleTool
class, so it shares all the attributes and methods of that class.
There are no additional methods for the TwoPointCCircleTool class.
    """
    def __init__(self):
        super(TwoPointCCircleTool, self).__init__()

    def create(self, image):
        """Create a new CCircle and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _center = self.getCenter()
        _radius = self.getRadius()
        if _center is not None and _radius is not None:
            _active_layer = image.getActiveLayer()
            _x, _y = _center
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _cp = Point(_x, _y)
                _active_layer.addObject(_cp)
            else:
                _cp = _pts[0]
            _ccircle = CCircle(_cp, _radius)
            _active_layer.addObject(_ccircle)
            self.reset()

#
# The PerpendicularCLineTool and TangentCLineTool classes are
# subclasses of Tool without any additional functionality (yet)
#

class PerpendicularCLineTool(Tool):
    pass

class TangentCLineTool(Tool):
    pass

class ParallelOffsetTool(Tool):
    """A specialized tool for creating parallel construction lines.

The ParallelOffsetTool will create a construction line parallel
to another construction line a fixed distance from the original
construction line. The type of the new construction line will match
that of the original.

The ParallelOffsetTool is derived from the Tool class, so it shares
all the attributes and methods of that class. The ParallelOffsetTool
has the following addtional methods:

{set/get}Offset(): Set/Get the distance between the construction lines.
{set/get}ConstructionLine(): Set/Get the original construction line
{set/get}ReferencePoint(): Set/Get the point to define where the new
                           construction line will go.
    """

    def __init__(self):
        super(ParallelOffsetTool, self).__init__()
        self.__refpt = None
        self.__offset = None
        self.__conline = None

    def setOffset(self, offset):
        """Store the displacement in the tool.

setOffset(offset)

Argument 'offset' must be a float.
        """
        _offset = util.get_float(offset)
        self.__offset = _offset

    def getOffset(self):
        """Return the stored offset from the tool.

getOffset()

This method will raise a ValueError exception if the offset has
not been set with setOffset()
        """
        _offset = self.__offset
        if _offset is None:
            raise ValueError, "Offset is not defined."
        return _offset

    def setConstructionLine(self, conline):
        """Store the reference construction line in the tool.

setConstructionLine(conline)

Argument 'conline' must be a VCLine, HCLine, ACLine, or CLine object.
        """
        if not isinstance(conline, (HCLine, VCLine, ACLine, CLine)):
            raise TypeError, "Invalid Construction line: " + `type(conline)`
        self.__conline = conline

    def getConstructionLine(self):
        """Retrieve the stored construction line from the tool.

getConstructionLine()

A ValueError exception is raised if the construction line has not been
set with the setConstructionLine() method.
        """
        _conline = self.__conline
        if _conline is None:
            raise ValueError, "Construction line is not defined."
        return _conline

    def setReferencePoint(self, x, y):
        """Store the reference point for positioning the new construction line.

setReferencePoint(x, y)

Arguments 'x' and 'y' give the coordinates of a reference point
used to determine where the new construction line will be placed.
Both arguments should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__refpt = (_x, _y)

    def getReferencePoint(self):
        """Retreive the reference point from the tool.

getReferencePoint()

This method returns a tuple containing the values stored from
the setReferencePoint() call. This method will raise a ValueError
exception if the reference point has not been set.
        """
        _refpt = self.__refpt
        if _refpt is None:
            raise ValueError, "No reference point defined."
        return _refpt

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(ParallelOffsetTool, self).reset()
        self.__refpt = None
        self.__offset = None
        self.__conline = None

    def create(self, image):
        """Create a parallel construction line in an image.

create(image)

This method overrides the Tool::create() method.
        """
        _offset = self.__offset
        _conline = self.__conline
        _refpt = self.__refpt
        if (_offset is not None and
            _conline is not None and
            _refpt is not None):
            _active_layer = image.getActiveLayer()
            _rx, _ry = _refpt
            _lp1 = _lp2 = _ncl = None
            if isinstance(_conline, HCLine):
                _x, _y = _conline.getLocation().getCoords()
                if _ry > _y:
                    _yn = _y + _offset
                else:
                    _yn = _y - _offset
                if len(_active_layer.find('hcline', _yn)) == 0:
                    _pts = _active_layer.find('point', _x, _yn)
                    if len(_pts) == 0:
                        _lp1 = Point(_x, _yn)
                    else:
                        _lp1 = _pts[0]
                    _ncl = HCLine(_lp1)
            elif isinstance(_conline, VCLine):
                _x, _y = _conline.getLocation().getCoords()
                if _rx > _x:
                    _xn = _x + _offset
                else:
                    _xn = _x - _offset
                if len(_active_layer.find('vcline', _xn)) == 0:
                    _pts = _active_layer.find('point', _xn, _y)
                    if len(_pts) == 0:
                        _lp1 = Point(_xn, _y)
                    else:
                        _lp1 = _pts[0]
                    _ncl = VCLine(_lp1)
            elif isinstance(_conline, ACLine):
                _x, _y = _conline.getLocation().getCoords()
                _angle = _conline.getAngle()
                if abs(_angle) < 1e-10: # horizontal
                    _dx = 0.0
                    _dy = _offset
                elif abs(abs(_angle) - 90.0) < 1e-10: # vertical
                    _dx = _offset
                    _dy = 0.0
                else:
                    _slope = math.tan(_angle * (math.pi/180.0))
                    _yint = _y - (_slope * _x)
                    #
                    # p1 => (_x, _y)
                    # p2 => (0, _yint)
                    #
                    # redefine angle from p1 to p2 ...
                    _angle = math.atan2((_yint - _y), -_x)
                    if _angle < 0.0:
                        _angle = _angle + (2.0 * math.pi)
                    _sqlen = math.hypot(_x, (_y - _yint))
                    _sn = ((_y - _ry) * (0.0 - _x)) - ((_x - _rx) * (_yint - _y))
                    _s = _sn/_sqlen
                    if _s < 0.0:
                        _perp = _angle + (math.pi/2.0)
                    else:
                        _perp = _angle - (math.pi/2.0)
                    _dx = _offset * math.cos(_perp)
                    _dy = _offset * math.sin(_perp)
                    _angle = _conline.getAngle() # reset variable
                _xn = _x + _dx
                _yn = _y + _dy
                if len(_active_layer.find('acline', _xn, _yn, _angle)) == 0:
                    _pts = _active_layer.find('point', _xn, _yn)
                    if len(_pts) == 0:
                        _lp1 = Point(_xn, _yn)
                    else:
                        _lp1 = _pts[0]
                    _ncl = ACLine(_lp1, _angle)
            elif isinstance(_conline, CLine):
                _p1, _p2 = _conline.getKeypoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                if abs(_x2 - _x1) < 1e-10: # vertical
                    _dx = _offset
                    _dy = 0.0
                elif abs(_y2 - _y1) < 1e-10: # horizontal
                    _dx = 0.0
                    _dy = _offset
                else:
                    _angle = math.atan2((_y2 - _y1), (_x2 - _x1))
                    if _angle < 0.0:
                        _angle = _angle + (2.0 * math.pi)
                    _sqlen = math.hypot((_x2 - _x1), (_y2 - _y1))
                    _sn = ((_y1 - _ry) * (_x2 - _x1)) - ((_x1 - _rx) * (_y2 - _y1))
                    _s = _sn/_sqlen
                    if _s < 0.0:
                        _perp = _angle + (math.pi/2.0)
                    else:
                        _perp = _angle - (math.pi/2.0)
                    _dx = math.cos(_perp) * _offset
                    _dy = math.sin(_perp) * _offset
                _x1n = _x1 + _dx
                _y1n = _y1 + _dy
                _x2n = _x2 + _dx
                _y2n = _y2 + _dy
                if len(_active_layer.find('cline', _x1n, _y1n, _x2n, _y2n)) == 0:
                    _pts = _active_layer.find('point', _x1n, _y1n)
                    if len(_pts) == 0:
                        _lp1 = Point(_x1n, _y1n)
                    else:
                        _lp1 = _pts[0]
                    _pts = _active_layer.find('point', _x2n, _y2n)
                    if len(_pts) == 0:
                        _lp2 = Point(_x2n, _y2n)
                    else:
                        _lp2 = _pts[0]
                    _ncl = CLine(_lp1, _lp2)
            else:
                raise TypeError, "Invalid Construction line type: " + `type(_conline)`
            if _ncl is not None:
                if _lp1 is not None and _lp1.getParent() is None:
                    _active_layer.addObject(_lp1)
                if _lp2 is not None and _lp2.getParent() is None:
                    _active_layer.addObject(_lp2)
                _active_layer.addObject(_ncl)
            self.reset()

class TangentCircleTool(Tool):
    """A specialized class for creating tangent construction circles.

This class is meant to be a base class for tools that create tangent
construction circles. It is derived from the tool class so it shares
all the attributes and methods of that class. This class has the
following additional methods:

{set/get}Center(): Set/Get the center of the tangent circle.
{set/get}Radius(): Set/Get the radius of the tangent circle.
{set/get}PixelRect(): Set/Get the screen rectangle for drawing the circle.
    """
    def __init__(self):
        super(TangentCircleTool, self).__init__()
        self.__center = None
        self.__radius = None
        self.__rect = None

    def setCenter(self, x, y):
        """Store the tangent circle center point in the tool.

setCenter(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__center = (_x, _y)

    def getCenter(self):
        """Return the center of the tangent circle.

getCenter()

This method returns a tuple holding two floats, the first
is the 'x' coordinate of the center, the second is the 'y'
coordinate. If the tool has not yet been invoked with a
setLocation() call, this method returns None.
        """
        return self.__center

    def setRadius(self, radius):
        """Store the radius in the tool.

setRadius(radius)

Argument 'radius' should be a float.
        """
        _radius = util.get_float(radius)
        self.__radius = _radius

    def getRadius(self):
        """Return the center of the tangent circle.

getRadius()

This method returns a float giving the radius of the tangent
circle, or None if the radius is not set.
        """
        return self.__radius

    def setPixelRect(self, xmin, ymin, width, height):
        """Store the screen coordinates used to draw the circle.

setPixelRect(xmin, ymin, width, height)

All the arguments should be integer values.
        """
        _xmin = xmin
        if not isinstance(_xmin, int):
            _xmin = int(xmin)
        _ymin = ymin
        if not isinstance(_ymin, int):
            _ymin = int(ymin)
        _width = width
        if not isinstance(_width, int):
            _width = int(_width)
        _height = height
        if not isinstance(_height, int):
            _height = int(height)
        self.__rect = (_xmin, _ymin, _width, _height)

    def getPixelRect(self):
        """Return the screen boundary of the circle to draw

getPixelRect(self)

This method will return a tuple holding four integer values:

xmin, ymin, width, height

If the rectangle has not been set by calling setPixelRect(), then
this method will return None.
        """
        return self.__rect

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(TangentCircleTool, self).reset()
        self.__center = None
        self.__radius = None
        self.__rect = None

    def create(self, image):
        """Create a new CCircle and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _active_layer = image.getActiveLayer()
        _x, _y = self.__center
        _radius = self.__radius
        _pts = _active_layer.find('point', _x, _y)
        if len(_pts) == 0:
            _cp = Point(_x, _y)
            _active_layer.addObject(_cp)
        else:
            _cp = _pts[0]
        _ccircle = CCircle(_cp, _radius)
        _active_layer.addObject(_ccircle)
        self.reset()

class TangentCCircleTool(TangentCircleTool):
    """A specialized tool for creating tangent construction circles.

The TangentCCircleTool will create a construction circle tangent
to a construction line or a construction circle.

The TangentCCircleTool is derived from the TangentCircleTool class, so
it shares all the attributes and methods of that class. The TangentCCircleTool
has the following addtional methods:

{set/get}ConstructionObject(): Set/Get the reference construction object.
    """
    def __init__(self):
        super(TangentCCircleTool, self).__init__()
        self.__conobj = None

    def setConstructionLine(self, conobj):
        """Store the reference construction object in the tool.

setConstructionLine(conobj)

Argument 'conobj' must be a VCLine, HCLine, ACLine, CLine,
or CCircle object.
        """
        if not isinstance(conobj, (HCLine, VCLine, ACLine, CLine, CCircle)):
            raise TypeError, "Invalid Construction entity type: " + `type(conobj)`
        self.__conobj = conobj

    def getConstructionLine(self):
        """Retrieve the stored construction line from the tool.

getConstructionLine()

A ValueError exception is raised if the construction line has not been
set with the setConstructionLine() method.
        """
        _conobj = self.__conobj
        if _conobj is None:
            raise ValueError, "Construction object is not defined."
        return _conobj

    def setLocation(self, x, y):
        """Store an x/y coordinate pair in the tool.

setLocation(x, y)

Arguments 'x' and 'y' should be floats. This method extends
the TangentCircleTool::setLocation() methods.
        """
        super(TangentCCircleTool, self).setLocation(x, y)
        _tx, _ty = self.getLocation()
        _conobj = self.__conobj
        _cx = _cy = _radius = None
        if isinstance(_conobj, HCLine):
            _x, _y = _conobj.getLocation().getCoords()
            _cx = _tx
            _cy = (_ty + _y)/2.0
            _radius = abs(_ty - _y)/2.0
        elif isinstance(_conobj, VCLine):
            _x, _y = _conobj.getLocation().getCoords()
            _cx = (_tx + _x)/2.0
            _cy = _ty
            _radius = abs(_tx - _x)/2.0
        elif isinstance(_conobj, (ACLine, CLine)):
            _px, _py = _conobj.getProjection(_tx, _ty)
            _cx = (_tx + _px)/2.0
            _cy = (_ty + _py)/2.0
            _radius = math.hypot((_tx - _px), (_ty - _py))/2.0
        elif isinstance(_conobj, CCircle):
            _ccx, _ccy = _conobj.getCenter().getCoords()
            _rad = _conobj.getRadius()
            _sep = math.hypot((_tx - _ccx), (_ty - _ccy))
            if _sep < 1e-10:
                return
            _angle = math.atan2((_ty - _ccy), (_tx - _ccx))
            _px = _ccx + (_rad * math.cos(_angle))
            _py = _ccy + (_rad * math.sin(_angle))
            _cx = (_tx + _px)/2.0
            _cy = (_ty + _py)/2.0
            _radius = math.hypot((_tx - _px), (_ty - _py))/2.0
        else:
            raise TypeError, "Invalid construction entity type: " + `type(_conobj)`
        self.setCenter(_cx, _cy)
        self.setRadius(_radius)

class TwoPointTangentCCircleTool(TangentCircleTool):
    """A specialized tool for creating tangent construction circles.

The TwoPointTangentCCircleTool will create a construction circle tangent
to two construction lines or a construction line and a construction
circle if such a tangent circle can be created.

The TwoPointTangentCCircleTool is derived from the TangentCircleTool
class, so it shares all the attributes and methods of that class. This
class also has the following addtional methods:

{set/get}FirstConObject(): Set/Get the first construction object.
{set/get}SecondConObject(): Set/Get the second constuction object.
    """
    def __init__(self):
        super(TwoPointTangentCCircleTool, self).__init__()
        self.__cobj1 = None
        self.__cobj2 = None

    def setFirstConObject(self, conobj):
        """Store the first reference construction object in the tool.

setFirstConObject(conobj)

Argument 'conobj' must be a VCLine, HCLine, ACLine, CLine, or CCircle object.
        """
        if not isinstance(conobj, (HCLine, VCLine, ACLine, CLine, CCircle)):
            raise TypeError, "Invalid Construction entity type: " + `type(conobj)`
        self.__cobj1 = conobj

    def getFirstConObject(self):
        """Retreive the first construction object from the tool.

getFirstConObject()
        """
        return self.__cobj1

    def setSecondConObject(self, conobj):
        """Store the second reference construction object in the tool.

setSecondConObject(conobj)

Argument 'conobj' must be a VCLine, HCLine, ACLine, or a CLine object.
Drawing a tangent circle against two CCircle objects is not yet supported.
A ValueError exception will be raised if this method is called before the
first construction object has been set.
        """
        if self.__cobj1 is None:
            raise ValueError, "First construction object not set."
        if not isinstance(conobj, (HCLine, VCLine, ACLine, CLine)):
            raise TypeError, "Invalid Construction line type: " + `type(conobj)`
        self.__cobj2 = conobj

    def getSecondConObject(self):
        """Retreive the second construction object from the tool.

getSecondConObject()
        """
        return self.__cobj2

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the TangentCircleTool::reset() method.
        """
        super(TwoPointTangentCCircleTool, self).reset()
        self.__cobj1 = None
        self.__cobj2 = None

    def setLocation(self, x, y):
        """Store an x/y coordinate pair in the tool.

setLocation(x, y)

Arguments 'x' and 'y' should be floats. This method extends
the TangentCircleTool::setLocation() methods.
        """
        super(TwoPointTangentCCircleTool, self).setLocation(x, y)
        _tx, _ty = self.getLocation()
        _obja = self.__cobj1
        _objb = self.__cobj2
        _tandata = tangent.calc_tangent_circle(_obja, _objb, _tx, _ty)
        if _tandata is not None:
            _cx, _cy, _radius = _tandata
            self.setCenter(_cx, _cy)
            self.setRadius(_radius)


class CCircleTangentLineTool(Tool):
    """A specialized class for creating tangent lines to construction circles.

This class is a specialized class that handles creating construction
lines around circles. There can be at most four possible tangent lines.
There are two tangent lines if the circles overlap, and no tangent
lines if one circle is inside another. As this tool is derived from
the Tool class it shares all the attributes and methods of that
class. The CCircleTangentLineTool class has the following additional
methods:

{get/set}FirstCCircle(): Get/Set the first CCircle in the tool.
{get/set}SecondCCircle(): Get/Set the second CCircle in the tool.
    """
    def __init__(self):
        super(CCircleTangentLineTool, self).__init__()
        self.__circ1 = None
        self.__circ2 = None
        self.__tanpts = []

    def setFirstCCircle(self, ccircle):
        """Store the first construction circle in the tool.

setFirstCCircle(ccircle)

Argument 'ccircle' must be a CCircle object.
        """
        if not isinstance(ccircle, CCircle):
            raise TypeError, "Invalid CCircle type: " + `type(ccircle)`
        self.__circ1 = ccircle

    def getFirstCCircle(self):
        """Retreive the first construction circle from the tool.

getFirstCCircle()
        """
        return self.__circ1

    def setSecondCCircle(self, ccircle):
        """Store the second construction circle in the tool.

setSecondCCircle(ccircle)

Argument 'ccircle' must be a CCircle object. A ValueError exception will
be raised if this method is called before the first construction circle
has been set.
        """
        if self.__circ1 is None:
            raise ValueError, "First construction circle not set."
        if not isinstance(ccircle, CCircle):
            raise TypeError, "Invalid CCircle type: " + `type(ccircle)`
        self.__circ2 = ccircle
        #
        # calculate the tangent points if they exist
        #
        _cc1 = self.__circ1
        _cc2 = self.__circ2
        _cx1, _cy1 = _cc1.getCenter().getCoords()
        _r1 = _cc1.getRadius()
        _cx2, _cy2 = _cc2.getCenter().getCoords()
        _r2 = _cc2.getRadius()
        _sep = math.hypot((_cx2 - _cx1), (_cy2 - _cy1))
        _angle = math.atan2((_cy2 - _cy1), (_cx2 - _cx1))
        _sine = math.sin(_angle)
        _cosine = math.cos(_angle)
        #
        # tangent points are calculated as if the first circle
        # center is (0, 0) and both circle centers on the x-axis,
        # so the points need to be transformed to the correct coordinates
        #
        _tanpts = self.__tanpts
        del _tanpts[:] # make sure it is empty ...
        _tansets = tangent.calc_two_circle_tangents(_r1, _r2, _sep)
        for _set in _tansets:
            _x1, _y1, _x2, _y2 = _set
            _tx1 = ((_x1 * _cosine) - (_y1 * _sine)) + _cx1
            _ty1 = ((_x1 * _sine) + (_y1 * _cosine)) + _cy1
            _tx2 = ((_x2 * _cosine) - (_y2 * _sine)) + _cx1
            _ty2 = ((_x2 * _sine) + (_y2 * _cosine)) + _cy1
            _tanpts.append((_tx1, _ty1, _tx2, _ty2))


    def getSecondCCircle(self):
        """Retreive the second construction circle from the tool.

getSecondCCircle()
        """
        return self.__circ2

    def hasTangentPoints(self):
        """Test if tangent points were found for the two circles.

hasTangentPoints()
        """
        _val = False
        if len(self.__tanpts):
            _val = True
        return _val

    def getTangentPoints(self):
        """Return the tangent points calculated for two-circle tangency.

getTangentPoints()

This method returns a list of tuples holding four float values:

(x1, y1, x2, y2)

A tangent line can be drawn between the two circles from (x1, y1) to (x2, y2).
        """
        return self.__tanpts[:]

    def create(self, image):
        """Create the tangent line for two circles.

create(image)
        """
        _x, _y = self.getLocation()
        _tanpts = self.__tanpts
        if not len(_tanpts):
            raise ValueError, "No tangent points defined."
        _minsep = _px1 = _py1 = _px2 = _py2 = None
        for _set in _tanpts:
            _x1, _y1, _x2, _y2 = _set
            _sqlen = pow((_x2 - _x1), 2) + pow((_y2 - _y1), 2)
            _rn = ((_x - _x1) * (_x2 - _x1)) + ((_y - _y1) * (_y2 - _y1))
            _r = _rn/_sqlen
            _px = _x1 + _r * (_x2 - _x1)
            _py = _y1 + _r * (_y2 - _y1)
            _sep = math.hypot((_px - _x), (_py - _y))
            if _minsep is None or _sep < _minsep:
                _minsep = _sep
                _px1 = _x1
                _py1 = _y1
                _px2 = _x2
                _py2 = _y2
        _active_layer = image.getActiveLayer()
        _pts = _active_layer.find('point', _px1, _py1)            
        if len(_pts) == 0:
            _p1 = Point(_px1, _py1)
            _active_layer.addObject(_p1)
        else:
            _p1 = _pts[0]
        _pts = _active_layer.find('point', _px2, _py2)
        if len(_pts) == 0:
            _p2 = Point(_px2, _py2)
            _active_layer.addObject(_p2)
        else:
            _p2 = _pts[0]
        _active_layer.addObject(CLine(_p1, _p2))

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(CCircleTangentLineTool, self).reset()
        self.__circ1 = None
        self.__circ2 = None
        del self.__tanpts[:]

class DimensionTool(Tool):
    """A base class for tools creating Dimension objects.

The DimensionTool class is meant to be a base class for classes
that will create Dimension objects. The DimensionTool class is
derived from the Tool class, so it shares all the attributes and
methods of that class. The DimensionTool class has the following
additional methods:

setDimension(): Store a dimension object in the tool
getDimension(): Retrieve a stored dimension object.
setDimPrefs(): Apply the current dimension preferences on a stored dimension.
    """
    def __init__(self):
        super(DimensionTool, self).__init__()
        self.__dim = None

    def _setDimension(self, dim):
        """Store a dimension in the tool.

setDimension(dim)

The argument 'dim' must be a Dimension object.
        """
        if not isinstance(dim, dimension.Dimension):
            raise TypeError, "Invalid Dimension type: " + `type(dim)`
        self.__dim = dim

    def getDimension(self):
        """Retrieve the stored dimension object from the tool.

getDimension()

This method returns the stored Dimension or None.
        """
        return self.__dim

    def setDimPrefs(self, image):
        """Apply the current dimension options to the stored dimension.

setDimPrefs(image)

The argument 'image' is an image option in which the current dimension
preferences are retrieved.
        """
        _dim = self.__dim
        if _dim is None:
            raise ValueError, "No dimension stored in tool."
        _pds = _dim.getPrimaryDimstring()
        _pds.mute()
        _pds.setFamily(image.getOption('DIM_PRIMARY_FONT_FAMILY'))
        _pds.setWeight(image.getOption('DIM_PRIMARY_FONT_WEIGHT'))
        _pds.setStyle(image.getOption('DIM_PRIMARY_FONT_STYLE'))
        _pds.setColor(image.getOption('DIM_PRIMARY_FONT_COLOR'))
        _pds.setSize(image.getOption('DIM_PRIMARY_TEXT_SIZE'))
        _pds.setAlignment(image.getOption('DIM_PRIMARY_TEXT_ALIGNMENT'))
        _pds.setPrecision(image.getOption('DIM_PRIMARY_PRECISION'))
        _pds.setUnits(image.getOption('DIM_PRIMARY_UNITS'))
        _pds.setPrintZero(image.getOption('DIM_PRIMARY_LEADING_ZERO'))
        _pds.setPrintDecimal(image.getOption('DIM_PRIMARY_TRAILING_DECIMAL'))
        _pds.unmute()
        _sds = _dim.getSecondaryDimstring()
        _sds.mute()
        _sds.setFamily(image.getOption('DIM_SECONDARY_FONT_FAMILY'))
        _sds.setWeight(image.getOption('DIM_SECONDARY_FONT_WEIGHT'))
        _sds.setStyle(image.getOption('DIM_SECONDARY_FONT_STYLE'))
        _sds.setColor(image.getOption('DIM_SECONDARY_FONT_COLOR'))
        _sds.setSize(image.getOption('DIM_SECONDARY_TEXT_SIZE'))
        _sds.setAlignment(image.getOption('DIM_SECONDARY_TEXT_ALIGNMENT'))
        _sds.setPrecision(image.getOption('DIM_SECONDARY_PRECISION'))
        _sds.setUnits(image.getOption('DIM_SECONDARY_UNITS'))
        _sds.setPrintZero(image.getOption('DIM_SECONDARY_LEADING_ZERO'))
        _sds.setPrintDecimal(image.getOption('DIM_SECONDARY_TRAILING_DECIMAL'))
        _sds.unmute()
        _dim.setOffset(image.getOption('DIM_OFFSET'))
        _dim.setExtension(image.getOption('DIM_EXTENSION'))
        _dim.setColor(image.getOption('DIM_COLOR'))
        _dim.setPosition(image.getOption('DIM_POSITION'))
        _dim.setEndpointType(image.getOption('DIM_ENDPOINT'))
        _dim.setEndpointSize(image.getOption('DIM_ENDPOINT_SIZE'))
        _dim.setDualDimMode(image.getOption('DIM_DUAL_MODE'))

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method sets the DimensionTool dimension to None.
        """
        super(DimensionTool, self).reset()
        self.__dim = None

class LinearDimensionTool(DimensionTool):
    """A specialized tool for drawing LinearDimension objects.

The LinearDimensionTool is derived from the DimensionTool and
Tool, class, so it shares all the attributes and methods of those classes.
The LinearDimensionTool class has the following addtional methods:

{set/get}FirstPoint(): Set/Get the first point in the LinearDimension
{set/get}SecondPoint(): Set/Get the second point in the LinearDimension.
{set/get}DimPosition(): Set/Get the location of the dimension text.
    """
    def __init__(self):
        super(LinearDimensionTool, self).__init__()
        self.__p1 = None
        self.__p2 = None
        self.__position = None

    def setFirstPoint(self, p):
        """Store the first point for the LinearDimension.

setFirstPoint(p):

The argument 'p' must be a Point instance.
        """
        if not isinstance (p, Point):
            raise TypeError, "Invalid Point: " + `type(p)`
        if p.getParent() is None:
            raise ValueError, "Point not found in a Layer."
        self.__p1 = p

    def getFirstPoint(self):
        """Return the first point for the LinearDimension.

getFirstPoint()

This method returns a tuple of two objects: the first object
is a Layer, the second object is a Point.
        """
        return self.__p1

    def setSecondPoint(self, p):
        """Store the second point for the LinearDimension.

setSecondPoint(p):

The argument 'p' must be a Point instance.
        """
        if self.__p1 is None:
            raise ValueError, "First point not set for LinearDimension."
        if not isinstance (p, Point):
            raise TypeError, "Invalid Point: " + `type(p)`
        if p.getParent() is None:
            raise ValueError, "Point not found in a Layer."
        self.__p2 = p

    def getSecondPoint(self):
        """Return the second point for the LinearDimension.

getSecondPoint()

This method returns a tuple of two objects: the first object
is a Layer, the second object is a Point.
        """
        return self.__p2

    def setDimPosition(self, x, y):
        """Store the point where the dimension text will be located.

setDimPosition(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__position = (_x, _y)

    def getDimPosition(self):
        """Retrieve where the dimension text should be placed.

getDimPosition()

This method returns a tuple containing the x/y coodindates defined
by the setDimPosition() call, or None if that method has not been invoked.
        """
        return self.__position

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the reset() methods of its base classes.
        """
        super(LinearDimensionTool, self).reset()
        self.__p1 = None
        self.__p2 = None
        self.__position = None

    def makeDimension(self, image):
        """Create a LinearDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension will be used.
        """
        _p1 = self.__p1
        _p2 = self.__p2
        _x, _y = self.__position
        if (_p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _ldim = dimension.LinearDimension(_p1, _p2, _x, _y, _ds)
            self._setDimension(_ldim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new LinearDimension and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _ldim = self.getDimension()
        if _ldim is not None:
            _pds = _ldim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _ldim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _ldim.calcDimValues()
            image.addObject(_ldim)
            self.reset()

class HorizontalDimensionTool(LinearDimensionTool):
    """A specialized tool for drawing HorizontalDimension objects.

The HorizontalDimensionTool is derived from the LinearDimensionTool
and the Tool classes, so it shares all the attributes and methods of
those class.

There are no additional methods for the HorizontalDimension class.
    """
    def __init__(self):
        super(HorizontalDimensionTool, self).__init__()

    def makeDimension(self, image):
        """Create a HorizontalDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension willbe used.
        """
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        _x, _y = self.getDimPosition()
        if (_p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _hdim = dimension.HorizontalDimension(_p1, _p2, _x, _y, _ds)
            self._setDimension(_hdim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new HorizontalDimension and add it to the image.

create(image)

This method overrides the LinearDimensionTool::create() method.
        """
        _hdim = self.getDimension()
        if _hdim is not None:
            _pds = _hdim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _hdim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _hdim.calcDimValues()
            image.addObject(_hdim)
            self.reset()

class VerticalDimensionTool(LinearDimensionTool):
    """A specialized tool for drawing VerticalDimension objects.

The VerticalalDimensionTool is derived from the LinearDimensionTool
and the Tool classes, so it shares all the attributes and methods of
those class.

There are no additional methods for the VerticalalDimension class.
    """
    def __init__(self):
        super(VerticalDimensionTool, self).__init__()

    def makeDimension(self, image):
        """Create a VerticalDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension will be used.
        """
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        _x, _y = self.getDimPosition()
        if (_p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _vdim = dimension.VerticalDimension(_p1, _p2, _x, _y, _ds)
            self._setDimension(_vdim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new VerticalDimension and add it to the image.

create(image)

This method overrides the LinearDimensionTool::create() method.
        """
        _vdim = self.getDimension()
        if _vdim is not None:
            _pds = _vdim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _vdim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _vdim.calcDimValues()
            image.addObject(_vdim)
            self.reset()

class RadialDimensionTool(DimensionTool):
    """A specialized tool for drawing RadialDimension objects.

The RadialDimensionTool class is derived from the DimensionTool class
and Tool class, so it shares all the attributes and methods of those
classes. The RadialDimensionTool class has the following additional
methods:

{set/get}DimObject(): Set/Get the circular object being dimensioned.
{set/get}DimPosition(): Set/Get the location of the dimension text.
    """
    def __init__(self):
        super(RadialDimensionTool, self).__init__()
        self.__cobj = None
        self.__position = None

    def setDimObject(self, cobj):
        """Store the Circle or Arc that the RadialDimension will describe.

setDimObject(cobj):

The argument 'cobj' must be either a Circle or Arc instance.
        """
        if not isinstance (cobj, (Circle, Arc)):
            raise TypeError, "Invalid Circle or Arc: " + `type(cobj)`
        if cobj.getParent() is None:
            raise ValueError, "Circle/Arc not found in a Layer."
        self.__cobj = cobj

    def getDimObject(self):
        """Return the object the RadialDimension will define.

getDimObject()

This method returns a tuple of two objects: the first object
is a Layer, the second object is either a Circle or an Arc
        """
        return self.__cobj.getParent(), self.__cobj

    def setDimPosition(self, x, y):
        """Store the point where the dimension text will be located.

setDimPosition(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__position = (_x, _y)

    def getDimPosition(self):
        """Retrieve where the dimension text should be placed.

getDimPosition()

This method returns a tuple containing the x/y coodindates defined
by the setDimPosition() call, or None if that method has not been
invoked.
        """
        return self.__position

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the reset() methods of its base classes.
        """
        super(RadialDimensionTool, self).reset()
        self.__cobj = None
        self.__position = None

    def makeDimension(self, image):
        """Create a RadialDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension will
be used.
        """
        _cobj = self.__cobj
        _x, _y = self.__position
        if (_cobj is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _rdim = dimension.RadialDimension(_cobj, _x, _y, _ds)
            self._setDimension(_rdim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new RadialDimension and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _rdim = self.getDimension()
        if _rdim is not None:
            _pds = _rdim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('RADIAL_DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('RADIAL_DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _rdim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('RADIAL_DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('RADIAL_DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _rdim.setDiaMode(image.getOption('RADIAL_DIM_DIA_MODE'))
            _rdim.calcDimValues()
            image.addObject(_rdim)
            self.reset()

class AngularDimensionTool(LinearDimensionTool):
    """A specialized tool for drawing AngularDimension objects.

The AngularDimensionTool class is derived from the LinearDimensionTool
class, so it shares all the attributes and methods of that class. The
AngularDimensionTool class has the following additional methods:

{set/get}VertexPoint(): Set/Get the vertex point used by the dimension
    """
    def __init__(self):
        super(AngularDimensionTool, self).__init__()
        self.__vp = None

    def setVertexPoint(self, p):
        """Store the vertex point for the AngularDimension.

setVertexPoint(p):

The argument 'p' must be a Point instance.
        """
        if not isinstance (p, Point):
            raise TypeError, "Invalid Point: " + `type(p)`
        if p.getParent() is None:
            raise ValueError, "Point not found in layer."
        self.__vp = p

    def getVertexPoint(self):
        """Return the vertex point for the AngularDimension.

getVertexPoint()

This method returns a tuple of two objects: the first object
is a Layer, the second object is a Point.
        """

        return self.__vp

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends LinearDimensionTool::reset().
        """
        super(AngularDimensionTool, self).reset()
        self.__vp = None

    def makeDimension(self, image):
        """Create an AngularDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension will be used.
        """
        _vp = self.__vp
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        _x, _y = self.getDimPosition()
        if (_vp is not None and
            _p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _adim = dimension.AngularDimension(_vp, _p1, _p2, _x, _y, _ds)
            self._setDimension(_adim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new AngularDimension and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _adim = self.getDimension()
        if _adim is not None:
            _pds = _adim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('ANGULAR_DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('ANGULAR_DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _adim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('ANGULAR_DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('ANGULAR_DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _adim.calcDimValues()
            image.addObject(_adim)
            self.reset()

#
# printing/plotting tools
#

class PlotTool(Tool):
    """A tool for defining plot regions
    """
    def __init__(self):
        super(PlotTool, self).__init__()
        self.__c1 = None
        self.__c2 = None

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(PlotTool, self).reset()
        self.__c1 = None
        self.__c2 = None

    def setFirstCorner(self, x, y):
        """Store the first corner of the plot region.

setFirstCorner(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__c1 = (_x, _y)

    def getFirstCorner(self):
        """Return the first corner of the plot region.

getFirstCorner()
        """
        if self.__c1 is None:
            raise ValueError, "First corner not defined"
        return self.__c1
    
    def setSecondCorner(self, x, y):
        """Store the second corner of the plot region.

setSecondCorner(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__c2 = (_x, _y)

    def getSecondCorner(self):
        """Return the second corner of the plot region.

getSecondCorner()
        """
        if self.__c2 is None:
            raise ValueError, "Second corner not defined"
        return self.__c2
    
#
# entity modification tools
#

class RegionTool(Tool):
    """A base class for a tool that can store a defined region.

The RegionTool class is designed to be a base class for tools that
need to store a rectangular region. The RegionTool class is derived
from the Tool class, so it shares all the attributes and methods of
that classs. The RegionTool class has the following additional methods:

{set/get}Region(): Set/Get a stored rectangular region
    """
    def __init__(self):
        super(RegionTool, self).__init__()
        self.__region = None

    def setRegion(self, xmin, ymin, xmax, ymax):
        """Store a rectangular region in the RegionTool.

setRegion(xmin, ymin, xmax, ymax)

xmin: The minimum x-coordinate value
ymin: The minimum y-coordinate value
xmax: The maximum x-coordinate value
ymax: The maximum y-coordinate value

All the arguments should be floats. If xmax < xmin or ymax < ymin
a ValueError exception is raised.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Invalid values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Invalid values: ymax < ymin"
        self.__region = (_xmin, _ymin, _xmax, _ymax)

    def getRegion(self):
        """Retrieve the stored rectangular region in the tool.

getRegion()

This method returns a tuple containing four float values:

(xmin, ymin, xmax, ymax)
        """
        return self.__region

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method resets the RegionTool region to None.
        """
        super(RegionTool, self).reset()
        self.__region = None

class MoveTool(RegionTool):
    """A specialized class for moving objects.

The MoveTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes. The
MoveTool class has the following additional methods:

{set/get}Distance(): Set/Get the values to move objects.
    """
    def __init__(self):
        super(MoveTool, self).__init__()
        self.__distance = None

    def setDistance(self, x, y):
        """Store the distance to move objects in the tool.

setDistance(x, y)

Arguments 'x' and 'y' should be floats, and represent the amount
to move objects in the x-coordinate and y-coordinate axes.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__distance = (_x, _y)

    def getDistance(self):
        """Get the displacement stored in the tool.

getDistance()

This method returns a tuple containing two float values.

(xdisp, ydisp)

If this method is called before the setDistance() method is
used, a ValueError exception is raised.
        """
        if self.__distance is None:
            raise ValueError, "No distance stored in tool."
        return self.__distance

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the reset() method of its base classes
        """
        super(MoveTool, self).reset()
        self.__distance = None

class HorizontalMoveTool(MoveTool):
    """A specialized class for moving objects horizontally.

The HorizontalMoveTool is derived from the MoveTool class, so
it shares all the attributes and methods of that class.

There are no additional methods for this class.
    """
    def __init__(self):
        super(HorizontalMoveTool, self).__init__()

    def setDistance(self, x, y):
        """Store the distance to move objects in the tool.

setDistance(x, y)

This method extends the MoveTool::setDistance() method by
enforcing a y-axis displacement of 0.0
        """
        _x = util.get_float(x)
        super(HorizontalMoveTool, self).setDistance(_x, 0.0)

class VerticalMoveTool(MoveTool):
    """A specialized class for moving objects vertically.

The VerticalMoveTool is derived from the MoveTool class, so
it shares all the attributes and methods of that class.

There are no additional methods for this class.

    """
    def __init__(self):
        super(VerticalMoveTool, self).__init__()

    def setDistance(self, x, y):
        """Store the distance to move objects in the tool.

setDistance(x, y)

This method extends the MoveTool::setDistance() method by
enforcing an x-axis displacement of 0.0
        """
        _y = util.get_float(y)
        super(VerticalMoveTool, self).setDistance(0.0, _y)

class StretchTool(MoveTool):
    """A specialized class for stretching objects

The StretchTool class is derived from the MoveTool class, so
it shares all the attributes and methods of that class.

There are no additional methods for this class.
    """
    def __init__(self):
        super(StretchTool, self).__init__()

class HorizontalStretchTool(HorizontalMoveTool):
    """A specialized class for stretching objects horizontally.

The HorizontalStretchTool class is derived from the HorizontalMoveTool
class, so it shares all the attributes and methods of that class.

There are no additional methods for this class.
    """
    def __init__(self):
        super(HorizontalStretchTool, self).__init__()

class VerticalStretchTool(VerticalMoveTool):
    """A specialized class for stretching objects horizontally.

The VerticalStretchTool class is derived from the VerticalMoveTool
class, so it shares all the attributes and methods of that class.

There are no additional methods for this class.
    """
    def __init__(self):
        super(VerticalStretchTool, self).__init__()

class DeleteTool(RegionTool):
    """A specialized class for deleting objects.

The DeleteTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes.

There are no additional methods for this class.
    """
    def __init__(self):
        super(DeleteTool, self).__init__()

class SplitTool(RegionTool):
    """A specialized class for splitting objects.

The SplitTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes.

There are no additional methods for this class.
    """
    def __init__(self):
        super(SplitTool, self).__init__()

class MirrorTool(RegionTool):
    """A specialized class for mirroring objects.

The MirrorTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes. The
MirrorTool class has the following additional methods:

{set/get}MirrorLine(): Set/Get the construction line used for mirroring
    """
    def __init__(self):
        super(MirrorTool, self).__init__()
        self.__mirrorline = None

    def setMirrorLine(self, mline):
        """Store the mirroring construction line in the tool.

setMirrorLine(mline)

The argument 'mline' must be a construction line, otherwise
a TypeError exception is raised.
        """
        if not isinstance(mline, (HCLine, VCLine, ACLine, CLine)):
            raise TypeError, "Invalid mirroring line type: " + `type(mline)`
        self.__mirrorline = mline

    def getMirrorLine(self):
        """Retrieve the mirroring construction line from the tool.

getMirrorLine()

If the mirroring construction line has not been set, a ValueError
exception is raised.
        """
        if self.__mirrorline is None:
            raise ValueError, "No mirror line set."
        return self.__mirrorline

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the RegionTool::reset() method.
        """
        super(MirrorTool, self).reset()
        self.__mirrorline = None

#
# The TransferTool class is a subclass of the RegionTool
# with no additional functionality (yet)
#

class TransferTool(RegionTool):
    pass

class RotateTool(RegionTool):
    """A specialized class for rotating objects.

The RotateTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes. The
Rotateool class has the following additional methods:

{set/get}RotationPoint(): Set/Get the point objects are rotated around
{set/get}Angle(): Set/Get the angle of rotation
    """
    def __init__(self):
        super(RotateTool, self).__init__()
        self.__rp = None
        self.__angle = None

    def setRotationPoint(self, x, y):
        """Set the coordinates the entities will rotate around

setRotationPoint(x, y)

Arguments 'x' and 'y' should be floats
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__rp = (_x, _y)

    def getRotationPoint(self):
        """Get the point objects will rotate around

getRotationPoint()

This method returns a tuple of two floats or None if the rotation
point has not be defined with setRotationPoint()
        """
        return self.__rp

    def setAngle(self, angle):
        """Set the angle of rotation.

setAngle(angle)

Argument 'angle' should be a float value. The value is normalized
so that abs(angle) < 360.0.
        """
        _a = util.get_float(angle)
        self.__angle = math.fmod(_a, 360.0)

    def getAngle(self):
        """Get the angle of rotation.

getAngle()

This method returns a float or None if the angle has not been
set with setAngle()
        """
        return self.__angle

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(RotateTool, self).reset()
        self.__rp = None
        self.__angle = None

class GraphicObjectTool(RegionTool):
    """A specialized class for changing attributes of GraphicObject instances.

The GraphicObjectTool class is derived from the RegionTool class,
so it shares all the attributes and methods of that class. The
GraphicObjectTool class has the following additional methods:

{set/get}Attribute(): Set/Get the desired attribute
{set/get}Value(): Set/Get the new entity color.
    """
    def __init__(self):
        super(RegionTool, self).__init__()
        self.__attr = None
        self.__value = None

    def setAttribute(self, attr):
        """Define which attribute the tool is modifying.

setAttribute(attr)

Argument 'attr' should be either 'setStyle', 'setLinetype', 'setColor',
or 'setThickness'
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        if attr not in ('setStyle', 'setLinetype', 'setColor', 'setThickness'):
             raise ValueError, "Invalid attribute: " + attr
        self.__attr = attr

    def getAttribute(self):
        """Return the specified attribute.

getAttribute()

If called before invoking setAttribute(), this method raises a ValueError.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        return self.__attr

    def setValue(self, val):
        """Store the new value of the entity attribute.

setValue(val)

Argument 'val' depends on the type of attribute defined for the
tool. If no attribute is defined this method raises a ValueError.
Invoking this method with 'None' as an argument sets the tool
to restore the default attribute value.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        _a = self.__attr
        _val = None
        if val is not None:
            if _a == 'setStyle':
                if not isinstance(val, style.Style):
                    raise TypeError, "Invalid Style: " + `type(val)`
                _val = val
            elif _a == 'setLinetype':
                if not isinstance(val, linetype.Linetype):
                    raise TypeError, "Invalid Linetype: " + `type(val)`
                _val = val
            elif _a == 'setColor':
                if not isinstance(val, color.Color):
                    raise TypeError, "Invalid Color: " + `type(val)`
                _val = val
            elif _a == 'setThickness':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid thickness: %g" % _val
            else:
                raise ValueError, "Unexpected attribute: " + _a
        self.__value = _val

    def getValue(self):
        """Get the stored attribute value.

getValue()

This method returns the value stored in setValue() or None.
        """
        return self.__value

#
#
#

class ChangeStyleTool(GraphicObjectTool):
    pass

class ChangeLinetypeTool(GraphicObjectTool):
    pass

class ChangeColorTool(GraphicObjectTool):
    pass

class ChangeThicknessTool(GraphicObjectTool):
    pass

class TextTool(RegionTool):
    """A specialized class for entering text.

The TextTool class is derived from the Tool class, so it shares
the attributes and methods of that class. The TextTool class also
has the following additional methods:

{set/get}Text(): Set/Get the text string in the tool.
hasText(): Test if the tool has stored a text string
{set/get}TextLocation(): Set/Get where the text is to be placed.
{set/get}TextBlock(): Set/Get a TextBlock instance in the Tool
{set/get}Bounds(): Set/Get the width and height of the text
{set/get}PixelSize(): Set/Get the a rectangular region bounding the text.
{set/get}Layout(): Set/Get the formatted text string display.
{set/get/test}Attribute(): Set/Get/Test a TextBlock attribute
{set/get}Value(): Set/Get the attribute value.
    """
    def __init__(self):
        super(TextTool, self).__init__()
        self.__text = None
        self.__location = None
        self.__tblock = None
        self.__attr = None
        self.__value = None
        self.__bounds = None
        self.__pixel_size = None
        self.__layout = None

    def setText(self, text):
        """Store some text in the tool.

setText(text)

The argument 'text' should be a unicode object.
        """
        _text = text
        if not isinstance(_text, unicode):
            _text = unicode(text)
        self.__text = _text

    def getText(self):
        """Retrieve the stored text from the TextTool.

getText()

If no text has been stored, this method raises a ValueError exception.
        """
        if self.__text is None:
            raise ValueError, "No text stored in TextTool."
        return self.__text

    def hasText(self):
        """Test if the tool has stored a text string.

hasText()
        """
        return self.__text is not None

    def setTextLocation(self, x, y):
        """Store the location where the text will be placed.

setTextLocation(x, y)

The arguments 'x' and 'y' should be float values.
        """
        _x, _y = util.make_coords(x, y)
        self.__location = (_x, _y)

    def getTextLocation(self):
        """Retrieve the location where the text will be placed.

getTextLocation()

This method returns a tuple holding two floats:

(x, y)


A ValueError exception is raised if this method is called prior to
setting the text location with setTextLocation().
        """
        if self.__location is None:
            raise ValueError, "No text location defined."
        return self.__location

    def testAttribute(self, attr):
        """Test that the given attribute is valid.

testAttribute(attr)

Argument 'attr' should be one of the following: 'setAngle',
'setAlignment', 'setFamily', 'setStyle', 'setWeight', 'setColor',
or 'setSize'
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        return attr in ('setAngle', 'setAlignment', 'setFamily',
                        'setStyle', 'setWeight', 'setColor', 'setSize')

    def setAttribute(self, attr):
        """Define which attribute the tool is modifying.

setAttribute(attr)

Argument 'attr' should be one of the following: 'setAngle',
'setAlignment', 'setFamily', 'setStyle', 'setWeight', 'setColor',
or 'setSize'
        """
        if not self.testAttribute(attr):
             raise ValueError, "Invalid attribute: " + attr
        self.__attr = attr

    def getAttribute(self):
        """Return the specified attribute.

getAttribute()

If called before invoking setAttribute(), this method raises a ValueError.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        return self.__attr

    def testValue(self, val):
        """Test that the given value is valid for the preset attribute.

testValue(val)

Argument 'val' depends on what attribute has been set with via setAttribute().
        """
        _a = self.__attr
        if _a == 'setAngle':
            _val = util.getFloat(val)
        elif _a == 'setAlignment':
            if not isinstance(val, int):
                raise TypeError, "Invalid alignment type: " + `type(val)`
            if (val != TextStyle.ALIGN_LEFT and
                val != TextStyle.ALIGN_CENTER and
                val != TextStyle.ALIGN_RIGHT):
                raise ValueError, "Invalid alignment value: %d" % val
            _val = val
        elif _a == 'setColor':
            if not isinstance(val, color.Color):
                raise TypeError, "Invalid Color: " + `type(val)`
            _val = val
        elif _a == 'setFamily':
            if not isinstance(val, types.StringTypes):
                raise TypeError, "Invalid family type: " + `type(val)`
            _val = val
        elif _a == 'setStyle':
            if not isinstance(val, int):
                raise TypeError, "Invalid style type: " + `type(val)`
            if (val != TextStyle.FONT_NORMAL and
                val != TextStyle.FONT_OBLIQUE and
                val != TextStyle.FONT_ITALIC):
                raise ValueError, "Invalid style value: %d" % val
            _val = val
        elif _a == 'setWeight':
            if not isinstance(val, int):
                raise TypeError, "Invalid weight type: " + `type(val)`
            if (val != TextStyle.WEIGHT_NORMAL and
                val != TextStyle.WEIGHT_LIGHT and
                val != TextStyle.WEIGHT_BOLD and
                val != TextStyle.WEIGHT_HEAVY):
                raise ValueError, "Invalid weight value: %d" % val
            _val = val
        elif _a == 'setSize':
            _val = util.get_float(val)
            if _val < 0.0:
                raise ValueError, "Invalid size: %g" % _val
        else:
            raise ValueError, "Unexpected attribute: " + _a
        return _val
        
    def setValue(self, val):
        """Store the new value of the entity attribute.

setValue(val)

Argument 'val' depends on the type of attribute defined for the
tool. If no attribute is defined this method raises a ValueError.
Invoking this method with 'None' as an argument sets the tool
to restore the default attribute value.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        _val = None
        if val is not None:
            _val = self.testValue(val)
        self.__value = _val

    def getValue(self):
        """Get the stored attribute value.

getValue()

This method returns the value stored in setValue() or None.
        """
        return self.__value

    def getBounds(self):
        """Return the width and height of the TextBlock.

getBounds()        
        """
        if self.__bounds is None:
            raise ValueError, "TextBlock bounds not defined."
        return self.__bounds

    def setBounds(self, width, height):
        """Set the width and height of the TextBlock.

setBounds(width, height):

Arguments 'width' and 'height' should be positive float values.
        """
        _w = util.get_float(width)
        if _w < 0.0:
            raise ValueError, "Invalid width: %g" % _w
        _h = util.get_float(height)
        if _h < 0.0:
            raise ValueError, "Invalid height: %g" % _h
        self.__bounds = (_w, _h)
        
    def setPixelSize(self, width, height):
        """Store a screen-size rectangular boundary for the text.

setPixelSize(width, height)

Arguments 'width' and 'height' should be positive integer values.

This method is somewhat GTK specific ...
        """
        _width = width
        if not isinstance(_width, int):
            _width = int(width)
        if _width < 0:
            raise ValueError, "Invalid width: %d" % _width
        _height = height
        if not isinstance(_height, int):
            _height = int(height)
        if _height < 0:
            raise ValueError, "Invalid height: %d" % _height
        self.__pixel_size = (_width, _height)

    def getPixelSize(self):
        """Retrieve the stored rectangular region of text.

getPixelSize()

A ValueError exception is raised if this method is called before
the size has been set by setPixelSize()
        """
        if self.__pixel_size is None:
            raise ValueError, "Pixel size is not defined."
        return self.__pixel_size

    def setLayout(self, layout):
        """Store a formatted layout string for the text.

setLayout()

This method is very GTK/Pango specific ...
        """
        self.__layout = layout

    def getLayout(self):
        """Retrieve the formatted layout for the text string.

getLayout()

This method is very GTK/Pango specific ...
        """
        return self.__layout

    def setTextBlock(self, tblock):
        """Store a TextBlock instance within the Tool.

setTextBlock(tblock)

Argument 'tblock' must be a TextBlock.
        """
        if not isinstance(tblock, TextBlock):
            raise TypeError, "Invalid TextBlock: " + `type(tblock)`
        self.__tblock = tblock

    def getTextBlock(self):
        """Retrieve a stored TextBlock within the Tool.

getTextBlock()

This method may return None if no TextBlock has been stored
via setTextBlock().
        """
        return self.__tblock
        
    def create(self, image):
        """Create a new TextBlock and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _tb = self.__tblock
        if _tb is None:
            _text = self.getText()
            _x, _y = self.getTextLocation()
            _ts = image.getOption('TEXT_STYLE')
            _tb = TextBlock(_x, _y, _text, _ts)
            _f = image.getOption('FONT_FAMILY')
            if _f != _ts.getFamily():
                _tb.setFamily(_f)
            _s = image.getOption('FONT_STYLE')
            if _s != _ts.getStyle():
                _tb.setStyle(_s)
            _w = image.getOption('FONT_WEIGHT')
            if _w != _ts.getWeight():
                _tb.setWeight(_w)
            _c = image.getOption('FONT_COLOR')
            if _c != _ts.getColor():
                _tb.setColor(_c)
            _sz = image.getOption('TEXT_SIZE')
            if abs(_sz - _ts.getSize()) > 1e-10:
                _tb.setSize(_sz)
            _a = image.getOption('TEXT_ANGLE')
            if abs(_a - _ts.getAngle()) > 1e-10:
                _tb.setAngle(_a)
            _al = image.getOption('TEXT_ALIGNMENT')
            if _al != _ts.getAlignment():
                _tb.setAlignment(_al)
        image.addObject(_tb)
        self.reset()

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(TextTool, self).reset()
        self.__text = None
        self.__location = None
        self.__tblock = None
        self.__bounds = None
        self.__pixel_size = None
        self.__layout = None

class EditDimensionTool(RegionTool):
    """A specialized class for changing attributes of Dimension instances.

The EditDimensionTool class is derived from the RegionTool class,
so it shares all the attributes and methods of that class. The
EditDimensionTool class has the following additional methods:

{set/get}Attribute(): Set/Get the desired attribute
{set/get}Value(): Set/Get the new entity color.
    """
    def __init__(self):
        super(RegionTool, self).__init__()
        self.__attr = None
        self.__value = None

    def setAttribute(self, attr):
        """Define which attribute the tool is modifying.

setAttribute(attr)

Argument 'attr' should be one of the following:

'setEndpointType', 'setEndpointSize', 'setDualDimMode', 'setDualModeOffset',
'setOffset', 'setExtension', 'setColor', 'setThickness', 'setScale'
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        if attr not in ('setEndpointType', 'setEndpointSize',
                        'setDualDimMode', 'setDualModeOffset',
                        'setOffset', 'setExtension', 'setColor',
                        'setThickness', 'setScale'):
             raise ValueError, "Invalid attribute: " + attr
        self.__attr = attr

    def getAttribute(self):
        """Return the specified attribute.

getAttribute()

If called before invoking setAttribute(), this method raises a ValueError.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        return self.__attr

    def setValue(self, val):
        """Store the new value of the entity attribute.

setValue(val)

Argument 'val' depends on the type of attribute defined for the
tool. If no attribute is defined this method raises a ValueError.
Invoking this method with 'None' as an argument sets the tool
to restore the default attribute value.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        _a = self.__attr
        _val = None
        if val is not None:
            if _a == 'setEndpointType':
                if (val != dimension.Dimension.DIM_ENDPT_NONE and
                    val != dimension.Dimension.DIM_ENDPT_ARROW and
                    val != dimension.Dimension.DIM_ENDPT_FILLED_ARROW and
                    val != dimension.Dimension.DIM_ENDPT_SLASH and
                    val != dimension.Dimension.DIM_ENDPT_CIRCLE):
                    raise ValueError, "Invalid endpoint value: " + str(val)
                _val = val
            elif _a == 'setEndpointSize':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid endpoint size: %g" % _val
                _val = val
            elif _a == 'setDualDimMode':
                util.test_boolean(val)
                _val = val
            elif _a == 'setDualModeOffset':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid offset length: %g" % _val
                _val = val
            elif _a == 'setOffset':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid offset length: %g" % _val
                _val = val
            elif _a == 'setExtension':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid extension length: %g" % _val
                _val = val
            elif _a == 'setColor':
                if not isinstance(val, color.Color):
                    raise TypeError, "Invalid Color: " + `type(val)`
                _val = val
            elif _a == 'setThickness':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid thickness: %g" % _val
            elif _a == 'setScale':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid scale: %g" % _val
            else:
                raise ValueError, "Unexpected attribute: " + _a
        self.__value = _val

    def getValue(self):
        """Get the stored attribute value.

getValue()

This method returns the value stored in setValue() or None.
        """
        return self.__value

class EditDimStringTool(TextTool):
    """A specialized class for modifying DimString instances in Dimensions.

The EditDimStringTool class is derived from the TextTool class, so it
shares the attributes and methods of that class. The TextTool class has
the following additional methods:

{set/get}Primary(): Set/Get the DimString on which the tool operates.
    """
    def __init__(self):
        super(EditDimStringTool, self).__init__()
        self.__pds = True

    def setPrimary(self, flag=True):
        """Set the tool to operate on the primary DimString

setPrimary([flag])

Optional argument 'flag' should be a boolean. By default the
tool will operate on the primary DimString of a Dimension. If
argument 'flag' is False, the tool will operate on the secondary
DimString.
        """
        util.test_boolean(flag)
        self.__pds = flag

    def getPrimary(self):
        """Test if the tool operates on the primary DimString

getPrimary()

This method returns a boolean
        """
        return self.__pds

    def testAttribute(self, attr):
        """Test that the attribute is valid for the DimString entity.

testAttribute(attr)

Argument 'attr' must be one of the following: 'setPrefix', 'setSuffix',
'setUnits', 'setPrecision', 'setPrintZero', 'setPringDecimal', 'setFamily',
'setStyle', 'setWeight', 'setSize', 'setAlignment', 'setColor', or
'setAngle'.
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        _res = attr in ('setPrefix', 'setSuffix', 'setUnits', 'setPrecision',
                        'setPrintZero', 'setPrintDecimal')
        if _res:
            return _res
        return super(EditDimStringTool, self).testAttribute(attr)

    def testValue(self, val):
        """Test that the value is valid for a given DimString attribute.

testValue(val)

Argument 'val' depends on the attribute set for the EditDimString instance.
        """
        _a = self.getAttribute()
        if _a == 'setPrefix' or _a == 'setSuffix':
            if not isinstance(val, types.StringTypes):
                raise TypeError, "Invalid %s type: %s " % (_a, `type(val)`)
            _val = val
            if not isinstance(_val, unicode):
                _val = unicode(val)
        elif _a == 'setPrecision':
            if not isinstance(val, int):
                raise TypeError, "Invalid precision type: " + `type(val)`
            _val = val            
        elif _a == 'setPrintZero' or _a == 'setPrintDecimal':
            try:
                util.test_boolean(val)
            except TypeError:
                raise TypeError, "Invalid %s type: %s " % (_a, `type(val)`)
            _val = val
        elif _a == 'setUnits':
            _val = val # FIXME: needs error checking ...
        else:
            _val = super(EditDimStringTool, self).testValue(val)
        return _val
            
    def setText(self, txt):
        pass

    def getText(self):
        pass
    
    def hasText(self):
        pass
    
    def setTextLocation(self, x, y):
        pass

    def getTextLocation(self):
        pass

    def setBounds(self, width, height):
        pass

    def getBounds(self):
        pass

    def setPixelSize(self, width, height):
        pass

    def getPixelSize(self):
        pass

    def setLayout(self, layout):
        pass

    def getLayout(self):
        pass
