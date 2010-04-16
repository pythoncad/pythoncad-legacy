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
from PythonCAD.Generic.Tools.text_tool import TextTool


class EditDimStringTool(TextTool):
    """A specialized class for modifying DimString instances in Dimensions.

The EditDimStringTool class is derived from the TextTool class, so it
shares the attributes and methods of that class. The TextTool class has
the following additional methods:

{set/get}Primary(): Set/Get the DimString on which the tool operates.
    """
    def __init__(self):
        super(EditDimStringTool, self).__init__()
        self.__pds = True

    def setPrimary(self, flag=True):
        """Set the tool to operate on the primary DimString

setPrimary([flag])

Optional argument 'flag' should be a boolean. By default the
tool will operate on the primary DimString of a Dimension. If
argument 'flag' is False, the tool will operate on the secondary
DimString.
        """
        util.test_boolean(flag)
        self.__pds = flag

    def getPrimary(self):
        """Test if the tool operates on the primary DimString

getPrimary()

This method returns a boolean
        """
        return self.__pds

    def testAttribute(self, attr):
        """Test that the attribute is valid for the DimString entity.

testAttribute(attr)

Argument 'attr' must be one of the following: 'setPrefix', 'setSuffix',
'setUnits', 'setPrecision', 'setPrintZero', 'setPringDecimal', 'setFamily',
'setStyle', 'setWeight', 'setSize', 'setAlignment', 'setColor', or
'setAngle'.
        """
        if not isinstance(attr, str):
            raise TypeError, "Invalid attribute type: " + `type(attr)`
        _res = attr in ('setPrefix', 'setSuffix', 'setUnits', 'setPrecision',
                        'setPrintZero', 'setPrintDecimal')
        if _res:
            return _res
        return super(EditDimStringTool, self).testAttribute(attr)

    def testValue(self, val):
        """Test that the value is valid for a given DimString attribute.

testValue(val)

Argument 'val' depends on the attribute set for the EditDimString instance.
        """
        _a = self.getAttribute()
        if _a == 'setPrefix' or _a == 'setSuffix':
            if not isinstance(val, types.StringTypes):
                raise TypeError, "Invalid %s type: %s " % (_a, `type(val)`)
            _val = val
            if not isinstance(_val, unicode):
                _val = unicode(val)
        elif _a == 'setPrecision':
            if not isinstance(val, int):
                raise TypeError, "Invalid precision type: " + `type(val)`
            _val = val            
        elif _a == 'setPrintZero' or _a == 'setPrintDecimal':
            try:
                util.test_boolean(val)
            except TypeError:
                raise TypeError, "Invalid %s type: %s " % (_a, `type(val)`)
            _val = val
        elif _a == 'setUnits':
            _val = val # FIXME: needs error checking ...
        else:
            _val = super(EditDimStringTool, self).testValue(val)
        return _val
            
    def setText(self, txt):
        pass

    def getText(self):
        pass
    
    def hasText(self):
        pass
    
    def setTextLocation(self, x, y):
        pass

    def getTextLocation(self):
        pass

    def setBounds(self, width, height):
        pass

    def getBounds(self):
        pass

    def setPixelSize(self, width, height):
        pass

    def getPixelSize(self):
        pass

    def setLayout(self, layout):
        pass

    def getLayout(self):
        pass

