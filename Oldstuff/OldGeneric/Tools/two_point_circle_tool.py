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
from PythonCAD.Generic.Tools.circle_tool import CircleTool


class TwoPointCircleTool(CircleTool):
    """A specialized class for drawing Circles between two points.

The TwoPointCircleTool class is derived from the CircleTool
class, so it shares all the methods and attributes of that
class. The TwoPointCircleTool class has the following addtional
methods:

{set/get}FirstPoint(): Set/Get the first point used to define the circle.
{set/get}SecondPoint(): Set/Get the second point used to define the circle.
    """
    def __init__(self):
        super(TwoPointCircleTool, self).__init__()
        self.__first_point = None
        self.__second_point = None

    def setFirstPoint(self, p):
        """
            Set the first point used to define the location of the circle.
            Arguments p give the location of a point.
        """
        self.__first_point = p

    def getFirstPoint(self):
        """Get the first point used to define the location of the circle.

getFirstPoint()

This method returns a tuple holding the values used when the
setFirstPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__first_point

    def setSecondPoint(self, p):
        """Set the second point used to define the location of the circle.

setSecondPoint(x, y)

Arguments 'x' and 'y' give the location of a point. Invoking
this method before the setFirstPoint() method will raise a
ValueError.
        """
        _x,_y=p.point.getCoords()
        if self.__first_point is None:
            raise ValueError, "First point is not set"
        _x1, _y1 = self.__first_point.point.getCoords()
        _xc = (_x + _x1)/2.0
        _yc = (_y + _y1)/2.0
        _radius = math.hypot((_x - _x1), (_y - _y1))/2.0
        _strPoint=SnapPointStr("Freepoint",Point(_xc,_yc),None)
        self.setCenter(_strPoint)
        self.setRadius(_radius)
        self.__second_point = (_x, _y)

    def getSecondPoint(self):
        """Get the second point used to define the location of the circle.

getSecondPoint()

This method returns a tuple holding the values used when the
setSecondPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__second_point

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends CircleTool::reset().
        """
        super(TwoPointCircleTool, self).reset()
        self.__first_point = None
        self.__second_point = None


        