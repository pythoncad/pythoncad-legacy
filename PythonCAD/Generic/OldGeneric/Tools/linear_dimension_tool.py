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
from PythonCAD.Generic.Tools.dimension_tool import DimensionTool


class LinearDimensionTool(DimensionTool):
    """
        A specialized tool for drawing LinearDimension objects.
        The LinearDimensionTool is derived from the DimensionTool and
        Tool, class, so it shares all the attributes and methods of those classes.
        The LinearDimensionTool class has the following addtional methods:
        {set/get}FirstPoint(): Set/Get the first point in the LinearDimension
        {set/get}SecondPoint(): Set/Get the second point in the LinearDimension.
        {set/get}DimPosition(): Set/Get the location of the dimension text.
    """
    def __init__(self):
        super(LinearDimensionTool, self).__init__()
        self.__p1 = None
        self.__p2 = None
        self.__position = None

    def setFirstPoint(self, p):
        """
            Store the first point for the LinearDimension.
            The argument 'p' must be a Point instance.
        """
        if not isinstance (p, Point):
            raise TypeError, "Invalid Point: " + `type(p)`
        if p.getParent() is None:
            raise ValueError, "Point not found in a Layer."
        self.__p1 = p

    def getFirstPoint(self):
        """Return the first point for the LinearDimension.

getFirstPoint()

This method returns a tuple of two objects: the first object
is a Layer, the second object is a Point.
        """
        return self.__p1

    def setSecondPoint(self, p):
        """Store the second point for the LinearDimension.

setSecondPoint(p):

The argument 'p' must be a Point instance.
        """
        if self.__p1 is None:
            raise ValueError, "First point not set for LinearDimension."
        if not isinstance (p, Point):
            raise TypeError, "Invalid Point: " + `type(p)`
        if p.getParent() is None:
            raise ValueError, "Point not found in a Layer."
        self.__p2 = p

    def getSecondPoint(self):
        """Return the second point for the LinearDimension.

getSecondPoint()

This method returns a tuple of two objects: the first object
is a Layer, the second object is a Point.
        """
        return self.__p2

    def setDimPosition(self, x, y):
        """Store the point where the dimension text will be located.

setDimPosition(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__position = (_x, _y)

    def getDimPosition(self):
        """
            Retrieve where the dimension text should be placed.
            This method returns a tuple containing the x/y coodindates defined
            by the setDimPosition() call, or None if that method has not been invoked.
        """
        return self.__position

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends the reset() methods of its base classes.
        """
        super(LinearDimensionTool, self).reset()
        self.__p1 = None
        self.__p2 = None
        self.__position = None

    def makeDimension(self, image):
        """
            Create a LinearDimension based on the stored tool values
            The argument 'image' is an image object where the dimension will be used.
        """
        _p1 = self.__p1
        _p2 = self.__p2
        _x, _y = self.__position
        if (_p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _ldim = dimension.LinearDimension(_p1, _p2, _x, _y, _ds)
            self._setDimension(_ldim)
            self.setDimPrefs(image)

    def create(self, image):
        """
            Create a new LinearDimension and add it to the image.
            This method overrides the Tool::create() method.
        """
        _ldim = self.getDimension()
        if _ldim is not None:
            _pds = _ldim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _ldim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _ldim.calcDimValues()
            image.addObject(_ldim)
            self.reset()

