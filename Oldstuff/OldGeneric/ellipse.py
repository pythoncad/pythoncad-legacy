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
# class stuff for ellipses
#
# Ellipse info:
# http://mathworld.wolfram.com/Ellipse.html
# http://astronomy.swin.edu.au/~pbourke/geometry/ellipsecirc/
#

import math

from PythonCAD.Generic import baseobject
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import point
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import util

class Ellipse(graphicobject.GraphicObject):
    """A base class for Ellipses

An ellipse has the following attributes:

center: A _point object
major_axis:
minor_axis:
angle: A float from -90.0 to 90.0 degrees
    """

    __defstyle = None
    
    __messages = {
        'center_changed' : True,
        'major_axis_changed' : True,
        'minor_axis_changed' : True,
        'angle_changed' : True,
        'moved' : True,
        }

    def __init__(self, center, major, minor, angle,
                 st=None, lt=None, col=None, t=None, **kw):
        _cp = center
        if not isinstance(_cp, point._Point):
            _cp = point.Point(center)
        _major = util.get_float(major)
        if not _major > 0.0:
            raise ValueError, "Invalid major axis value: %g" % _major
        _minor = util.get_float(minor)
        if not _minor > 0.0:
            raise ValueError, "Invalid minor axis value: %g" % _minor
        if _minor > _major:
            raise ValueError, "Minor axis must be less than major axis"
        _angle = util.make_angle(angle)
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        super(Ellipse, self).__init__(_st, lt, col, t, **kw)
        self.__center = _cp
        self.__major = _major
        self.__minor = _minor
        self.__angle = _angle
        _cp.storeUser(self)
        _cp.connect('moved', self.__movePoint)
        _cp.connect('change_pending', self.__pointChangePending)
        _cp.connect('change_complete', self.__pointChangeComplete)
            
    def __eq__(self, obj):
        """Compare one ellipse to another for equality.
        """
        if not isinstance(obj, Ellipse):
            return False
        if obj is self:
            return True
        return (self.__center == obj.getCenter() and
                abs(self.__major - obj.getMajorAxis()) < 1e-10 and
                abs(self.__minor - obj.getMinorAxis()) < 1e-10 and
                abs(self.__angle - obj.getAngle()) < 1e-10)

    def __ne__(self, obj):
        """Compare one ellipse to another for equality.
        """
        if not isinstance(obj, Ellipse):
            return True
        if obj is self:
            return False
        return (self.__center != obj.getCenter() or
                abs(self.__major - obj.getMajorAxis()) > 1e-10 or
                abs(self.__minor - obj.getMinorAxis()) > 1e-10 or
                abs(self.__angle - obj.getAngle()) > 1e-10)

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Default Ellipse Style',
                             linetype.Linetype(u'Solid', None),
                             color.Color(0xffffff),
                             1.0)
            cls.__defstyle = _s
        return cls.__defstyle

    getDefaultStyle = classmethod(getDefaultStyle)

    def setDefaultStyle(cls, s):
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid style: " + `type(s)`
        cls.__defstyle = s

    setDefaultStyle = classmethod(setDefaultStyle)

    def finish(self):
        self.__center.disconnect(self)
        self.__center.freeUser(self)
        self.__center = self.__major = self.__minor = self.__angle = None
        super(Ellipse, self).finish()

    def setStyle(self, s):
        """Set the Style of the Ellipse.

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(Ellipse, self).setStyle(_s)

    def getValues(self):
        """Return values comprising the Ellipse.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(Ellipse, self).getValues()
        _data.setValue('type', 'ellipse')
        _data.setValue('center', self.__center.getID())
        _data.setValue('major', self.__major)
        _data.setValue('minor', self.__minor)
        _data.setValue('angle', self.__angle)
        return _data
        
    def getCenter(self):
        """Return the center _Point of the Ellipse.

getCenter()
        """
        return self.__center

    def setCenter(self, cp):
        """Set the center _Point of the Ellipse.

setCenter(cp)

The argument must be a _Point or a tuple containing
two float values.
        """
        if self.isLocked():
            raise RuntimeError, "Setting center not allowed - object locked."
        if not isinstance(cp, point._Point):
            raise TypeError, "Invalid Point: " + `cp`
        _c = self.__center
        if _c is not cp:
            _c.disconnect(self)
            _c.freeUser(self)
            self.startChange('center_changed')
            self.__center = cp
            self.endChange('center_changed')
            self.sendMessage('center_changed', _c)
            cp.storeUser(self)
            cp.connect('moved', self.__movePoint)
            cp.connect('change_pending', self.__pointChangePending)
            cp.connect('change_complete', self.__pointChangeComplete)
            if abs(_c.x - cp.x) > 1e-10 or abs(_c.y - cp.y) > 1e-10:
                _x, _y = _c.getCoords()
                self.sendMessage('moved', _x, _y, self.__major, self.__minor,
                                 self.__angle)
            self.modified()

    center = property(getCenter, setCenter, None, "Ellipse center")

    def getMajorAxis(self):
        """Return the major axis value of the Ellipse.

getMajorAxis()

This method returns a float.
        """
        return self.__major

    def setMajorAxis(self, val):
        """Set the major axis of the Ellipse.

setMajorAxis(val)

Argument 'val' must be a float value greater than 0.
        """
        if self.isLocked():
            raise RuntimeError, "Setting major axis not allowed - object locked."
        _val = util.get_float(val)
        if not _val > 0.0:
            raise ValueError, "Invalid major axis value: %g" % _val
        if _val < self.__minor:
            raise ValueError, "Major axis must be greater than minor axis."
        _maj = self.__major
        if abs(_val - _maj) > 1e-10:
            self.startChange('major_axis_changed')
            self.__major = _val
            self.endChange('major_axis_changed')
            self.sendMessage('major_axis_changed', _maj)
            _x, _y = self.__center.getCoords()
            self.sendMessage('moved', _x, _y, _maj, self.__minor, self.__angle)
            self.modified()

    major_axis = property(getMajorAxis, setMajorAxis, None,
                          "Ellipse major axis")

    def getMinorAxis(self):
        """Return the minor axis value of the Ellipse.

getMinorAxis()

This method returns a float.
        """
        return self.__minor

    def setMinorAxis(self, val):
        """Set the minor axis of the Ellipse.

setMinorAxis(val)

Argument 'val' must be a float value greater than 0.
        """
        if self.isModified():
            raise RuntimeError, "Setting minor axis not allowed - object locked."
        _val = util.get_float(val)
        if not _val > 0.0:
            raise ValueError, "Invalid minor axis value: %g" % _val
        if _val > self.__major:
            raise ValueError, "Minor axis must be less than major axis"
        _min = self.__minor
        if abs(_val - _min) > 1e-10:
            self.startChange('minor_axis_changed')
            self.__minor = _val
            self.endChange('minor_axis_changed')
            self.sendMessage('minor_axis_changed', _min)
            _x, _y = self.__center.getCoords()
            self.sendMessage('moved', _x, _y, self.__major, _min, self.__angle)
            self.modified()

    minor_axis = property(getMinorAxis, setMinorAxis, None,
                          "Ellipse minor axis")

    def getAngle(self):
        """Return the Ellipse major axis angle.

getAngle()

This method returns a float value.
        """
        return self.__angle

    def setAngle(self, angle):
        """Set the Ellipse major axis angle.

setAngle(angle)

Argument 'angle' should be a float. The value will be
adjusted so the angle will be defined from 90.0 to -90.0.
        """
        if self.isModified():
            raise RuntimeError, "Setting angle not allowed - object locked."
        _angle = util.make_angle(angle)
        _a = self.__angle
        if abs(_a - _angle) > 1e-10:
            self.startChange('angle_changed')
            self.__angle = _angle
            self.endChange('angle_changed')
            self.sendMessage('angle_changed', _a)
            _x, _y = self.__center.getCoords()
            self.sendMessage('moved', _x, _y, self.__major, self.__minor,
                             _angle)
            self.modified()

    angle = property(getAngle, setAngle, None, "Ellipse major axis angle")

    def move(self, dx, dy):
        """Move an Ellipse.

move(dx, dy)

Arguments 'dx' and 'dy' should be floats.
        """
        if self.isLocked() or self.__center.isLocked():
            raise RuntimeError, "Moving object not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x, _y = self.__center.getCoords()
            self.ignore('moved')
            try:
                self.__center.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _x, _y, self.__major, self.__minor,
                             self.__angle)

    def rotate(self, angle):
        """Rotate an Ellipse

rotate(angle)

Argument 'angle' should be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Rotating object not allowed - object locked."
        _angle = util.get_float(angle)
        if abs(_angle) > 1e-10:
            _cur = self.__angle
            _new = util.make_angle(_angle + _cur)
            self.startChange('angle_changed')
            self.__angle = _new
            self.endChange('angle_changed')
            self.sendMessage('angle_changed', _cur)
            _x, _y = self.__center.getCoords()
            self.sendMessage('moved', _x, _y, self.__major, self.__minor, _cur)
            self.modified()

    def eccentricity(self):
        """Return the eccecntricity of the Ellipse.

