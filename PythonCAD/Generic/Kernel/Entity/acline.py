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
# single point construction lines at an arbitrary angle
#

from __future__ import generators

import math


from geometricalentity  import *
from tolerance          import *
from util               import *
from point              import Point

class ACLine(GeometricalEntity):
    """
        A class for single point construction lines at a specified angle.
        A ACLine object is derived from an Spcline,so it has
        all that objects properties.

        There is one additional attribute for an ACLine:

        angle: A float value listing the angle at which this line rises or declines

        The limits of the float value: -90.0 < value < 90.0. Any values outside
        that range are adjusted to fall between those limits.
    """
    
    def __init__(self, p, a):
        """
            Initialize an ACLine object.
            p: A Point object the line passes through
            a: The angle at which the line rises or declines
            angle must be in radiants
        """
        if not isinstance(p, Point):
            p = Point(p)
        self.__keypoint = p
        self.__angle = a

    def __eq__(self, obj):
        """
            Compare one ACLine to another for equality.
        """
        if not isinstance(obj, ACLine):
            return False
        if obj is self:
            return True
        _as = self.__angle
        _ao = obj.getAngle()
        _xs, _ys = self.getLocation().getCoords()
        _xo, _yo = obj.getLocation().getCoords()
        _val = False
        if (self.isVertical() and
            obj.isVertical() and
            abs(_xs - _xo) < 1e-10):
            _val = True
        elif (self.isHorizontal() and
              obj.isHorizontal() and
              abs(_ys - _yo) < 1e-10):
              _val = True
        else:
            if abs(_as - _ao) < 1e-10: # same angle
                _ms = math.tan(_as)
                _bs = _ys - (_ms * _xs)
                _y = (_ms * _xo) + _bs
                if abs(_y - _yo) < 1e-10:
                    _val = True
        return _val

    def __ne__(self, obj):
        """
            Compare one ACLine to another for inequality.
        """
        if not isinstance(obj, ACLine):
            return False
        if obj is self:
            return False
        _as = self.__angle
        _ao = obj.getAngle()
        _xs, _ys = self.getLocation().getCoords()
        _xo, _yo = obj.getLocation().getCoords()
        _val = True
        if (self.isVertical() and
            obj.isVertical() and
            abs(_xs - _xo) < 1e-10):
            _val = False
        elif (self.isHorizontal() and
              obj.isHorizontal() and
              abs(_ys - _yo) < 1e-10):
              _val = False
        else:
            if abs(_as - _ao) < 1e-10: # same angle
                _ms = math.tan(_as)
                _bs = _ys - (_ms * _xs)
                _y = (_ms * _xo) + _bs
                if abs(_y - _yo) < 1e-10:
                    _val = False
        return _val

    def __str__(self):
        _point = self.getLocation()
        _angle = self.__angle
        return "Angled construction line through %s at %g degrees" % (_point, _angle)
    
    def getConstructionElements(self):
        """
            get construction elements
        """
        return (self.__keypoint, self.__angle)

    def getAngle(self):
        """
            Return the angle of the ACLine.
        """
        return self.__angle

    def setAngle(self, angle):
        """
            The argument a should be a float representing the angle
            of the ACLine in degrees.
        """
        _a = util.make_angle(angle)
        _oa = self.__angle
        if abs(_a - _oa) > 1e-10:
            self.__angle = _a
            _x, _y = self.__keypoint.getCoords()

    angle = property(getAngle, setAngle, None, "Angle of inclination.")

    def isVertical(self):
        return abs(abs(self.__angle) - 90.0) < 1e-10

    def isHorizontal(self):
        return abs(self.__angle) < 1e-10

    def getLocation(self):
        return self.__keypoint

    def setLocation(self, p):
        if not isinstance(p, Point):
            raise TypeError, "Unexpected type for point: " + `type(p)`
        _kp = self.__keypoint
        if p is not _kp:
            _x, _y = _kp.getCoords()
            self.__keypoint = p

    def mapCoords(self, x, y, tol=TOL):
        """
            Return the nearest Point on the ACLine to a coordinate pair.

            mapCoords(x, y[, tol])

            The function has two required arguments:

            x: A Float value giving the x-coordinate
            y: A Float value giving the y-coordinate

            There is a single optional argument:

            tol: A float value equal or greater than 0.0

            This function is used to map a possibly near-by coordinate pair to
            an actual Point on the ACLine. If the distance between the actual
            Point and the coordinates used as an argument is less than the tolerance,
            the actual Point is returned. Otherwise, this function returns None.
        """
        _x = get_float(x)
        _y = get_float(y)
        _t = toltest(tol)
        _xs, _ys = self.getLocation().getCoords()
        _angle = self.__angle
        #
        # the second point is 1 unit away - this simplifies things ...
        #
        if self.isHorizontal():
            _x2 = _xs + 1.0
            _y2 = _ys
        elif self.isVertical():
            _x2 = _xs
            _y2 = _ys + 1.0
        else:
            _x2 = _xs + math.cos(_angle )
            _y2 = _ys + math.sin(_angle )
        _r = ((_x - _xs)*(_x2 - _xs) + (_y - _ys)*(_y2 - _ys))
        _px = _xs + (_r * (_x2 - _xs))
        _py = _ys + (_r * (_y2 - _ys))
        if abs(_px - _x) < _t and abs(_py - _y) < _t:
            return _px, _py
        return None

    def getProjection(self, x, y):
        """
            Find the projection point of some coordinates on the ACLine.
            Arguments 'x' and 'y' should be float values.
        """
        _x = get_float(x)
        _y = get_float(y)
        _x1, _y1 = self.getLocation().getCoords()
        _angle = self.__angle
        if self.isHorizontal():
            _px = _x
            _py = _y1
        elif self.isVertical():
            _px = _x1
            _py = _y
        else:
            _dx = math.cos(_angle)
            _dy = math.sin(_angle)
            _sqlen = pow(_dx, 2) + pow(_dy, 2)
            _rn = ((_x - _x1) * _dx) + ((_y - _y1) * _dy)
            _r = _rn/_sqlen
            _px = _x1 + (_r * _dx)
            _py = _y1 + (_r * _dy)
        return _px, _py

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not an ACLine passes through a region.
            The first four arguments define the boundary. The method
            will return True if the ACLine passes through the boundary.
            Otherwise the function will return False.
        """
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        test_boolean(fully)
        if fully:
            return False
        _x, _y = self.getLocation().getCoords()
        _angle = self.__angle
        _val = False
        if _xmin < _x < _xmax and _ymin < _y < _ymax:
            _val = True
        elif self.isHorizontal() and _ymin < _y < _ymax:
            _val = True
        elif self.isVertical() and _xmin < _x < _xmax:
            _val = True
        else:
            #
            # the ACLine can be parameterized as
            #
            # x = u * (x2 - x1) + x1
            # y = u * (y2 - y1) + y1
            #
            # for u = 0, x => x1, y => y1
            # for u = 1, x => x2, y => y2
            #
            # if the ACLine passes through the region then there
            # will be valid u occuring at the region boundary
            #
            _dx = math.cos(_angle)
            _dy = math.sin(_angle)
            #
            # x = xmin
            #
            _u = (_xmin - _x)/_dx
            _yt = (_u * _dy) + _y
            if (_ymin - 1e-10) < _yt < (_ymax + 1e-10): # catch endpoints
                _val = True
            if not _val:
                #
                # x = xmax
                #
                _u = (_xmax - _x)/_dx
                _yt = (_u * _dy) + _y
                if (_ymin - 1e-10) < _yt < (_ymax + 1e-10): # catch endpoints
                    _val = True
                if not _val:
                    #
                    # y = ymin
                    #
                    # if this fails there is no way the ACLine can be in
                    # region because it cannot pass through only one side
                    #
                    _u = (_ymin - _y)/_dy
                    _xt = (_u * _dx) + _x
                    if _xmin < _xt < _xmax:
                        _val = True
        return _val

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        _xmin = get_float(xmin)
        _ymin = get_float(ymin)
        _xmax = get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _x, _y = self.getLocation().getCoords()
        _angle = self.__angle
        _coords = None
        if self.isVertical() and _xmin < _x < _xmax:
            _coords = (_x, _ymin, _x, _ymax)
        elif self.isHorizontal() and _ymin < _y < _ymax:
            _coords = (_xmin, _y, _xmax, _y)
        else:
            #
            # the ACLine can be parameterized as
            #
            # x = u * (x2 - x1) + x1
            # y = u * (y2 - y1) + y1
            #
            # for u = 0, x => x1, y => y1
            # for u = 1, x => x2, y => y2
            #
            # The following is the Liang-Barsky Algorithm
            # for segment clipping modified slightly for
            # construction lines
            #
            _dx = math.cos(_angle)
            _dy = math.sin(_angle)
            _P = [-_dx, _dx, -_dy, _dy]
            _q = [(_x - _xmin), (_xmax - _x), (_y - _ymin), (_ymax - _y)]
            _u1 = None
            _u2 = None
            _valid = True
            for _i in range(4):
                _pi = _P[_i]
                _qi = _q[_i]
                if abs(_pi) < 1e-10: # this should be caught earlier ...
                    if _qi < 0.0:
                        _valid = False
                        break
                else:
                    _r = _qi/_pi
                    if _pi < 0.0:
                        if _u2 is not None and _r > _u2:
                            _valid = False
                            break
                        if _u1 is None or _r > _u1:
                            _u1 = _r
                    else:
                        if _u1 is not None and _r < _u1:
                            _valid = False
                            break
                        if _u2 is None or _r < _u2:
                            _u2 = _r
            if _valid:
                _coords = (((_u1 * _dx) + _x),
                           ((_u1 * _dy) + _y),
                           ((_u2 * _dx) + _x),
                           ((_u2 * _dy) + _y))
        return _coords

    def clone(self):
        """
            Create an identical copy of an ACLine.
        """
        return ACLine(self.__keypoint.clone(), self.__angle)


def intersect_region(acl, xmin, ymin, xmax, ymax):
    if not isinstance(acl, ACLine):
        raise TypeError, "Argument not an ACLine: " + `type(acl)`
    _xmin = get_float(xmin)
    _ymin = get_float(ymin)
    _xmax = get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _x, _y = acl.getLocation().getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if acl.isVertical() and _xmin < _x < _xmax:
        _x1 = _x
        _y1 = _ymin
        _x2 = _x
        _y2 = _ymax
    elif acl.isHorizontal() and _ymin < _y < _ymax:
        _x1 = _xmin
        _y1 = _y
        _x2 = _xmax
        _y2 = _y
    else:
        _angle = acl.getAngle()
        _slope = math.tan(_angle )
        _yint = _y - (_x * _slope)
        _xt = _x + math.cos(_angle)
        _yt = _y + math.sin(_angle)
        #
        # find y for x = xmin
        #
        _yt = (_slope * _xmin) + _yint
        if _ymin < _yt < _ymax:
            # print "hit at y for x=xmin"
            _x1 = _xmin
            _y1 = _yt
        #
        # find y for x = xmax
        #
        _yt = (_slope * _xmax) + _yint
        if _ymin < _yt < _ymax:
            # print "hit at y for x=xmax"
            if _x1 is None:
                _x1 = _xmax
                _y1 = _yt
            else:
                _x2 = _xmax
                _y2 = _yt
        if _x2 is None:
            #
            # find x for y = ymin
            #
            _xt = (_ymin - _yint)/_slope
            if _xmin < _xt < _xmax:
                # print "hit at x for y=ymin"
                if _x1 is None:
                    _x1 = _xt
                    _y1 = _ymin
                else:
                    _x2 = _xt
                    _y2 = _ymin
        if _x2 is None:
            #
            # find x for y = ymax
            #
            _xt = (_ymax - _yint)/_slope
            if _xmin < _xt < _xmax:
                # print "hit at x for y=ymax"
                if _x1 is None:
                    _x1 = _xt
                    _y1 = _ymax
                else:
                    _x2 = _xt
                    _y2 = _ymax
    return _x1, _y1, _x2, _y2

