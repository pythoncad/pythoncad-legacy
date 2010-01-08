#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
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
# tool stuff
#

import math
import types
import array

from PythonCAD.Generic import util
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic import dimension
from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic import tangent
from PythonCAD.Generic import intersections 
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import pyGeoLib 
from PythonCAD.Generic.snap import SnapPointStr

from PythonCAD.Generic import error
from PythonCAD.Generic.Tools.tool import Tool


class PolygonTool(Tool):
    """
        A specialized to for creating Polygons from Segments.
        The PolygonTool will create an uniformly sized polygon from Segment
        entities. The minimum number of sides is three, creating an equilateral
        triangle. There is no maximum number of sides, though realistically any
        polygon with more than 20 or so sides is unlikely to be drawn. As
        the PolygonTool is derived from the Tool class, it shares all the attributes
        and method of that class. 
    """
    def __init__(self):
        super(PolygonTool, self).__init__()
        self.__nsides = None
        self.__increment = None
        self.__external = False
        self.__center = None
        self.__xpts = array.array("d")
        self.__ypts = array.array("d")

    def setSideCount(self, count):
        """
            Set the number of sides of the polygon to create.
            Argument "count" should be an integer value greater than 2.
        """
        _count = count
        if not isinstance(_count, int):
            _count = int(count)
        if _count < 3:
            raise ValueError, "Invalid count: %d" % _count
        self.__nsides = _count
        self.__increment = (360.0/float(_count)) * (math.pi/180.0)
        for _i in range(_count):
            self.__xpts.insert(_i, 0.0)
            self.__ypts.insert(_i, 0.0)

    def getSideCount(self):
        """
            Get the number of sides of the polygon to be created.
            A ValueError exception is raised if the side count has not been
            set with setSideCount()
        """
        if self.__nsides is None:
            raise ValueError, "No side count defined."
        return self.__nsides

    def setExternal(self):
        """
            Create the polygon on the outside of a reference circle.
            By default the polygon is drawing completely contained within a
            circle. Invoking this method will created the polygon so that all
            sides are outside the circle.
        """
        self.__external = True

    def getExternal(self):
        """
            Test if the polygon will be created outside a circle.
            If the setExternal() method has been called, this method will
            return True. By default this method will return False.
        """
        return self.__external

    def setCenter(self, p):
        """Define the center of the polygon.

setCenter(x, y)

Arguments 'x' and 'y' should be float values.
        """
        self.__center = p

    def getCenter(self):
        """Retrieve the center of the polygon to be created.

getCenter()

This method returns a tuple holding two float values containing
the 'x' and 'y' coordinates of the polygon center. A ValueError
is raised if the center has not been set with a prior call to setCenter().
        """
        if self.__center is None:
            raise ValueError, "Center is undefined."
        return self.__center

    def getCoord(self, i):
        """Get one of the coordinates of the polygon corners.

getCoord(i)

Argument "i" should be an integer value such that:

0 <= i <= number of polygon sides
        """
        _x = self.__xpts[i]
        _y = self.__ypts[i]
        return _x, _y

    def setLocation(self, p):
        """Set the tool location.

setLocation(x, y)

This method extends Tool::setLocation() and calculates the polygon
points.
        """
        super(PolygonTool, self).setLocation(p.point)
        _x, _y = self.getLocation().getCoords()
        _count = self.__nsides
        _inc = self.__increment
        if self.__external:
            _offset = _inc/2.0
        else:
            _offset = 0.0
        _cx, _cy = self.__center.point.getCoords()
        _xsep = _x - _cx
        _ysep = _y - _cy
        _angle = math.atan2(_ysep, _xsep) + _offset
        _rad = math.hypot(_xsep, _ysep)/math.cos(_offset)
        _xp = self.__xpts
        _yp = self.__ypts
        for _i in range(_count):
            _xp[_i] = _cx + (_rad * math.cos(_angle))
            _yp[_i] = _cy + (_rad * math.sin(_angle))
            _angle = _angle + _inc

    def create(self, image):
        """Create a Polygon from Segments and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if len(self.__xpts):
            _active_layer = image.getActiveLayer()
            _s = image.getOption('LINE_STYLE')
            _l = image.getOption('LINE_TYPE')
            if _l == _s.getLinetype():
                _l = None
            _c = image.getOption('LINE_COLOR')
            if _c == _s.getColor():
                _c = None
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) < 1e-10:
                _t = None
            _count = self.__nsides
            _xp = self.__xpts
            _yp = self.__ypts
            _x = _xp[0]
            _y = _yp[0]
            #
            # find starting point ...
            #
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _p0 = Point(_x, _y)
                _active_layer.addObject(_p0)
            else:
                _p0 = _pts[0]
            #
            # make segments for all the points ...
            #
            _p1 = _p0
            for _i in range(1, _count):
                _x = _xp[_i]
                _y = _yp[_i]
                _pts = _active_layer.find('point', _x, _y)
                if len(_pts) == 0:
                    _pi = Point(_x, _y)
                    _active_layer.addObject(_pi)
                else:
                    _pi = _pts[0]
                _seg = Segment(_p1, _pi, _s, linetype=_l, color=_c, thickness=_t)
                _active_layer.addObject(_seg)
                _p1 = _pi
            #
            # now add closing segment ...
            #
            _seg = Segment(_p1, _p0, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            self.reset()

    def reset(self):
        """Restore the PolygonTool to its original state.

reset()

This method extends Tool::reset()
        """
        super(PolygonTool, self).reset()
        # self.__nsides = None
        # self.__increment = None
        # self.__external = False # make this adjustable?
        self.__center = None
        for _i in range(self.__nsides):
            self.__xpts[_i] = 0.0
            self.__ypts[_i] = 0.0

            