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


class TangentCircleTool(Tool):
    """
        A specialized class for creating tangent construction circles.
        This class is meant to be a base class for tools that create tangent
        construction circles. It is derived from the tool class so it shares
        all the attributes and methods of that class. This class has the
        following additional methods:
    """
    def __init__(self):
        super(TangentCircleTool, self).__init__()
        self.__center = None
        self.__radius = None
        self.__rect = None

    def setCenter(self, x, y):
        """Store the tangent circle center point in the tool.

setCenter(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__center = (_x, _y)

    def getCenter(self):
        """Return the center of the tangent circle.

getCenter()

This method returns a tuple holding two floats, the first
is the 'x' coordinate of the center, the second is the 'y'
coordinate. If the tool has not yet been invoked with a
setLocation() call, this method returns None.
        """
        return self.__center

    def setRadius(self, radius):
        """Store the radius in the tool.

setRadius(radius)

Argument 'radius' should be a float.
        """
        _radius = util.get_float(radius)
        self.__radius = _radius

    def getRadius(self):
        """Return the center of the tangent circle.

getRadius()

This method returns a float giving the radius of the tangent
circle, or None if the radius is not set.
        """
        return self.__radius

    def setPixelRect(self, xmin, ymin, width, height):
        """Store the screen coordinates used to draw the circle.

setPixelRect(xmin, ymin, width, height)

All the arguments should be integer values.
        """
        _xmin = xmin
        if not isinstance(_xmin, int):
            _xmin = int(xmin)
        _ymin = ymin
        if not isinstance(_ymin, int):
            _ymin = int(ymin)
        _width = width
        if not isinstance(_width, int):
            _width = int(_width)
        _height = height
        if not isinstance(_height, int):
            _height = int(height)
        self.__rect = (_xmin, _ymin, _width, _height)

    def getPixelRect(self):
        """Return the screen boundary of the circle to draw

getPixelRect(self)

This method will return a tuple holding four integer values:

xmin, ymin, width, height

If the rectangle has not been set by calling setPixelRect(), then
this method will return None.
        """
        return self.__rect

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(TangentCircleTool, self).reset()
        self.__center = None
        self.__radius = None
        self.__rect = None

    def create(self, image):
        """Create a new CCircle and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _active_layer = image.getActiveLayer()
        _x, _y = self.__center
        _radius = self.__radius
        _pts = _active_layer.find('point', _x, _y)
        if len(_pts) == 0:
            _cp = Point(_x, _y)
            _active_layer.addObject(_cp)
        else:
            _cp = _pts[0]
        _ccircle = CCircle(_cp, _radius)
        _active_layer.addObject(_ccircle)
        self.reset()


        