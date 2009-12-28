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


class ArcTool(CircleTool):
    """
        A specialized tool for drawing Arc objects.
        The ArcTool is Derived from the CircleTool class, so it shares
        all the attributes and methods of that class. The ArcTool class
        has the following addtional methods:
    """
    def __init__(self):
        super(ArcTool, self).__init__()
        self.__start_angle = None
        self.__end_angle = None

    def setStartAngle(self, angle):
        """
            Set the start angle of the arc.
            The argument 'angle' should be a float value between 0.0 and 360.0
        """
        _angle = util.make_c_angle(angle)
        self.__start_angle = _angle

    def getStartAngle(self):
        """
            Return the start angle of the arc.
            This method returns the value defined in the previous setStartAngle()
            call, or None if that method has not been called.
        """
        return self.__start_angle

    def setEndAngle(self, angle):
        """
            Set the start angle of the arc.
            The argument 'angle' should be a float value between 0.0 and 360.0
        """
        _angle = util.make_c_angle(angle)
        self.__end_angle = _angle

    def getEndAngle(self):
        """
            Return the end angle of the arc.
            This method returns the value defined in the previous setEndAngle()
            call, or None if that method has not been called.
        """
        return self.__end_angle
        
    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends CircleTool::reset().
        """
        super(ArcTool, self).reset()
        self.__start_angle = None
        self.__end_angle = None

    def create(self, image):
        """
            Create a new Arc and add it to the image.
            This method overrides the CircleTool::create() method.
        """
        _center = self.getCenter()
        _radius = self.getRadius()
        _sa = self.__start_angle
        _ea = self.__end_angle
        if (_center is not None and
            _radius is not None and
            _sa is not None and
            _ea is not None):
            _active_layer = image.getActiveLayer()
            _x, _y = _center.point.getCoords()
            _pts = _active_layer.find('point', _x, _y)
            if len(_pts) == 0:
                _cp = Point(_x, _y)
                _active_layer.addObject(_cp)
            else:
                _cp = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _arc = Arc(_cp, _radius, _sa, _ea, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _arc.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _arc.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _arc.setThickness(_t)
            for _ep in _arc.getEndpoints():
                _ex, _ey = _ep
                _pts = _active_layer.find('point', _ex, _ey)
                if len(_pts) == 0:
                    _lp = Point(_ex, _ey)
                    _active_layer.addObject(_lp)
            _active_layer.addObject(_arc)
            self.reset()

