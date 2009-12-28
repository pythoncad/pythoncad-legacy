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
from PythonCAD.Generic.Tools.segment_tool import SegmentTool


class CLineTool(SegmentTool):
    """A specialized tool for drawing CLine objects.

The CLineTool class is derived from the SegmentTool class,
so it shares all the attributes and methods of that class.

There are no extra methods for the CLineTool class.
    """
    def __init__(self):
        super(CLineTool, self).__init__()

    def create(self, image):
        """Create a new CLine and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _p1 = self.getFirstPoint().point
        _p2 = self.getSecondPoint().point
        if _p1 is not None and _p2 is not None:
            _active_layer = image.getActiveLayer()
            _x1, _y1 = _p1.getCoords()
            _x2, _y2 = _p2.getCoords()
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x2, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _cline = CLine(_p1, _p2)
            _active_layer.addObject(_cline)
            self.reset()

