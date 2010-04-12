#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas 
# Copyright (c) 2009,2010 Matteo Boscolo
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
# classes for line segments
#

from __future__ import generators

import math

from point import Point
  
class Segment(object):
    """
        A class representing a line segment.
    """
    def __init__(self, p1, p2):
        """
            Initialize a Segment object.
            p1: Segment first endpoint - may be a Point or a two-item tuple of floats.
            p2: Segment second endpoint - may be a Point or a two-item tuple of floats.
        """

        _p1 = p1
        if not isinstance(_p1, Point):
            _p1 = Point(p1)
        _p2 = p2
        if not isinstance(_p2, Point):
            _p2 = Point(p2)
        if _p1 is _p2:
            raise ValueError, "Segments cannot have identical endpoints."
        _st = st
        self.__p1 = _p1
        self.__p2 = _p2     
        
    def getConstructionElements(self):
        """
            Get the endpoints of the Point.
            This function returns a tuple containing the Point objects
            that for inizializing the Point
        """
        return self.__p1, self.__p2
        
    def __str__(self):
        return "Segment: %s to %s" % (self.__p1, self.__p2)

    def __eq__(self, obj):
        """
            Compare a Segment to another for equality.
        """
        if not isinstance(obj, Segment):
            return False
        if obj is self:
            return True
        _sp1 = self.__p1
        _sp2 = self.__p2
        _op1, _op2 = obj.getEndpoints()
        return (((_sp1 == _op1) and (_sp2 == _op2)) or
                ((_sp1 == _op2) and (_sp2 == _op1)))

    def __ne__(self, obj):
        """
            Compare a Segment to another for inequality.
        """
        if not isinstance(obj, Segment):
            return True
        if obj is self:
            return False
        _sp1 = self.__p1
        _sp2 = self.__p2
        _op1, _op2 = obj.getEndpoints()
        return (((_sp1 != _op1) or (_sp2 != _op2)) and
                ((_sp1 != _op2) or (_sp2 != _op1)))

    def getValues(self):
        """
            Return values comprising the Segment.
            This method extends the GraphicObject::getValues() method.
        """
        _data = {}
        _data['type']='segment'
        _data['p1']=self.__p1.getID()
        _data['p2']=self.__p2.getID()
        return _data

    def getEndpoints(self):
        """
            Get the endpoints of the Segment.
            This function returns a tuple containing the two Point objects
            that are the endpoints of the segment.
        """
        return self.__p1, self.__p2

    def getP1(self):
        """
            Return the first endpoint Point of the Segment.
        """
        return self.__p1

    def setP1(self, p):
        """
            Set the first endpoint Point of the Segment.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid P1 endpoint type: " + `type(p)`
        if p is self.__p2:
            raise ValueError, "Segments cannot have identical endpoints."
        _pt = self.__p1
        if _pt is not p:
            self.__p1 = p

    p1 = property(getP1, setP1, None, "First endpoint of the Segment.")

    def getP2(self):
        """
            Return the second endpoint Point of the Segment.
        """
        return self.__p2

    def setP2(self, p):
        """
            Set the second endpoint Point of the Segment.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid P2 endpoint type: " + `type(p)`
        if p is self.__p1:
            raise ValueError, "Segments cannot have identical endpoints."
        _pt = self.__p2
        if _pt is not p:
            self.__p2 = p

    p2 = property(getP2, setP2, None, "Second endpoint of the Segment.")

    def length(self):
        """
            Return the length of the Segment.
        """
        return self.__p1 - self.__p2
        
    def getCoefficients(self):
        """
            Express the line segment as a function ax + by + c = 0
            This method returns a tuple of three floats: (a, b, c)
        """
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _a = _y2 - _y1
        _b = _x1 - _x2
        _c = (_x2 * _y1) - (_x1 * _y2)
        return _a, _b, _c
    
    def getMiddlePoint(self):
        """
            Return the middle point of the segment
        """
        _p1,_p2=self.getEndpoints()
        _x1=util.get_float(_p1.x)
        _x2=util.get_float(_p2.x)
        _y1=util.get_float(_p1.y)
        _y2=util.get_float(_p2.y)
        _deltax=abs(_x1-_x2)/2.0
        _deltay=abs(_y1-_y2)/2.0
        if(_x1<_x2):
            retX=_x1+_deltax
        else:
            retX=_x2+_deltax
        if(_y1<_y2):
            retY=_y1+_deltay
        else:
            retY=_y2+_deltay
        return retX,retY
    
    def getProjection(self,x,y):
        """
            get Projection of the point x,y in the line 
        """
        _x = util.get_float(x)
        _y = util.get_float(y)       
        p1=self.__p1
        p2=self.__p2
        p3=Point(_x, _y)
        v=pyGeoLib.Vector(p1,p2)
        v1=pyGeoLib.Vector(p1,p3)
        xp,yp=v1.Point().getCoords()
        pjPoint=v.Map(xp,yp).Point()
        x,y = pjPoint.getCoords()
        _x1,_y1=p1.getCoords()
        x=x+_x1
        y=y+_y1
        return x,y
        
    def mapCoords(self, x, y, tol=0.001):
        """
            Return the nearest Point on the Segment to a coordinate pair.
            The function has two required arguments:
            x: A Float value giving the 'x' coordinate
            y: A Float value giving the 'y' coordinate
            There is a single optional argument:
            tol: A float value equal or greater than 0.
            This function is used to map a possibly near-by coordinate pair to an
            actual Point on the Segment. If the distance between the actual
            Point and the coordinates used as an argument is less than the tolerance,
            the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        return util.map_coords(_x, _y, _x1, _y1, _x2, _y2, _t)

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not a Segment exists within a region.
            The four arguments define the boundary of an area, and the
            method returns True if the Segment lies within that area. If
            the optional argument fully is used and is True, then both
            endpoints of the Segment must lie within the boundary.
            Otherwise, the method returns False.
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
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        _pxmin = min(_x1, _x2)
        _pymin = min(_y1, _y2)
        _pxmax = max(_x1, _x2)
        _pymax = max(_y1, _y2)
        if ((_pxmax < _xmin) or
            (_pymax < _ymin) or
            (_pxmin > _xmax) or
            (_pymin > _ymax)):
            return False
        if fully:
            if ((_pxmin > _xmin) and
                (_pymin > _ymin) and
                (_pxmax < _xmax) and
                (_pymax < _ymax)):
                return True
            return False
        return util.in_region(_x1, _y1, _x2, _y2, _xmin, _ymin, _xmax, _ymax)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        """
            Clip the Segment using the Liang-Barsky Algorithm.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _x1, _y1 = self.__p1.getCoords()
        _x2, _y2 = self.__p2.getCoords()
        #
        # simple tests to reject line
        #
        if ((max(_x1, _x2) < _xmin) or
            (max(_y1, _y2) < _ymin) or
            (min(_x1, _x2) > _xmax) or
            (min(_y1, _y2) > _ymax)):
            return None
        #
        # simple tests to accept line
        #
        _coords = None
        if (_xmin < _x1 < _xmax and
            _xmin < _x2 < _xmax and
            _ymin < _y1 < _ymax and
            _ymin < _y2 < _ymax):
            _coords = (_x1, _y1, _x2, _y2)
        else:
            #
            # the Segment can be parameterized as
            #
            # x = u * (x2 - x1) + x1
            # y = u * (y2 - y1) + y1
            #
            # for u = 0, x => x1, y => y1
            # for u = 1, x => x2, y => y2
            #
            # The following is the Liang-Barsky Algorithm
            # for segment clipping
            #
            _dx = _x2 - _x1
            _dy = _y2 - _y1
            _P = [-_dx, _dx, -_dy, _dy]
            _q = [(_x1 - _xmin), (_xmax - _x1), (_y1 - _ymin), (_ymax - _y1)]
            _u1 = 0.0
            _u2 = 1.0
            _valid = True
            for _i in range(4):
                _pi = _P[_i]
                _qi = _q[_i]
                if abs(_pi) < 1e-10:
                    if _qi < 0.0:
                        _valid = False
                        break
                else:
                    _r = _qi/_pi
                    if _pi < 0.0:
                        if _r > _u2:
                            _valid = False
                            break
                        if _r > _u1:
                            _u1 = _r
                    else:
                        if _r < _u1:
                            _valid = False
                            break
                        if _r < _u2:
                            _u2 = _r
            if _valid:
                _coords = (((_u1 * _dx) + _x1),
                           ((_u1 * _dy) + _y1),
                           ((_u2 * _dx) + _x1),
                           ((_u2 * _dy) + _y1))
        return _coords

    def clone(self):
        """
            Create an identical copy of a Segment.
        """
        _cp1 = self.__p1.clone()
        _cp2 = self.__p2.clone()
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Segment(_cp1, _cp2, _st, _lt, _col, _th)

