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
from PythonCAD.Generic.Tools.point_tool import PointTool


class ACLineTool(PointTool):
    """
        A specialized tool for drawing ACLine objects.
        The ACLineTool class is derived from the PointTool class
        so it shares all the attributes and methods of that class.
        The ACLineTool class has the following addtional methods:
    """
    def __init__(self):
        super(ACLineTool, self).__init__()
        self.__angle = None

    def setLocation(self, p):
        """
            Set the location of the Tool.
            This method extends the Tool::setLocation() method.
        """
        super(ACLineTool, self).setLocation(p.point)
        _loc = self.getLocation()
        if _loc is None:
            return
        _x, _y = _loc.getCoords()
        _x1, _y1 = self.getPoint().point.getCoords()
        if abs(_y - _y1) < 1e-10: # horizontal
            self.__angle = 0.0
        elif abs(_x - _x1) < 1e-10: # vertical
            self.__angle = 90.0
        else:
            _slope = 180.0/math.pi * math.atan2((_y - _y1), (_x - _x1))
            self.__angle = util.make_angle(_slope)

    def setAngle(self, angle):
        """
            Set the angle for the ACLine.
            The argument 'angle' should be a float where -90.0 < angle < 90.0
        """
        _angle = util.make_angle(angle)
        self.__angle = _angle

    def getAngle(self):
        """
            Get the angle for the ACLine.
            This method returns a float.
        """
        return self.__angle

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends PointTool::reset().
        """
        super(ACLineTool, self).reset()
        self.__angle = None

    def create(self, image):
        """
            Create a new ACLine and add it to the image.
            This method overrides the Tool::create() method.
        """
        _p = self.getPoint().point
        if (_p is not None and
            self.__angle is not None):
            _active_layer = image.getActiveLayer()
            _x, _y = _p.getCoords()
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _pt = Point(_x, _y)
                _active_layer.addObject(_pt)
            else:
                _pt = _pts[0]
            _acl = ACLine(_pt, self.__angle)
            _active_layer.addObject(_acl)
            self.reset()

