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
# classes for polyline objects
#

from __future__ import generators

import math

from Generic.Kernel.Entity.tolerance            import *
from Generic.Kernel.Entity.point                import Point
from Generic.Kernel.Entity.geometricalentity    import *

class Polyline(GeometricalEntity):
    """
        A class representing a polyline. A polyline is essentially
        a number of segments that connect end to end.
    """
    def __init__(self, plist):
        """
            Initialize a Polyline object.
            The argument 'plist' is a tuple or list containing Point objects.
            There should be two or more Points in the list.
        """
        if not isinstance(plist, (tuple, list)):
            raise TypeError, "Invalid Point list/tuple: " + `type(plist)`
        _pts = []
        _count = len(plist)
        if _count < 2:
            raise ValueError, "Invalid list count: %d" % _count
        for _i in range(_count):
            _obj = plist[_i]
            if not isinstance(_obj, Point):
                _obj = Point(plist[_i])
            _pts.append(_obj)
        _plist = []
        for _pt in _pts:
            try: # no exception means an equal point already found
                _i = _plist.index(_pt)
                _plist.append(_plist[_i])
            except: # no equal point found
                _plist.append(_pt)
        if len(_plist) < 2:
            raise ValueError, "Invalid point list: " + str(plist)
        self.__pts = _plist

    def __len__(self):
        return len(self.__pts)

    def __str__(self):
        return "Polyline" # fixme

    def __eq__(self, obj):
        """
            Compare two Polyline objects for equality.
        """
        if not isinstance(obj, Polyline):
            return False
        if obj is self:
            return True
        _val = False
        _ppts = obj.getPoints()
        _pcount = len(_ppts)
        _spts = self.__pts
        _scount = len(_spts)
        if _pcount == _scount:
            _val = True
            for _i in range(_scount):
                if _ppts[_i] != _spts[_i]:
                    _val = False
                    break
            if not _val: # check reversed point list of second polyline
                _val = True
                _ppts.reverse()
                for _i in range(_scount):
                    if _ppts[_i] != _spts[_i]:
                        _val = False
                        break
        return _val

    def __ne__(self, obj):
        """
            Compare two Polyline objects for inequality.
        """
        if not isinstance(obj, Polyline):
            return True
        if obj is self:
            return False
        _val = True
        _ppts = obj.getPoints()
        _pcount = len(_ppts)
        _spts = self.__pts
        _scount = len(_spts)
        if _pcount == _scount:
            _val = False
            for _i in range(_scount):
                if _ppts[_i] != _spts[_i]:
                    _val = True
                    break
            if _val: # check reversed point list of second polyline
                _val = False
                _ppts.reverse()
                for _i in range(_scount):
                    if _ppts[_i] != _spts[_i]:
                        _val = True
                        break
        return _val

    def getConstructionElements(self):
        """
            Get the construction element of the polyline
        """
        return tuple(self.__pts)

    def getValues(self):
        """
            Return values comprising the Polyline.
        """
        _data = {}
        _data['type']='polyline'
        _pts = []
        for _pt in self.__pts:
            #_pts.append(_pt.getID()) The id is not more present on geometrical entity
            _pts.append(_pt)
        _data['points']=_pts
        return _data

    def getPoints(self):
        """
            Get the points of the Polyline.
            This function returns a list containing all the Point
            objects that define the Polyline.
        """
        return self.__pts[:]

    def getNumPoints(self):
        """
            Return the number of Point objects defining the Polyline.
        """
        return len(self)

    def getPoint(self, i):
        """
            Return a single Point object used for defining the Polyline.
            The argument 'i' must be an integer, and its value represents
            the i'th Point used to define the Polyline.
        """
        return self.__pts[i]

    def setPoint(self, i, p):
        """
            Set a Point of the Polyline.
            The argument 'i' must be an integer, and its value represents
            the i'th Point used to define the Polyline. Argument 'p'
            must be a Point.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid Point for Polyline point: " + `type(p)`
        _pt = self.__pts[i]
        if _pt is not p:
            self.__pts[i] = p

    def addPoint(self, i, p):
        """
            Add a Point to the Polyline.
            The argument 'i' must be an integer, and argument 'p' must be a
            Point. The Point is added into the list of points comprising
            the Polyline as the i'th point.
        """
        if not isinstance(p, Point):
            raise TypeError, "Invalid Point for Polyline point: " + `type(p)`
        self.__pts.insert(i, p)


    def delPoint(self, i):
        """
            Remove a Point from the Polyline.
            The argument i represents the index of the point to remove from
            the list of points defining the Polyline. The point will be
            removed only if the polyline will still have at least two Points.
        """
        if len(self.__pts) > 2:
            _p = self.__pts[i]
            _pts = []
            for _pt in self.__pts:
                _pts.append((_pt.x, _pt.y))
            del self.__pts[i]

    def length(self):
        """
            Return the length of the Polyline.
            The length is the sum of the lengths of all the sub-segments
            in the Polyline
        """
        _length = 0.0
        _pts = self.__pts
        _count = len(_pts) - 1
        for _i in range(_count):
            _sublength = _pts[_i + 1] - _pts[_i]
            _length = _length + _sublength
        return _length

    def getBounds(self):
        """
            Return the bounding rectangle around a Polyline.
            This method returns a tuple of four values:
            (xmin, ymin, xmax, ymax)
        """
        _pts = self.__pts
        _pxmin = None
        _pymin = None
        _pxmax = None
        _pymax = None
        for _pt in _pts:
            _px, _py = _pt.getCoords()
            if _pxmin is None or _px < _pxmin:
                _pxmin = _px
            if _pymin is None or _py < _pymin:
                _pymin = _py
            if _pxmax is None or _px > _pxmax:
                _pxmax = _px
            if _pymax is None or _py > _pymax:
                _pymax = _py
        return _pxmin, _pymin, _pxmax, _pymax

    def mapCoords(self, x, y, tol=TOL):
        """
            Return the nearest Point on the Polyline by the x/y coordinates.

            x: A Float value giving the 'x' coordinate
            y: A Float value giving the 'y' coordinate

            There is a single optional argument:

            tol: A float value equal or greater than 0.0

            This function is used to map a possibly near-by coordinate pair to a
            Point object on the Polyline. If the distance between the actual
            Point and the coordinates used as an argument is less than the tolerance,
            the actual Point is returned. Otherwise, this method returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _count = len(self.__pts) - 1
        for _i in range(_count):
            _x1, _y1 = self.__pts[_i].getCoords()
            _x2, _y2 = self.__pts[_i + 1].getCoords()
            _pt = util.map_coords(_x, _y, _x1, _y1, _x2, _y2, _t)
            if _pt is not None:
                return _pt
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not a Polyline exists within a region.
            The four arguments define the boundary of an area, and the
            method returns True if the Polyline lies within that area. If
            the optional argument 'fully' is used and is True, then both
            endpoints of the Polyline must lie within the boundary.
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
        _pxmin, _pymin, _pxmax, _pymax = self.getBounds()
        if ((_pxmax < _xmin) or
            (_pxmin > _xmax) or
            (_pymax < _ymin) or
            (_pymin > _ymax)):
            return False
        if fully:
            if ((_pxmin > _xmin) and
                (_pymin > _ymin) and
                (_pxmax < _xmax) and
                (_pymax < _ymax)):
                return True
            return False
        _pts = self.__pts
        for _i in range(len(_pts) - 1):
            _x1, _y1 = _pts[_i].getCoords()
            _x2, _y2 = _pts[_i + 1].getCoords()
            if util.in_region(_x1, _y1, _x2, _y2, _xmin, _ymin, _xmax, _ymax):
                return True
        return False

    def clone(self):
        """
            Create an identical copy of a Polyline.
        """
        _cpts = []
        for _pt in self.__pts:
            _cpts.append(_pt.clone())
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Polyline(_cpts, _st, _lt, _col, _th)

