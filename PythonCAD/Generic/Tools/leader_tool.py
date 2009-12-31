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


class LeaderTool(Tool):
    """
        A specialized tool for drawing Leader objects.
        The LeaderTool class is derived from the Tool class, so it
        shares the methods and attributes of that class. 
    """
    def __init__(self):
        super(LeaderTool, self).__init__()
        self.__start_point = None
        self.__mid_point = None
        self.__end_point = None

    def setFirstPoint(self, p):
        """Set the first point used to define the Leader.

setFirstPoint(x, y)

Arguments 'x' and 'y' give the location of a point.
        """

        self.__start_point = p

    def getFirstPoint(self):
        """Get the first point used to define the Leader.

getFirstPoint()

This method returns a tuple holding the values used when the
setFirstPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__start_point

    def setMidPoint(self, p):
        """Set the second point used to define the Leader.

setMidPoint(x, y)

Arguments 'x' and 'y' give the location of a point. If the
first point has not been set this method raises a ValueError.
        """
        if self.__start_point is None:
            raise ValueError, "First point not set in LeaderTool."
        self.__mid_point =p

    def getMidPoint(self):
        """Get the second point used to define the Leader.

getMidPoint()

This method returns a tuple holding the values used when the
setMidPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__mid_point

    def setFinalPoint(self,p):
        """Set the first point used to final point of the Leader.
            Arguments 'x' and 'y' give the location of a point. This method
            raises an error if the first point or second point have not been
            set.
        """
        if self.__start_point is None:
            raise ValueError, "First point not set in LeaderTool."
        if self.__mid_point is None:
            raise ValueError, "Second point not set in LeaderTool."
        self.__end_point = p

    def getFinalPoint(self):
        """Get the third point used to define the Leader.

getFinalPoint()

This method returns a tuple holding the values used when the
setFinalPoint() method was called, or None if that method has
not yet been used.
        """
        return self.__end_point

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(LeaderTool, self).reset()
        self.__start_point = None
        self.__mid_point = None
        self.__end_point = None

    def create(self, image):
        """Create a new Leader and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        if (self.__start_point is not None and
            self.__mid_point is not None and
            self.__end_point is not None):
            _active_layer = image.getActiveLayer()
            _x1, _y1 = self.__start_point.point.getCoords()
            _x2, _y2 = self.__mid_point.point.getCoords()
            _x3, _y3 = self.__end_point.point.getCoords()
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
            _pts = _active_layer.find('point', _x3, _y3)
            if len(_pts) == 0:
                _p3 = Point(_x3, _y3)
                _active_layer.addObject(_p3)
            else:
                _p3 = _pts[0]
            _size = image.getOption('LEADER_ARROW_SIZE')
            _s = image.getOption('LINE_STYLE')
            _leader = Leader(_p1, _p2, _p3, _size, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _leader.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _leader.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _leader.setThickness(_t)
            _active_layer.addObject(_leader)
            self.reset()

            