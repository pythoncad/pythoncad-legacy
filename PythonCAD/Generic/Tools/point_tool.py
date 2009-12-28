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

##from PythonCAD.Generic.segment import Segment
##from PythonCAD.Generic.circle import Circle
##from PythonCAD.Generic.arc import Arc
##from PythonCAD.Generic.leader import Leader
##from PythonCAD.Generic.polyline import Polyline
##from PythonCAD.Generic.hcline import HCLine
##from PythonCAD.Generic.vcline import VCLine
##from PythonCAD.Generic.acline import ACLine
##from PythonCAD.Generic.cline import CLine
##from PythonCAD.Generic.ccircle import CCircle
##from PythonCAD.Generic.text import TextStyle, TextBlock
##from PythonCAD.Generic import dimension
##from PythonCAD.Generic.layer import Layer
##from PythonCAD.Generic import tangent
##from PythonCAD.Generic import intersections 
##from PythonCAD.Generic.segjoint import Chamfer, Fillet
##from PythonCAD.Generic import pyGeoLib 
##from PythonCAD.Generic.snap import SnapPointStr

from PythonCAD.Generic import error
from PythonCAD.Generic.Tools.tool import Tool


class PointTool(Tool):
    """
        A specialized tool for drawing Point objects.
        The PointTool class is derived from the Tool class, so it
        shares the methods and attributes of that class. The PointTool
        class has the following additional methods:
    """
    def __init__(self):
        super(PointTool, self).__init__()
        self.__point = None

    def setPoint(self, p):
        """
            Store a Point in the tool
            Argument: p should be Point
        """
        self.__point = p

    def getPoint(self):
        """
            Get the stored Point from the tool
            This method returns a Poiny containing the values passed in
            with the setPoint() method, or None if that method has not
            been invoked.
        """
        return self.__point

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends Tool::reset().
        """
        super(PointTool, self).reset()
        self.__point = None

    def create(self, image):
        """
            Create a new Point and add it to the image.
            This method overrides the Tool::create() method.
        """
        if self.__point is not None:
            _active_layer = image.getActiveLayer()
            _active_layer.addObject(self.__point.point)
            self.reset()

            