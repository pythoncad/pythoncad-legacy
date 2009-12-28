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


class RegionTool(Tool):
    """A base class for a tool that can store a defined region.

The RegionTool class is designed to be a base class for tools that
need to store a rectangular region. The RegionTool class is derived
from the Tool class, so it shares all the attributes and methods of
that classs. The RegionTool class has the following additional methods:

{set/get}Region(): Set/Get a stored rectangular region
    """
    def __init__(self):
        super(RegionTool, self).__init__()
        self.__region = None

    def setRegion(self, xmin, ymin, xmax, ymax):
        """Store a rectangular region in the RegionTool.

setRegion(xmin, ymin, xmax, ymax)

xmin: The minimum x-coordinate value
ymin: The minimum y-coordinate value
xmax: The maximum x-coordinate value
ymax: The maximum y-coordinate value

All the arguments should be floats. If xmax < xmin or ymax < ymin
a ValueError exception is raised.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Invalid values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Invalid values: ymax < ymin"
        self.__region = (_xmin, _ymin, _xmax, _ymax)

    def getRegion(self):
        """Retrieve the stored rectangular region in the tool.

getRegion()

This method returns a tuple containing four float values:

(xmin, ymin, xmax, ymax)
        """
        return self.__region

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method resets the RegionTool region to None.
        """
        super(RegionTool, self).reset()
        self.__region = None


        