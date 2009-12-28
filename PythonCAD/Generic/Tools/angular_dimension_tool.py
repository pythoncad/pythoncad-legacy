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
from PythonCAD.Generic.Tools.linear_dimension_tool import LinearDimensionTool


class AngularDimensionTool(LinearDimensionTool):
    """A specialized tool for drawing AngularDimension objects.

The AngularDimensionTool class is derived from the LinearDimensionTool
class, so it shares all the attributes and methods of that class. The
AngularDimensionTool class has the following additional methods:

{set/get}VertexPoint(): Set/Get the vertex point used by the dimension
    """
    def __init__(self):
        super(AngularDimensionTool, self).__init__()
        self.__vp = None

    def setVertexPoint(self, p):
        """Store the vertex point for the AngularDimension.

setVertexPoint(p):

The argument 'p' must be a Point instance.
        """
        if not isinstance (p, Point):
            raise TypeError, "Invalid Point: " + `type(p)`
        if p.getParent() is None:
            raise ValueError, "Point not found in layer."
        self.__vp = p

    def getVertexPoint(self):
        """Return the vertex point for the AngularDimension.

getVertexPoint()

This method returns a tuple of two objects: the first object
is a Layer, the second object is a Point.
        """

        return self.__vp

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends LinearDimensionTool::reset().
        """
        super(AngularDimensionTool, self).reset()
        self.__vp = None

    def makeDimension(self, image):
        """Create an AngularDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension will be used.
        """
        _vp = self.__vp
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        _x, _y = self.getDimPosition()
        if (_vp is not None and
            _p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _adim = dimension.AngularDimension(_vp, _p1, _p2, _x, _y, _ds)
            self._setDimension(_adim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new AngularDimension and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _adim = self.getDimension()
        if _adim is not None:
            _pds = _adim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('ANGULAR_DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('ANGULAR_DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _adim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('ANGULAR_DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('ANGULAR_DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _adim.calcDimValues()
            image.addObject(_adim)
            self.reset()

