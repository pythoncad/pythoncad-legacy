#
# Copyright (c) 2003, 2004, 2005, 2006 Art Haas
# Copyright (c) 2010 Matteo Boscolo
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


from tolerance          import *
from util               import *
from point              import Point
from geometricalentity  import *

class Ellipse(GeometricalEntity):
    """
        A base class for Ellipses
        An ellipse has the following attributes:
        center: A _point object
        major_axis:
        minor_axis:
        angle: A float from -90.0 to 90.0 degrees
    """
    def __init__(self, center, major, minor, angle,):
        _cp = center
        if not isinstance(_cp, Point):
            _cp = Point(center)
        _major = get_float(major)
        if not _major > 0.0:
            raise ValueError, "Invalid major axis value: %g" % _major
        _minor = get_float(minor)
        if not _minor > 0.0:
            raise ValueError, "Invalid minor axis value: %g" % _minor
        if _minor > _major:
            raise ValueError, "Minor axis must be less than major axis"
        _angle = make_angle(angle)
        self.__center = _cp
        self.__major = _major
        self.__minor = _minor
        self.__angle = _angle

    def __eq__(self, obj):
        """
            Compare one ellipse to another for equality.
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
        """
            Compare one ellipse to another for equality.
        """
        if not isinstance(obj, Ellipse):
            return True
        if obj is self:
            return False
        return (self.__center != obj.getCenter() or
                abs(self.__major - obj.getMajorAxis()) > 1e-10 or
                abs(self.__minor - obj.getMinorAxis()) > 1e-10 or
                abs(self.__angle - obj.getAngle()) > 1e-10)

    def getConstructionElements(self):
        """
            Get the Construction element of the Ellipse.
            This function returns a tuple containing the Point objects
            that for inizializing the Ellipse
        """
        return self.__center, self.__major,self.__minor,self.__angle

    def getCenter(self):
        """
            Return the center _Point of the Ellipse.
        """
        return self.__center

    def setCenter(self, cp):
        """
            Set the center _Point of the Ellipse.
            The argument must be a _Point or a tuple containing
            two float values.
        """
        if not isinstance(cp, Point):
            raise TypeError, "Invalid Point: " + `cp`
        _c = self.__center
        if _c is not cp:
            self.__center = cp

    center = property(getCenter, setCenter, None, "Ellipse center")

    def getMajorAxis(self):
        """
            Return the major axis value of the Ellipse.
            This method returns a float.
        """
        return self.__major

    def setMajorAxis(self, val):
        """
            Set the major axis of the Ellipse.
            Argument 'val' must be a float value greater than 0.
        """
        _val = get_float(val)
        if not _val > 0.0:
            raise ValueError, "Invalid major axis value: %g" % _val
        if _val < self.__minor:
            raise ValueError, "Major axis must be greater than minor axis."
        _maj = self.__major
        if abs(_val - _maj) > 1e-10:
            self.__major = _val
    major_axis = property(getMajorAxis, setMajorAxis, None,
                          "Ellipse major axis")

    def getMinorAxis(self):
        """
            Return the minor axis value of the Ellipse.
            This method returns a float.
        """
        return self.__minor

    def setMinorAxis(self, val):
        """
            Set the minor axis of the Ellipse.
            Argument 'val' must be a float value greater than 0.
        """
        _val = get_float(val)
        if not _val > 0.0:
            raise ValueError, "Invalid minor axis value: %g" % _val
        if _val > self.__major:
            raise ValueError, "Minor axis must be less than major axis"
        _min = self.__minor
        if abs(_val - _min) > 1e-10:
            self.__minor = _val

    minor_axis = property(getMinorAxis, setMinorAxis, None,
                          "Ellipse minor axis")

    def getAngle(self):
        """
            Return the Ellipse major axis angle.
            This method returns a float value.
        """
        return self.__angle

    def setAngle(self, angle):
        """
            Set the Ellipse major axis angle.
            Argument 'angle' should be a float. The value will be
            adjusted so the angle will be defined from 90.0 to -90.0.
        """
        _angle = make_angle(angle)
        _a = self.__angle
        if abs(_a - _angle) > 1e-10:
            self.__angle = _angle
    angle = property(getAngle, setAngle, None, "Ellipse major axis angle")


    def rotate(self, angle):
        """
            Rotate an Ellipse
            Argument 'angle' should be a float.
        """
        _angle = get_float(angle)
        if abs(_angle) > 1e-10:
            _cur = self.__angle
            _new = make_angle(_angle + _cur)
            self.__angle = _new

    def eccentricity(self):
        """
            Return the eccecntricity of the Ellipse.
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
        """
            Return the area of the Ellipse.
            This method returns a float value.
        """
        return math.pi * self.__major * self.__minor

    def circumference(self):
        """
            Return the circumference of an ellipse.
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

    def mapCoords(self, x, y, tol=TOL):
        """
            Return the nearest _Point on the Ellipse to a coordinate pair.
            x: A Float value giving the 'x' coordinate
            y: A Float value giving the 'y' coordinate
            There is a single optional argument:
            tol: A float value equal or greater than 0.0

            This function is used to map a possibly near-by coordinate pair to
            an actual _Point on the Ellipse. If the distance between the actual
            _Point and the coordinates used as an argument is less than the tolerance,
            the actual _Point is returned. Otherwise, this function returns None.
        """
        _x = get_float(x)
        _y = get_float(y)
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
                _ep =Point((_cx + _px), (_cy + _py))
        else:
            if _dist < _major and _dist > _minor:
                _ecos = math.cos(self.__angle)
                _esin = math.sin(self.__angle)
                # FIXME ...
        return _ep

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
        """
            Make a copy of an Ellipse.
            This method returns a new Ellipse object
        """
        _cp = self.__center.clone()
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Ellipse(_cp, self.__major, self.__minor, self.__angle,
                       _st, _lt, _col, _th)