eccentricity()

This method returns a float value.
        """
        _major = self.__major
        _minor = self.__minor
        if abs(_major - _minor) < 1e-10: # circular
            _e = 0.0
        else:
            _e = math.sqrt(1.0 - ((_minor * _minor)/(_major * _major)))
        return _e

    def area(self):
        """Return the area of the Ellipse.

area()

This method returns a float value.
        """
        return math.pi * self.__major * self.__minor

    def circumference(self):
        """Return the circumference of an ellipse.

circumference()

This method returns a float.

The algorithm below is taken from
http://astronomy.swin.edu.au/~pbourke/geometry/ellipsecirc/
Ramanujan, Second Approximation
        """
        _a = self.__major
        _b = self.__minor
        _h = math.pow((_a - _b), 2)/math.pow((_a + _b), 2)
        _3h = 3.0 * _h
        return math.pi * (_a + _b) * (1.0 + _3h/(10.0 + math.sqrt(4.0 - _3h)))

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest _Point on the Ellipse to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the 'x' coordinate
y: A Float value giving the 'y' coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual _Point on the Ellipse. If the distance between the actual
_Point and the coordinates used as an argument is less than the tolerance,
the actual _Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _cx, _cy = self.__center.getCoords()
        _dist = math.hypot((_x - _cx), (_y - _cy))
        _major = self.__major
        _minor = self.__minor
        _ep = None
        if abs(_major - _minor) < 1e-10: # circular
            _sep = _dist - _major
            if _sep < _t or abs(_sep - _t) < 1e-10:
                _angle = math.atan2((_y - _cy),(_x - _cx))
                _px = _major * math.cos(_angle)
                _py = _major * math.sin(_angle)
                _ep = point._Point((_cx + _px), (_cy + _py))
        else:
            if _dist < _major and _dist > _minor:
                _ecos = math.cos(self.__angle)
                _esin = math.sin(self.__angle)
                # FIXME ...
        return _ep

    def __pointChangePending(self, p, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if args[0] == 'moved':
            self.startChange('moved')

    def __pointChangeComplete(self, p, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if args[0] == 'moved':
            self.endChange('moved')

    def __movePoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        if p is not self.__center:
            raise ValueError, "Unexpected point in movePoint" + `p`
        self.sendMessage('moved', _x, _y, self.__major, self.__minor,
                         self.__angle)
        self.modified()
    
#
# measure r from focus
#
# x = c + r*cos(theta)
# y = r*sin(theta)
#
# c = sqrt(a^2 - b^2)
#
# r = a*(1-e)/(1 + e*cos(theta))

    def clone(self):
        """Make a copy of an Ellipse.

clone()

This method returns a new Ellipse object
        """
        _cp = self.__center.clone()
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Ellipse(_cp, self.__major, self.__minor, self.__angle,
                       _st, _lt, _col, _th)

    def sendsMessage(self, m):
        if m in Ellipse.__messages:
            return True
        return super(Ellipse, self).sendsMessage(m)
