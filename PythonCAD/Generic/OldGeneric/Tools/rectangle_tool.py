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


class RectangleTool(SegmentTool):
    """A Specialized tool for drawing rectangles.

The RectangleTool is derived from the SegmentTool, so it
shares all the methods and attributes of that class. A
RectangleTool creates four Segments in the shape of
a rectangle in the image.
    """
    def __init__(self):
        super(RectangleTool, self).__init__()

    def create(self, image):
        """Create Segments and add them to the image.

create(image)

This method overrides the SegmentTool::create() method.
        """
        _p1 = self.getFirstPoint().point
        _p2 = self.getSecondPoint().point
        if _p1 is not None and _p2 is not None:
            _x1, _y1 = _p1.getCoords()
            _x2, _y2 = _p2.getCoords()
            _active_layer = image.getActiveLayer()
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x1, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x1, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p3 = Point(_x2, _y2)
                _active_layer.addObject(_p3)
            else:
                _p3 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y1)
            if len(_pts) == 0:
                _p4 = Point(_x2, _y1)
                _active_layer.addObject(_p4)
            else:
                _p4 = _pts[0]
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
            _seg = Segment(_p1, _p2, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            _seg = Segment(_p2, _p3, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            _seg = Segment(_p3, _p4, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            _seg = Segment(_p4, _p1, _s, linetype=_l, color=_c, thickness=_t)
            _active_layer.addObject(_seg)
            self.reset()


            