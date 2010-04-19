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


class CircleTool(Tool):
    """
        A Specialized tool for drawing Circle objects.
        The CircleTool is derived from the Tool class, so it shares
        all the methods and attributes of that class. The CircleTool
        class has the following addtional methods:
    """
    def __init__(self):
        super(CircleTool, self).__init__()
        self.__center = None
        self.__radius = None
        self.__radiusPoint=None
    def setRadiusPoint(self,snapPoint):
        """
            set The radius point Cliched
        """
        if not isinstance(snapPoint,SnapPointStr):
            raise TypeError, "Invalid SnapPointStr type : " + `type(snapPoint)`
        self.__radiusPoint=snapPoint
    def getRadiusPoint(self):
        """
            Return the radiuspoint clicked by the user
        """
        return self.__radiusPoint
    radiusPoint=property(getRadiusPoint,setRadiusPoint,None,"Radius point cliched by the user")
    def setCenter(self, snapPoint):
        """
            Set the center point location of the circle.
            The arguments snapPoint give the location for the center
                of the circle.
        """
        if not isinstance(snapPoint,SnapPointStr):
            raise TypeError, "Invalid SnapPointStr type : " + `type(snapPoint)`
        self.__center = snapPoint

    def getCenter(self):
        """
            Get the center point location of the circle.
            This method returns the SnapPointStr stored with the setCenter()
            method, or None if that method has not been called.
        """
        return self.__center
    center =property(getCenter,setCenter,None,"center point")
    def setRadius(self, radius):
        """Set the radius of the circle.

setRadius(radius)

The argument 'radius' must be a float value greater than 0.0
        """
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        self.__radius = _r

    def getRadius(self):
        """Get the radius of the circle.

getRadius()

This method returns the value specified from the setRadius()
call, or None if that method has not been invoked.
        """
        return self.__radius

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends Tool::reset().
        """
        super(CircleTool, self).reset()
        self.__center = None
        self.__radius = None
        self.__radiusPoint=None

    def create(self, image):
        """
            Create a new Circle and add it to the image.
            This method overrides the Tool::create() method.
        """
        if (self.__center is not None and
            self.__radius is not None):
            _active_layer = image.getActiveLayer()
            _x, _y = self.__center.point.getCoords()
            _r = self.__radius
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _cp = Point(_x, _y)
                _active_layer.addObject(_cp)
            else:
                _cp = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _circle = Circle(_cp, _r, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _circle.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _circle.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _circle.setThickness(_t)
            _active_layer.addObject(_circle)
            self.reset()


            