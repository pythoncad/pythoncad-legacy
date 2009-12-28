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
from PythonCAD.Generic.Tools.tangent_circle_tool import TangentCircleTool


class TwoPointTangentCCircleTool(TangentCircleTool):
    """
        A specialized tool for creating tangent construction circles.
        The TwoPointTangentCCircleTool will create a construction circle tangent
        to two construction lines or a construction line and a construction
        circle if such a tangent circle can be created.
        The TwoPointTangentCCircleTool is derived from the TangentCircleTool
        class, so it shares all the attributes and methods of that class.
    """
    def __init__(self):
        super(TwoPointTangentCCircleTool, self).__init__()
        self.__cobj1 = None
        self.__cobj2 = None

    def setFirstConObject(self, conobj):
        """Store the first reference construction object in the tool.

setFirstConObject(conobj)

Argument 'conobj' must be a VCLine, HCLine, ACLine, CLine, or CCircle object.
        """
        if not isinstance(conobj, (HCLine, VCLine, ACLine, CLine, CCircle)):
            raise TypeError, "Invalid Construction entity type: " + `type(conobj)`
        self.__cobj1 = conobj

    def getFirstConObject(self):
        """Retreive the first construction object from the tool.

getFirstConObject()
        """
        return self.__cobj1

    def setSecondConObject(self, conobj):
        """Store the second reference construction object in the tool.

setSecondConObject(conobj)

Argument 'conobj' must be a VCLine, HCLine, ACLine, or a CLine object.
Drawing a tangent circle against two CCircle objects is not yet supported.
A ValueError exception will be raised if this method is called before the
first construction object has been set.
        """
        if self.__cobj1 is None:
            raise ValueError, "First construction object not set."
        if not isinstance(conobj, (HCLine, VCLine, ACLine, CLine)):
            raise TypeError, "Invalid Construction line type: " + `type(conobj)`
        self.__cobj2 = conobj

    def getSecondConObject(self):
        """Retreive the second construction object from the tool.

getSecondConObject()
        """
        return self.__cobj2

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends the TangentCircleTool::reset() method.
        """
        super(TwoPointTangentCCircleTool, self).reset()
        self.__cobj1 = None
        self.__cobj2 = None

    def setLocation(self, x, y):
        """Store an x/y coordinate pair in the tool.

setLocation(x, y)

Arguments 'x' and 'y' should be floats. This method extends
the TangentCircleTool::setLocation() methods.
        """
        super(TwoPointTangentCCircleTool, self).setLocation(x, y)
        _tx, _ty = self.getLocation()
        _obja = self.__cobj1
        _objb = self.__cobj2
        _tandata = tangent.calc_tangent_circle(_obja, _objb, _tx, _ty)
        if _tandata is not None:
            _cx, _cy, _radius = _tandata
            self.setCenter(_cx, _cy)
            self.setRadius(_radius)


            