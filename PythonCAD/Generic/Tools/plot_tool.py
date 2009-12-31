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


#
# printing/plotting tools
#

class PlotTool(Tool):
    """A tool for defining plot regions
    """
    def __init__(self):
        super(PlotTool, self).__init__()
        self.__c1 = None
        self.__c2 = None

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(PlotTool, self).reset()
        self.__c1 = None
        self.__c2 = None

    def setFirstCorner(self, x, y):
        """Store the first corner of the plot region.

setFirstCorner(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__c1 = (_x, _y)

    def getFirstCorner(self):
        """Return the first corner of the plot region.

getFirstCorner()
        """
        if self.__c1 is None:
            raise ValueError, "First corner not defined"
        return self.__c1
    
    def setSecondCorner(self, x, y):
        """Store the second corner of the plot region.

setSecondCorner(x, y)

Arguments 'x' and 'y' should be floats.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__c2 = (_x, _y)

    def getSecondCorner(self):
        """Return the second corner of the plot region.

getSecondCorner()
        """
        if self.__c2 is None:
            raise ValueError, "Second corner not defined"
        return self.__c2
    

    