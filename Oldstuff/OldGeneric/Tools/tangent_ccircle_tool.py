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


class TangentCCircleTool(TangentCircleTool):
    """A specialized tool for creating tangent construction circles.

The TangentCCircleTool will create a construction circle tangent
to a construction line or a construction circle.

The TangentCCircleTool is derived from the TangentCircleTool class, so
it shares all the attributes and methods of that class. The TangentCCircleTool
has the following addtional methods:

{set/get}ConstructionObject(): Set/Get the reference construction object.
    """
    def __init__(self):
        super(TangentCCircleTool, self).__init__()
        self.__conobj = None

    def setConstructionLine(self, conobj):
        """Store the reference construction object in the tool.

setConstructionLine(conobj)

Argument 'conobj' must be a VCLine, HCLine, ACLine, CLine,
or CCircle object.
        """
        if not isinstance(conobj, (HCLine, VCLine, ACLine, CLine, CCircle)):
            raise TypeError, "Invalid Construction entity type: " + `type(conobj)`
        self.__conobj = conobj

    def getConstructionLine(self):
        """Retrieve the stored construction line from the tool.

getConstructionLine()

A ValueError exception is raised if the construction line has not been
set with the setConstructionLine() method.
        """
        _conobj = self.__conobj
        if _conobj is None:
            raise ValueError, "Construction object is not defined."
        return _conobj

    #-----------------------------------------------------------------------------------------------
    def setLocation(self, point):
        """Store an x/y coordinate pair in the tool.

setLocation(x, y)

Arguments 'x' and 'y' should be floats. This method extends
the TangentCircleTool::setLocation() methods.
        """
        super(TangentCCircleTool, self).setLocation(point)
        _tx, _ty = self.getLocation().getCoords()
        _conobj = self.__conobj
        _cx = _cy = _radius = None
        if isinstance(_conobj, HCLine):
            _x, _y = _conobj.getLocation().getCoords()
            _cx = _tx
            _cy = (_ty + _y) / 2.0
            _radius = abs(_ty - _y) / 2.0
        elif isinstance(_conobj, VCLine):
            _x, _y = _conobj.getLocation().getCoords()
            _cx = (_tx + _x) / 2.0
            _cy = _ty
            _radius = abs(_tx - _x) / 2.0
        elif isinstance(_conobj, (ACLine, CLine)):
            _px, _py = _conobj.getProjection(_tx, _ty)
            _cx = (_tx + _px) / 2.0
            _cy = (_ty + _py) / 2.0
            _radius = math.hypot((_tx - _px), (_ty - _py)) / 2.0
        elif isinstance(_conobj, CCircle):
            _ccx, _ccy = _conobj.getCenter().getCoords()
            _rad = _conobj.getRadius()
            _sep = math.hypot((_tx - _ccx), (_ty - _ccy))
            if _sep < 1e-10:
                return
            _angle = math.atan2((_ty - _ccy), (_tx - _ccx))
            _px = _ccx + (_rad * math.cos(_angle))
            _py = _ccy + (_rad * math.sin(_angle))
            _cx = (_tx + _px) / 2.0
            _cy = (_ty + _py) / 2.0
            _radius = math.hypot((_tx - _px), (_ty - _py)) / 2.0
        else:
            raise TypeError, "Invalid construction entity type: " + `type(_conobj)`
        self.setCenter(Point(_cx, _cy))
        self.setRadius(_radius)


        