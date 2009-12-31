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


class HorizontalDimensionTool(LinearDimensionTool):
    """A specialized tool for drawing HorizontalDimension objects.

The HorizontalDimensionTool is derived from the LinearDimensionTool
and the Tool classes, so it shares all the attributes and methods of
those class.

There are no additional methods for the HorizontalDimension class.
    """
    def __init__(self):
        super(HorizontalDimensionTool, self).__init__()

    def makeDimension(self, image):
        """Create a HorizontalDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension willbe used.
        """
        _p1 = self.getFirstPoint()
        _p2 = self.getSecondPoint()
        _x, _y = self.getDimPosition()
        if (_p1 is not None and
            _p2 is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _hdim = dimension.HorizontalDimension(_p1, _p2, _x, _y, _ds)
            self._setDimension(_hdim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new HorizontalDimension and add it to the image.

create(image)

This method overrides the LinearDimensionTool::create() method.
        """
        _hdim = self.getDimension()
        if _hdim is not None:
            _pds = _hdim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _hdim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _hdim.calcDimValues()
            image.addObject(_hdim)
            self.reset()

