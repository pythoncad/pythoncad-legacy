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


class RadialDimensionTool(DimensionTool):
    """A specialized tool for drawing RadialDimension objects.

The RadialDimensionTool class is derived from the DimensionTool class
and Tool class, so it shares all the attributes and methods of those
classes. The RadialDimensionTool class has the following additional
methods:

{set/get}DimObject(): Set/Get the circular object being dimensioned.
{set/get}DimPosition(): Set/Get the location of the dimension text.
    """
    def __init__(self):
        super(RadialDimensionTool, self).__init__()
        self.__cobj = None
        self.__position = None

    def setDimObject(self, cobj):
        """Store the Circle or Arc that the RadialDimension will describe.

setDimObject(cobj):

The argument 'cobj' must be either a Circle or Arc instance.
        """
        if not isinstance (cobj, (Circle, Arc)):
            raise TypeError, "Invalid Circle or Arc: " + `type(cobj)`
        if cobj.getParent() is None:
            raise ValueError, "Circle/Arc not found in a Layer."
        self.__cobj = cobj

    def getDimObject(self):
        """Return the object the RadialDimension will define.

getDimObject()

This method returns a tuple of two objects: the first object
is a Layer, the second object is either a Circle or an Arc
        """
        return self.__cobj.getParent(), self.__cobj

    def setDimPosition(self, x, y):
        """Store the point where the dimension text will be located.

setDimPosition(x, y)

Arguments 'x' and 'y' should be float values.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        self.__position = (_x, _y)

    def getDimPosition(self):
        """Retrieve where the dimension text should be placed.

getDimPosition()

This method returns a tuple containing the x/y coodindates defined
by the setDimPosition() call, or None if that method has not been
invoked.
        """
        return self.__position

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the reset() methods of its base classes.
        """
        super(RadialDimensionTool, self).reset()
        self.__cobj = None
        self.__position = None

    def makeDimension(self, image):
        """Create a RadialDimension based on the stored tool values.

makeDimension(image)

The argument 'image' is an image object where the dimension will
be used.
        """
        _cobj = self.__cobj
        _x, _y = self.__position
        if (_cobj is not None and
            _x is not None and
            _y is not None):
            _ds = image.getOption('DIM_STYLE')
            _rdim = dimension.RadialDimension(_cobj, _x, _y, _ds)
            self._setDimension(_rdim)
            self.setDimPrefs(image)

    def create(self, image):
        """Create a new RadialDimension and add it to the image.

create(image)

This method overrides the Tool::create() method.
        """
        _rdim = self.getDimension()
        if _rdim is not None:
            _pds = _rdim.getPrimaryDimstring()
            _pds.mute()
            try:
                _pds.setPrefix(image.getOption('RADIAL_DIM_PRIMARY_PREFIX'))
                _pds.setSuffix(image.getOption('RADIAL_DIM_PRIMARY_SUFFIX'))
            finally:
                _pds.unmute()
            _sds = _rdim.getSecondaryDimstring()
            _sds.mute()
            try:
                _sds.setPrefix(image.getOption('RADIAL_DIM_SECONDARY_PREFIX'))
                _sds.setSuffix(image.getOption('RADIAL_DIM_SECONDARY_SUFFIX'))
            finally:
                _sds.unmute()
            _rdim.setDiaMode(image.getOption('RADIAL_DIM_DIA_MODE'))
            _rdim.calcDimValues()
            image.addObject(_rdim)
            self.reset()

