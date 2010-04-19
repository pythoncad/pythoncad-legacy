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
from PythonCAD.Generic.Tools.region_tool import RegionTool


class RotateTool(RegionTool):
    """A specialized class for rotating objects.

The RotateTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes. The
Rotateool class has the following additional methods:

{set/get}RotationPoint(): Set/Get the point objects are rotated around
{set/get}Angle(): Set/Get the angle of rotation
    """
    def __init__(self):
        super(RotateTool, self).__init__()
        self.__rp = None
        self.__angle = None

    def setRotationPoint(self, x, y):
        """Set the coordinates the entities will rotate around

setRotationPoint(x, y)

Arguments 'x' and 'y' should be floats
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__rp = (_x, _y)

    def getRotationPoint(self):
        """Get the point objects will rotate around

getRotationPoint()

This method returns a tuple of two floats or None if the rotation
point has not be defined with setRotationPoint()
        """
        return self.__rp

    def setAngle(self, angle):
        """Set the angle of rotation.

setAngle(angle)

Argument 'angle' should be a float value. The value is normalized
so that abs(angle) < 360.0.
        """
        _a = util.get_float(angle)
        self.__angle = math.fmod(_a, 360.0)

    def getAngle(self):
        """Get the angle of rotation.

getAngle()

This method returns a float or None if the angle has not been
set with setAngle()
        """
        return self.__angle

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(RotateTool, self).reset()
        self.__rp = None
        self.__angle = None

