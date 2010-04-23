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
# vertical construction lines
#

from __future__ import generators

import math

from acline             import ACLine
from tolerance          import *
from util               import *
from point              import Point

class VCLine(ACLine):
    """
        A base class for horizontal construction lines.
    """
    def __init__(self, p):
        """
            Instantiate an VCLine object.
        """
        ACLine.__init__(self, p, math.pi/2)
        self.__keypoint = p

    def __eq__(self, obj):
        """
            Compare one VCLine to another for equality.
        """
        if not isinstance(obj, VCLine):
            return False
        if obj is self:
            return True
        if abs(self.getLocation().x - obj.getLocation().x) < 1e-10:
            return True
        return False

    def __ne__(self, obj):
        """
            Compare one VCLine to another for inequality.
        """
        if not isinstance(obj, VCLine):
            return True
        if obj is self:
            return False
        if abs(self.getLocation().x - obj.getLocation().x) < 1e-10:
            return False
        return True

    def __str__(self):
        _x, _y = self.getLocation().getCoords()
        return "Vertical Construction Line at x = %g" % self.__keypoint.x

    def getConstructionElements(self):
        """
            get construction elements
        """
        return (self.__keypoint, )
        
    def getLocation(self):
        return self.__keypoint

    def setLocation(self, p):

        if not isinstance(p, Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        _kp = self.__keypoint
        if p is not _kp:
            _x = _kp.x
            self.__keypoint = p

    def mapCoords(self, x, y, tol=TOL):
        """
            Return the nearest Point on the VCLine to a coordinate pair.
            The function has two required argument:

            x: A Float value giving the 'x' coordinate
            y: A Float value giving the 'y' coordinate

            There is a single optional argument:

            tol: A float value equal or greater than 0.0

            This function is used to map a possibly near-by coordinate pair to
            an actual Point on the VCLine. If the distance between the actual
            Point and the coordinates used as an argument is less than the tolerance,
            the actual Point is returned. Otherwise, this function returns None.
        """
        _x = get_float(x)
        _y = get_float(y)
        _t = tolerance.toltest(tol)
        _vx = self.__keypoint.x
        if abs(_vx - x) < _t:
            return _vx, _y
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not an VCLine passes through a region.

            The first four arguments define the boundary. The method
            will return True if the VCLine falls between xmin and xmax.
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
        _x = self.__keypoint.x
        return not (_x < _xmin or _x > _xmax)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _x = self.__keypoint.x
        if _xmin < _x < _xmax:
            return _x, _ymin, _x, _ymax
        return None

    def clone(self):
        """
            Create an identical copy of an VCLine.
        """
        return VCLine(self.__keypoint.clone())

    def getProjection(self,x,y):
        """
            Get the projection of the point in to the line
        """
        VCLinePoint=self.getLocation()
        x1,y1=VCLinePoint.getCoords()
        y1=y
        return x1,y1
    
def intersect_region(vcl, xmin, ymin, xmax, ymax):
    if not isinstance(vcl, VCLine):
        raise TypeError, "Invalid VCLine: " + `type(vcl)`
    _xmin = get_float(xmin)
    _ymin = get_float(ymin)
    _xmax = get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _x, _y = vcl.getLocation().getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if _xmin < _x < _xmax:
        _x1 = _x
        _y1 = _ymin
        _x2 = _x
        _y2 = _ymax
    return _x1, _y1, _x2, _y2

