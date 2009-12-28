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


class MoveTool(RegionTool):
    """A specialized class for moving objects.

The MoveTool class is derived from the Tool and RegionTool classes,
so it shares all the attributes and methods of those classes. The
MoveTool class has the following additional methods:

{set/get}Distance(): Set/Get the values to move objects.
    """
    def __init__(self):
        super(MoveTool, self).__init__()
        self.__distance = None

    def setDistance(self, x, y):
        """Store the distance to move objects in the tool.

setDistance(x, y)

Arguments 'x' and 'y' should be floats, and represent the amount
to move objects in the x-coordinate and y-coordinate axes.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__distance = (_x, _y)

    def getDistance(self):
        """Get the displacement stored in the tool.

getDistance()

This method returns a tuple containing two float values.

(xdisp, ydisp)

If this method is called before the setDistance() method is
used, a ValueError exception is raised.
        """
        if self.__distance is None:
            raise ValueError, "No distance stored in tool."
        return self.__distance

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the reset() method of its base classes
        """
        super(MoveTool, self).reset()
        self.__distance = None


        