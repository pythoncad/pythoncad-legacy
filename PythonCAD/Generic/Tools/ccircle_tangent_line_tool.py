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


class CCircleTangentLineTool(Tool):
    """A specialized class for creating tangent lines to construction circles.

This class is a specialized class that handles creating construction
lines around circles. There can be at most four possible tangent lines.
There are two tangent lines if the circles overlap, and no tangent
lines if one circle is inside another. As this tool is derived from
the Tool class it shares all the attributes and methods of that
class. The CCircleTangentLineTool class has the following additional
methods:

{get/set}FirstCCircle(): Get/Set the first CCircle in the tool.
{get/set}SecondCCircle(): Get/Set the second CCircle in the tool.
    """
    def __init__(self):
        super(CCircleTangentLineTool, self).__init__()
        self.__circ1 = None
        self.__circ2 = None
        self.__tanpts = []

    def setFirstCCircle(self, ccircle):
        """Store the first construction circle in the tool.

setFirstCCircle(ccircle)

Argument 'ccircle' must be a CCircle object.
        """
        if not isinstance(ccircle, CCircle):
            raise TypeError, "Invalid CCircle type: " + `type(ccircle)`
        self.__circ1 = ccircle

    def getFirstCCircle(self):
        """Retreive the first construction circle from the tool.

getFirstCCircle()
        """
        return self.__circ1

    def setSecondCCircle(self, ccircle):
        """Store the second construction circle in the tool.

setSecondCCircle(ccircle)

Argument 'ccircle' must be a CCircle object. A ValueError exception will
be raised if this method is called before the first construction circle
has been set.
        """
        if self.__circ1 is None:
            raise ValueError, "First construction circle not set."
        if not isinstance(ccircle, CCircle):
            raise TypeError, "Invalid CCircle type: " + `type(ccircle)`
        self.__circ2 = ccircle
        #
        # calculate the tangent points if they exist
        #
        _cc1 = self.__circ1
        _cc2 = self.__circ2
        _cx1, _cy1 = _cc1.getCenter().getCoords()
        _r1 = _cc1.getRadius()
        _cx2, _cy2 = _cc2.getCenter().getCoords()
        _r2 = _cc2.getRadius()
        _sep = math.hypot((_cx2 - _cx1), (_cy2 - _cy1))
        _angle = math.atan2((_cy2 - _cy1), (_cx2 - _cx1))
        _sine = math.sin(_angle)
        _cosine = math.cos(_angle)
        #
        # tangent points are calculated as if the first circle
        # center is (0, 0) and both circle centers on the x-axis,
        # so the points need to be transformed to the correct coordinates
        #
        _tanpts = self.__tanpts
        del _tanpts[:] # make sure it is empty ...
        _tansets = tangent.calc_two_circle_tangents(_r1, _r2, _sep)
        for _set in _tansets:
            _x1, _y1, _x2, _y2 = _set
            _tx1 = ((_x1 * _cosine) - (_y1 * _sine)) + _cx1
            _ty1 = ((_x1 * _sine) + (_y1 * _cosine)) + _cy1
            _tx2 = ((_x2 * _cosine) - (_y2 * _sine)) + _cx1
            _ty2 = ((_x2 * _sine) + (_y2 * _cosine)) + _cy1
            _tanpts.append((_tx1, _ty1, _tx2, _ty2))


    def getSecondCCircle(self):
        """Retreive the second construction circle from the tool.

getSecondCCircle()
        """
        return self.__circ2

    def hasTangentPoints(self):
        """Test if tangent points were found for the two circles.

hasTangentPoints()
        """
        _val = False
        if len(self.__tanpts):
            _val = True
        return _val

    def getTangentPoints(self):
        """Return the tangent points calculated for two-circle tangency.

getTangentPoints()

This method returns a list of tuples holding four float values:

(x1, y1, x2, y2)

A tangent line can be drawn between the two circles from (x1, y1) to (x2, y2).
        """
        return self.__tanpts[:]

    def create(self, image):
        """Create the tangent line for two circles.

create(image)
        """
        _x, _y = self.getLocation()
        _tanpts = self.__tanpts
        if not len(_tanpts):
            raise ValueError, "No tangent points defined."
        _minsep = _px1 = _py1 = _px2 = _py2 = None
        for _set in _tanpts:
            _x1, _y1, _x2, _y2 = _set
            _sqlen = pow((_x2 - _x1), 2) + pow((_y2 - _y1), 2)
            _rn = ((_x - _x1) * (_x2 - _x1)) + ((_y - _y1) * (_y2 - _y1))
            _r = _rn/_sqlen
            _px = _x1 + _r * (_x2 - _x1)
            _py = _y1 + _r * (_y2 - _y1)
            _sep = math.hypot((_px - _x), (_py - _y))
            if _minsep is None or _sep < _minsep:
                _minsep = _sep
                _px1 = _x1
                _py1 = _y1
                _px2 = _x2
                _py2 = _y2
        _active_layer = image.getActiveLayer()
        _pts = _active_layer.find('point', _px1, _py1)            
        if len(_pts) == 0:
            _p1 = Point(_px1, _py1)
            _active_layer.addObject(_p1)
        else:
            _p1 = _pts[0]
        _pts = _active_layer.find('point', _px2, _py2)
        if len(_pts) == 0:
            _p2 = Point(_px2, _py2)
            _active_layer.addObject(_p2)
        else:
            _p2 = _pts[0]
        _active_layer.addObject(CLine(_p1, _p2))

    def reset(self):
        """Restore the tool to its initial state.

reset()

This method extends Tool::reset().
        """
        super(CCircleTangentLineTool, self).reset()
        self.__circ1 = None
        self.__circ2 = None
        del self.__tanpts[:]

