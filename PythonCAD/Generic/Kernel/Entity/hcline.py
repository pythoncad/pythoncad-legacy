#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
#
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
# horizontal construction lines
#

from __future__ import generators

import math

from acline             import ACLine
from tolerance          import *
from util               import *
from point              import Point

class HCLine(ACLine):
    """
        A base class for horizontal construction lines.
    """
    
    def __init__(self, p):
        """
            Instantiate an HCLine object.
        """
        self.__keypoint =p
        ACLine.__init__(self, p, 0)
   
    def __eq__(self, obj):
        """Compare one HCLine to another for equality.
        """
        if not isinstance(obj, HCLine):
            return False
        if obj is self:
            return True
        if abs(self.getLocation().y - obj.getLocation().y) < 1e-10:
            return True
        return False

    def __ne__(self, obj):
        """
            Compare one HCLine to another for inequality.
        """
        if not isinstance(obj, HCLine):
            return True
        if obj is self:
            return False
        if abs(self.getLocation().y - obj.getLocation().y) < 1e-10:
            return False
        return True

    def __str__(self):
        _x, _y = self.getLocation().getCoords()
        return "Horizontal Construction Line at y = %g" % self.__keypoint.y
    
    def getConstructionElements(self):
        """
            get construction elements
        """
        return (self.__keypoint, )
        
    def getLocation(self):
        return self.__keypoint

    def setLocation(self, p):
        if not isinstance(p, point.Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        _kp = self.__keypoint
        if p is not _kp:
            _y = _kp.y
            self.__keypoint = p

    def mapCoords(self, x, y, tol=TOL):
        """
            Return the nearest Point on the HCLine to a coordinate pair.
            The function has two required argument:

            x: A Float value giving the 'x' coordinate
            y: A Float value giving the 'y' coordinate

            There is a single optional argument:

            tol: A float value equal or greater than 0.0

            This function is used to map a possibly near-by coordinate pair to
            an actual Point on the HCLine. If the distance between the actual
            Point and the coordinates used as an argument is less than the tolerance,
            the actual Point is returned. Otherwise, this function returns None.
        """
        _x = get_float(x)
        _y = get_float(y)
        _t = toltest(tol)
        _hy = self.__keypoint.y
        if abs(_hy - _y) < _t:
            return _x, _hy
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not an HCLine passes through a region.

            The first four arguments define the boundary. The method
            will return True if the HCLine falls between ymin and ymax.
            Otherwise the function will return False.
        """
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        test_boolean(fully)
        if fully:
            return False
        _y = self.__keypoint.y
        return not (_y < _ymin or _y > _ymax)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _y = self.__keypoint.y
        if _ymin < _y < _ymax:
            return _xmin, _y, _xmax, _y
        return None

    def clone(self):
        """
            Create an identical copy of an HCLine.
        """
        return HCLine(self.__keypoint.clone())
    def getProjection(self,x,y):
        """
            Get the projection of the point in to the line
        """
        HCLinePoint=self.getLocation()
        x1,y1=HCLinePoint.getCoords()
        x1=x
        return x1,y1
#
#
#

def intersect_region(hcl, xmin, ymin, xmax, ymax):
    if not isinstance(hcl, HCLine):
        raise TypeError, "Invalid HCLine: " + `type(hcl)`
    _xmin = get_float(xmin)
    _ymin = get_float(ymin)
    _xmax = get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _x, _y = hcl.getLocation().getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if _ymin < _y < _ymax:
        _x1 = _xmin
        _y1 = _y
        _x2 = _xmax
        _y2 = _y
    return _x1, _y1, _x2, _y2

