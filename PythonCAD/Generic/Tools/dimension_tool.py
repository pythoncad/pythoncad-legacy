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


class DimensionTool(Tool):
    """A base class for tools creating Dimension objects.

The DimensionTool class is meant to be a base class for classes
that will create Dimension objects. The DimensionTool class is
derived from the Tool class, so it shares all the attributes and
methods of that class. The DimensionTool class has the following
additional methods:

setDimension(): Store a dimension object in the tool
getDimension(): Retrieve a stored dimension object.
setDimPrefs(): Apply the current dimension preferences on a stored dimension.
    """
    def __init__(self):
        super(DimensionTool, self).__init__()
        self.__dim = None

    def _setDimension(self, dim):
        """Store a dimension in the tool.

setDimension(dim)

The argument 'dim' must be a Dimension object.
        """
        if not isinstance(dim, dimension.Dimension):
            raise TypeError, "Invalid Dimension type: " + `type(dim)`
        self.__dim = dim

    def getDimension(self):
        """Retrieve the stored dimension object from the tool.

getDimension()

This method returns the stored Dimension or None.
        """
        return self.__dim

    def setDimPrefs(self, image):
        """Apply the current dimension options to the stored dimension.

setDimPrefs(image)

The argument 'image' is an image option in which the current dimension
preferences are retrieved.
        """
        _dim = self.__dim
        if _dim is None:
            raise ValueError, "No dimension stored in tool."
        _pds = _dim.getPrimaryDimstring()
        _pds.mute()
        _pds.setFamily(image.getOption('DIM_PRIMARY_FONT_FAMILY'))
        _pds.setWeight(image.getOption('DIM_PRIMARY_FONT_WEIGHT'))
        _pds.setStyle(image.getOption('DIM_PRIMARY_FONT_STYLE'))
        _pds.setColor(image.getOption('DIM_PRIMARY_FONT_COLOR'))
        _pds.setSize(image.getOption('DIM_PRIMARY_TEXT_SIZE'))
        _pds.setAlignment(image.getOption('DIM_PRIMARY_TEXT_ALIGNMENT'))
        _pds.setPrecision(image.getOption('DIM_PRIMARY_PRECISION'))
        _pds.setUnits(image.getOption('DIM_PRIMARY_UNITS'))
        _pds.setPrintZero(image.getOption('DIM_PRIMARY_LEADING_ZERO'))
        _pds.setPrintDecimal(image.getOption('DIM_PRIMARY_TRAILING_DECIMAL'))
        _pds.unmute()
        _sds = _dim.getSecondaryDimstring()
        _sds.mute()
        _sds.setFamily(image.getOption('DIM_SECONDARY_FONT_FAMILY'))
        _sds.setWeight(image.getOption('DIM_SECONDARY_FONT_WEIGHT'))
        _sds.setStyle(image.getOption('DIM_SECONDARY_FONT_STYLE'))
        _sds.setColor(image.getOption('DIM_SECONDARY_FONT_COLOR'))
        _sds.setSize(image.getOption('DIM_SECONDARY_TEXT_SIZE'))
        _sds.setAlignment(image.getOption('DIM_SECONDARY_TEXT_ALIGNMENT'))
        _sds.setPrecision(image.getOption('DIM_SECONDARY_PRECISION'))
        _sds.setUnits(image.getOption('DIM_SECONDARY_UNITS'))
        _sds.setPrintZero(image.getOption('DIM_SECONDARY_LEADING_ZERO'))
        _sds.setPrintDecimal(image.getOption('DIM_SECONDARY_TRAILING_DECIMAL'))
        _sds.unmute()
        _dim.setOffset(image.getOption('DIM_OFFSET'))
        _dim.setExtension(image.getOption('DIM_EXTENSION'))
        _dim.setColor(image.getOption('DIM_COLOR'))
        _dim.setPosition(image.getOption('DIM_POSITION'))
        _dim.setEndpointType(image.getOption('DIM_ENDPOINT'))
        _dim.setEndpointSize(image.getOption('DIM_ENDPOINT_SIZE'))
        _dim.setDualDimMode(image.getOption('DIM_DUAL_MODE'))
    
    def reset(self):
        """
            Restore the tool to its initial state.
            This method sets the DimensionTool dimension to None.
        """
        super(DimensionTool, self).reset()
        self.__dim = None
        self.__tempPoint=[]

