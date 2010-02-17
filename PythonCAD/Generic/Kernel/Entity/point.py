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

#from PythonCAD.Generic import tolerance
#from PythonCAD.Generic import util

class Point(object):
    """A 2-D point Class.

A Point has the following attributes:

x: x-coordinate
y: y-coordinate

A Point object has the following methods:

{get/set}x(): Get/Set the x-coordinate of the Point.
{get/set}y(): Get/Set the y-coordinate of the Point.
{get/set}Coords(): Get/Set both the x and y coordinates of the Point.
move(): Move a Point.
clone(): Return an identical copy of a Point.
inRegion(): Returns True if the point is in some area.
    """
    __messages = {
        'moved' : True,
        }
    # member functions

    def __init__(self, x, y=None, **kw):
        """
            Initialize a Point.
            There are Tree ways to initialize a Point:
            Point(xc,yc) - Two arguments, with both arguments being floats
            Point((xc,yc)) - A single tuple containing two float objects
            Point(Point) - A single Point Object
        """
        super(Point, self).__init__(**kw)
        if isinstance(x, tuple):
            if y is not None:
                raise SyntaxError, "Invalid call to Point()"
            _x, _y = util.tuple_to_two_floats(x)
        elif y is not None:
            _x = float(x)
            _y = float(y)
        elif isinstance(x,Point):
            _x,_y=x.getCoords()
        else:
            #print "Debug : x[%s] y[%s]"%(str(x),str(y))
            #print "Debug : type x %s"%str(type(x))
            raise SyntaxError, "Invalid call to Point()."
        self.__x = _x
        self.__y = _y

    def __str__(self):
        return "(%g,%g)" % (self.__x, self.__y)

    def __sub__(self, p):
        """Return the separation between two points.

This function permits the use of '-' to be an easy to read
way to find the distance between two Point objects.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid type for Point subtraction: " + `type(p)`
        _px, _py = p.getCoords()
        return math.hypot((self.__x - _px), (self.__y - _py))

    def __eq__(self, obj):
        """Compare a Point to either another Point or a tuple for equality.
        """
        if not isinstance(obj, (Point,tuple)):
            return False
        if isinstance(obj, Point):
            if obj is self:
                return True
            _x, _y = obj.getCoords()
        else:
            _x, _y = util.tuple_to_two_floats(obj)
        if abs(self.__x - _x) < 1e-10 and abs(self.__y - _y) < 1e-10:
            return True
        return False

    def __ne__(self, obj):
        """
            Compare a Point to either another Point or a tuple for inequality.
        """
        if not isinstance(obj, (Point, tuple)):
            return True
        if isinstance(obj, Point):
            if obj is self:
                return False
            _x, _y = obj.getCoords()
        else:
            _x, _y = util.tuple_to_two_floats(obj)
        if abs(self.__x - _x) < 1e-10 and abs(self.__y - _y) < 1e-10:
            return False
        return True
    
    def __add__(self,obj):
        """
            Add two Point
        """
        if not isinstance(obj, Point):
            if isinstance(obj, tuple):
                x, y = util.tuple_to_two_floats(obj)
            else:
                raise TypeError,"Invalid Argument obj: Point or tuple Required"
        else:
            x,y = obj.getCoords()
        return self.__x+x,self.__y+y
    
    def finish(self):
        try: #Fix the setx to None exeption
            self.x = self.y = None
            super(Point, self).finish()
        except:
            return
    def getValues(self):
        """
            Return values comprising the Point.
            getValues()
            This method extends the Subpart::getValues() method.
        """
        _data = super(Point, self).getValues()
        _data.setValue('type', 'point')
        _data.setValue('x', self.__x)
        _data.setValue('y', self.__y)
        return _data

    def getx(self):
        """
            Return the x-coordinate of a Point.
            getx()
        """
        return self.__x

    def setx(self, val):
        """
            Set the x-coordinate of a Point
            setx(val)
            The argument 'val' must be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Coordinate change not allowed - object locked."
        _v = util.get_float(val)
        _x = self.__x
        if abs(_x - _v) > 1e-10:
            self.startChange('moved')
            self.__x = _v
            self.endChange('moved')
            self.sendMessage('moved', _x, self.__y)
            self.modified()

    x = property(getx, setx, None, "x-coordinate value")

    def gety(self):
        """Return the y-coordinate of a Point.

gety()
        """
        return self.__y

    def sety(self, val):
        """Set the y-coordinate of a Point

sety(val)

The argument 'val' must be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Coordinate change not allowed - object locked."
        _v = util.get_float(val)
        _y = self.__y
        if abs(_y - _v) > 1e-10:
            self.startChange('moved')
            self.__y = _v
            self.endChange('moved')
            self.sendMessage('moved', self.__x, _y)
            self.modified()

    y = property(gety, sety, None, "y-coordinate value")

    def getCoords(self):
        """Return the x and y Point coordinates in a tuple.

getCoords()
        """
        return self.__x, self.__y

    def setCoords(self, x, y):
        """Set both the coordinates of a Point.

setCoords(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _sx = self.__x
        _sy = self.__y
        if abs(_sx - _x) > 1e-10 or abs(_sy - _y) > 1e-10:
            self.startChange('moved')
            self.__x = _x
            self.__y = _y
            self.endChange('moved')
            self.sendMessage('moved', _sx, _sy)
            self.modified()

    def move(self, dx, dy):
        """
            Move a Point.
            The first argument gives the x-coordinate displacement,
            and the second gives the y-coordinate displacement. Both
            values should be floats.
        """
        if self.isLocked():
            raise RuntimeError, "Moving not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x = self.__x
            _y = self.__y
            self.startChange('moved')
            self.__x = _x + _dx
            self.__y = _y + _dy
            self.endChange('moved')
            self.sendMessage('moved', _x, _y)
            self.modified()

    def clone(self):
        """
            Create an identical copy of a Point.
        """
        return Point(self.__x, self.__y)

    def inRegion(self, xmin, ymin, xmax, ymax, fully=True):
        """
            Returns True if the Point is within the bounding values.
            inRegion(xmin, ymin, xmax, ymax)
            The four arguments define the boundary of an area, and the
            function returns True if the Point lies within that area.
            Otherwise, the function returns False.
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
        _x = self.__x
        _y = self.__y
        return not ((_x < _xmin) or
                    (_x > _xmax) or
                    (_y < _ymin) or
                    (_y > _ymax))

    def sendsMessage(self, m):
        if m in Point.__messages:
            return True
        return super(Point, self).sendsMessage(m)

    def Dist(self,obj):
        """
           Get The Distance From 2 Points
        """
        if not isinstance(obj, Point):
            if isinstance(x, tuple):            
                _x, _y = util.tuple_to_two_floats(obj)
            else:
                raise TypeError,"Invalid Argument point: Point or Tuple Required"   
        else:
            x,y=obj.getCoords()
        xDist=x-self.__x
        yDist=y-self.__y
        return math.sqrt(pow(xDist,2)+pow(yDist,2)) 
