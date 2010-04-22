#
# Copyright (c) 2002, 2003, 2004, 2005 Art Haas
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
# a construction line defined by two points
#

from __future__ import generators

import math

from acline             import ACLine
from tolerance          import *
from util               import *
from point              import Point

class CLine(ACLine):
    """
        A class for construction lines defined by two distinct Points.

        A CLine object is derived from the conobject class, so it shares
        the functionality of that class. In addition, a CLine instance
        has two attributes:

        p1: A Point object representing the first keypoint
        p2: A Point object representing the second keypoint

        A CLine has the following methods:
    """
    def __init__(self, p1, p2):
        """
            Initialize a CLine object.
            p1: Point
            p2: Point
            Both arguments are Point objects that the CLine passes through.
        """
        if not isinstance(p1, Point):
            raise AttributeError, "p1 must be a Point"
        if not isinstance(p2, Point):
            raise AttributeError, "p2 must be a Point"
        if p1 is p2:
            raise ValueError, "A CLine must have two different keypoints."
        self.__p1 = p1
        self.__p2 = p2
        angle=self._getAngle(p1, p2)
        ACLine.__init__(p1, angle)

    def _getAngle(self, p1, p2):
        """
            get an angle that define the line
        """
        x, y=p1.getCoords()
        x1, y1=p1.getCoords()
        b=float(abs(x1-x))
        a=float(abs(y1-y))
        try:
            rangle=(a/b)
            angle=math.atan(rangle)
            return angle
        except ZeroDivisionError:
            return math.pi/2
        
    def getP1(self):
        """
            Return the first keypoint Point of the CLine.
        """
        return self.__p1

    def setP1(self, p):
        """
            Set the first keypoint Point of the CLine.
            Argument 'p' must be a Point.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        if p is self.__p2 or p == self.__p2:
            raise ValueError, "CLines must have two different keypoints."
        _kp = self.__p1
        if _kp is not p:
            self.__p1 = p

    p1 = property(getP1, setP1, None, "First keypoint of the CLine.")

    def getP2(self):
        """
            Return the second keypoint Point of the CLine.
        """
        return self.__p2

    def setP2(self, p):
        """
            Set the second keypoint Point of the CLine.
            Argument 'p' must be a Point.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid keypoint: " + `type(p)`
        if p is self.__p1 or p == self.__p1:
            raise ValueError, "CLines must have two different keypoints."
        _kp = self.__p2
        if _kp is not p:
            self.__p2 = p
            p.storeUser(self)

    p2 = property(getP2, setP2, None, "Second keypoint of the CLine.")

    def clone(self):
        """
            Create an identical copy of a CLine.
        """
        _cp1 = self.__p1.clone()
        _cp2 = self.__p2.clone()
        return CLine(_cp1, _cp2)
  
    def getMiddlePoint(self):
        """
            get the middle point of the two cline defining points
        """
        _x = (self.__p1.getx() + self.__p2.getx()) / 2
        _y = (self.__p1.gety() + self.__p2.gety()) / 2
        _point = Point(_x, _y)
        return _point
        
def intersect_region(cl, xmin, ymin, xmax, ymax):
    if not isinstance(cl, CLine):
        raise TypeError, "Invalid CLine: " + `type(cl)`
    _xmin = get_float(xmin)
    _ymin = get_float(ymin)
    _xmax = get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = util.get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    _p1, _p2 = cl.getKeypoints()
    _p1x, _p1y = _p1.getCoords()
    _p2x, _p2y = _p2.getCoords()
    _x1 = _y1 = _x2 = _y2 = None
    if abs(_p2x - _p1x) < 1e-10: # vertical
        if _xmin < _p1x < _xmax:
            _x1 = _p1x
            _y1 = _ymin
            _x2 = _p1x
            _y2 = _ymax
    elif abs(_p2y - _p1y) < 1e-10: # horiztonal
        if _ymin < _p1y < _ymax:
            _x1 = _xmin
            _y1 = _p1y
            _x2 = _xmax
            _y2 = _p1y
    else:
        _slope = (_p2y - _p1y)/(_p2x - _p1x)
        _yint = _p1y - (_p1x * _slope)
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

