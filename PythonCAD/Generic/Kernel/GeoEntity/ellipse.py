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


from Kernel.GeoUtil.tolerance              import *
from Kernel.GeoUtil.util                   import *
from Kernel.GeoEntity.point                import Point
from Kernel.GeoEntity.geometricalentity    import *

class Ellipse(GeometricalEntity):
    """
        A base class for Ellipses
        An ellipse has the following attributes:
        center: A _point object
        major_axis:
        minor_axis:
    """
    def __init__(self,kw):
        """
            Initialize a Arc/Circle.
            kw['ELLIPSE_0'] center must be a point 
            kw['ELLIPSE_1'] major ax
            kw['ELLIPSE_2'] minor ax
        """
        argDescription={
                        "ELLIPSE_0":Point,
                        "ELLIPSE_1":(float, int), 
                        "ELLIPSE_2":(float, int)
                        }
        _major=kw['ELLIPSE_1']
        _minor=kw['ELLIPSE_2']
        if _minor > _major:
            kw['ELLIPSE_2']=get_float(major)
            kw['ELLIPSE_1']=get_float(minor)
        GeometricalEntity.__init__(self,kw, argDescription)
            
    def __eq__(self, obj):
        """
            Compare one ellipse to another for equality.
        """
        if not isinstance(obj, Ellipse):
            return False
        if obj is self:
            return True
        return (self.center == obj.getCenter() and
                abs(self.major - obj.getMajorAxis()) < 1e-10 and
                abs(self.minor - obj.getMinorAxis()) < 1e-10 
                )

    def __ne__(self, obj):
        """
            Compare one ellipse to another for equality.
        """
        return not self==object

    def getCenter(self):
        """
            Return the center _Point of the Ellipse.
        """
        return self['ELLIPSE_0']

    def setCenter(self, point):
        """
            Set the center _Point of the Ellipse.
            The argument must be a _Point or a tuple containing
            two float values.
        """
        self['ELLIPSE_0'] = point

    center = property(getCenter, setCenter, None, "Ellipse center")

    def getMajorAxis(self):
        """
            Return the major axis value of the Ellipse.
            This method returns a float.
        """
        return self['ELLIPSE_1']

    def setMajorAxis(self, val):
        """
            Set the major axis of the Ellipse.
            Argument 'val' must be a float value greater than 0.
        """
        _val = get_float(val)
        if _val < 0.0:
            raise ValueError, "Invalid major axis value: %g" % _val
        if _val < self.minor:
            self.self['ELLIPSE_1']=self.minor
            self.minor=_val
        else:
            self['ELLIPSE_1']=_val
            
    major= property(getMajorAxis, setMajorAxis, None,
                          "Ellipse major axis")

    def getMinorAxis(self):
        """
            Return the minor axis value of the Ellipse.
            This method returns a float.
        """
        return self['ELLIPSE_2']

    def setMinorAxis(self, val):
        """
            Set the minor axis of the Ellipse.
            Argument 'val' must be a float value greater than 0.
        """
        _val = get_float(val)
        if _val < 0.0:
            raise ValueError, "Invalid minor axis value: %g" % _val
        if _val > self.major:
            self['ELLIPSE_2']=self.major
            self.major=_val
        else:
            self['ELLIPSE_2']=_val
            
    minor = property(getMinorAxis, setMinorAxis, None,
                          "Ellipse minor axis")


    def eccentricity(self):
        """
            Return the eccecntricity of the Ellipse.
            This method returns a float value.
        """
        _major = self.major
        _minor = self.minor
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
        return math.pi * self.major * self.minor

    def circumference(self):
        """
            Return the circumference of an ellipse.
            This method returns a float.
            The algorithm below is taken from
            http://astronomy.swin.edu.au/~pbourke/geometry/ellipsecirc/
            Ramanujan, Second Approximation
        """
        _a = self.major
        _b = self.minor
        _h = math.pow((_a - _b), 2)/math.pow((_a + _b), 2)
        _3h = 3.0 * _h
        return math.pi * (_a + _b) * (1.0 + _3h/(10.0 + math.sqrt(4.0 - _3h)))

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
        return Ellipse(self.getConstructionElements())

    def getSympy(self):
        """
            get the sympy object in this case a ellipse
        """
        _cp=self.center.getSympy()
        return geoSympy.Ellipse(geoSympy.Point(0,0),mainSympy.Rational(self.major),mainSympy.Rational(self.minor))
        
    def setFromSympy(self, sympyEllipse):    
        """
            update the points cord from a sympyobject only avaiable for circle
        """
        self.center.setFromSympy(sympyEllipse[0])
        self.major=float(sympyEllipse[1])
        self.minor=float(sympyEllipse[2])
        
    def __str__(self):
        msg="Ellipse: Center %s , Major Axi=%s, Mino Axi=%s"%(
            str(self.center), str(self.major), str(self.minor))
        return msg
