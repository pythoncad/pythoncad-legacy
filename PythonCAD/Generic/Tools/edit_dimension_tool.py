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
from PythonCAD.Generic.Tools.region_tool import RegionTool


class EditDimensionTool(RegionTool):
    """A specialized class for changing attributes of Dimension instances.

The EditDimensionTool class is derived from the RegionTool class,
so it shares all the attributes and methods of that class. The
EditDimensionTool class has the following additional methods:

{set/get}Attribute(): Set/Get the desired attribute
{set/get}Value(): Set/Get the new entity color.
    """
    def __init__(self):
        super(RegionTool, self).__init__()
        self.__attr = None
        self.__value = None

    def setAttribute(self, attr):
        """Define which attribute the tool is modifying.

setAttribute(attr)

Argument 'attr' should be one of the following:

'setEndpointType', 'setEndpointSize', 'setDualDimMode', 'setDualModeOffset',
'setOffset', 'setExtension', 'setColor', 'setThickness', 'setScale'
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        if attr not in ('setEndpointType', 'setEndpointSize',
                        'setDualDimMode', 'setDualModeOffset',
                        'setOffset', 'setExtension', 'setColor',
                        'setThickness', 'setScale'):
             raise ValueError, "Invalid attribute: " + attr
        self.__attr = attr

    def getAttribute(self):
        """Return the specified attribute.

getAttribute()

If called before invoking setAttribute(), this method raises a ValueError.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        return self.__attr

    def setValue(self, val):
        """Store the new value of the entity attribute.

setValue(val)

Argument 'val' depends on the type of attribute defined for the
tool. If no attribute is defined this method raises a ValueError.
Invoking this method with 'None' as an argument sets the tool
to restore the default attribute value.
        """
        if self.__attr is None:
            raise ValueError, "Tool attribute not defined."
        _a = self.__attr
        _val = None
        if val is not None:
            if _a == 'setEndpointType':
                if (val != dimension.Dimension.DIM_ENDPT_NONE and
                    val != dimension.Dimension.DIM_ENDPT_ARROW and
                    val != dimension.Dimension.DIM_ENDPT_FILLED_ARROW and
                    val != dimension.Dimension.DIM_ENDPT_SLASH and
                    val != dimension.Dimension.DIM_ENDPT_CIRCLE):
                    raise ValueError, "Invalid endpoint value: " + str(val)
                _val = val
            elif _a == 'setEndpointSize':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid endpoint size: %g" % _val
                _val = val
            elif _a == 'setDualDimMode':
                util.test_boolean(val)
                _val = val
            elif _a == 'setDualModeOffset':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid offset length: %g" % _val
                _val = val
            elif _a == 'setOffset':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid offset length: %g" % _val
                _val = val
            elif _a == 'setExtension':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid extension length: %g" % _val
                _val = val
            elif _a == 'setColor':
                if not isinstance(val, color.Color):
                    raise TypeError, "Invalid Color: " + `type(val)`
                _val = val
            elif _a == 'setThickness':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid thickness: %g" % _val
            elif _a == 'setScale':
                _val = util.get_float(val)
                if _val < 0.0:
                    raise ValueError, "Invalid scale: %g" % _val
            else:
                raise ValueError, "Unexpected attribute: " + _a
        self.__value = _val

    def getValue(self):
        """Get the stored attribute value.

getValue()

This method returns the value stored in setValue() or None.
        """
        return self.__value

