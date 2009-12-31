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


class ParallelOffsetTool(Tool):
    """
        A specialized tool for creating parallel construction lines.
        The ParallelOffsetTool will create a construction line parallel
        to another construction line a fixed distance from the original
        construction line. The type of the new construction line will match
        that of the original.
        The ParallelOffsetTool is derived from the Tool class, so it shares
        all the attributes and methods of that class. 
    """
    def __init__(self):
        super(ParallelOffsetTool, self).__init__()
        self.__refpt = None
        self.__offset = None
        self.__conline = None
    def setOffset(self, offset):
        """
            Store the displacement in the tool.
            Argument 'offset' must be a float.
        """
        _offset = util.get_float(offset)
        self.__offset = _offset
    def getOffset(self):
        """Return the stored offset from the tool.
        This method will raise a ValueError exception if the offset has
        not been set with setOffset()
        """
        _offset = self.__offset
        if _offset is None:
            raise ValueError, "Offset is not defined."
        return _offset
    def setConstructionLine(self, conline):
        """
            Store the reference construction line in the tool.
            Argument 'conline' must be a VCLine, HCLine, ACLine, or CLine object.
        """
        if not isinstance(conline, (HCLine, VCLine, ACLine, CLine)):
            raise TypeError, "Invalid Construction line: " + `type(conline)`
        self.__conline = conline
    def getConstructionLine(self):
        """
            Retrieve the stored construction line from the tool.
            A ValueError exception is raised if the construction line has not been
            set with the setConstructionLine() method.
        """
        _conline = self.__conline
        if _conline is None:
            raise ValueError, "Construction line is not defined."
        return _conline
    def setReferencePoint(self, x,y):
        """
            Store the reference point for positioning the new construction line.
            Arguments 'x' and 'y' give the coordinates of a reference point
            used to determine where the new construction line will be placed.
            Both arguments should be floats.
        """
        self.__refpt = (x,y)
    def getReferencePoint(self):
        """
            Retreive the reference point from the tool.
            This method returns a tuple containing the values stored from
            the setReferencePoint() call. This method will raise a ValueError
            exception if the reference point has not been set.
        """
        _refpt = self.__refpt
        if _refpt is None:
            raise ValueError, "No reference point defined."
        return _refpt
    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends Tool::reset().
        """
        super(ParallelOffsetTool, self).reset()
        self.__refpt = None
        self.__offset = None
        self.__conline = None

    def create(self, image):
        """
            Create a parallel construction line in an image.
            This method overrides the Tool::create() method.
        """
        _offset = self.__offset
        _conline = self.__conline
        _refpt = self.__refpt
        if (_offset is not None and
            _conline is not None and
            _refpt is not None):
            _active_layer = image.getActiveLayer()
            _rx, _ry = _refpt
            _lp1 = _lp2 = _ncl = None
            if isinstance(_conline, HCLine):
                _x, _y = _conline.getLocation().getCoords()
                if _ry > _y:
                    _yn = _y + _offset
                else:
                    _yn = _y - _offset
                if len(_active_layer.find('hcline', _yn)) == 0:
                    _pts = _active_layer.find('point', _x, _yn)
                    if len(_pts) == 0:
                        _lp1 = Point(_x, _yn)
                    else:
                        _lp1 = _pts[0]
                    _ncl = HCLine(_lp1)
            elif isinstance(_conline, VCLine):
                _x, _y = _conline.getLocation().getCoords()
                if _rx > _x:
                    _xn = _x + _offset
                else:
                    _xn = _x - _offset
                if len(_active_layer.find('vcline', _xn)) == 0:
                    _pts = _active_layer.find('point', _xn, _y)
                    if len(_pts) == 0:
                        _lp1 = Point(_xn, _y)
                    else:
                        _lp1 = _pts[0]
                    _ncl = VCLine(_lp1)
            elif isinstance(_conline, ACLine):
                _x, _y = _conline.getLocation().getCoords()
                _angle = _conline.getAngle()
                if abs(_angle) < 1e-10: # horizontal
                    _dx = 0.0
                    _dy = _offset
                elif abs(abs(_angle) - 90.0) < 1e-10: # vertical
                    _dx = _offset
                    _dy = 0.0
                else:
                    _slope = math.tan(_angle * (math.pi/180.0))
                    _yint = _y - (_slope * _x)
                    #
                    # p1 => (_x, _y)
                    # p2 => (0, _yint)
                    #
                    # redefine angle from p1 to p2 ...
                    _angle = math.atan2((_yint - _y), -_x)
                    if _angle < 0.0:
                        _angle = _angle + (2.0 * math.pi)
                    _sqlen = math.hypot(_x, (_y - _yint))
                    _sn = ((_y - _ry) * (0.0 - _x)) - ((_x - _rx) * (_yint - _y))
                    _s = _sn/_sqlen
                    if _s < 0.0:
                        _perp = _angle + (math.pi/2.0)
                    else:
                        _perp = _angle - (math.pi/2.0)
                    _dx = _offset * math.cos(_perp)
                    _dy = _offset * math.sin(_perp)
                    _angle = _conline.getAngle() # reset variable
                _xn = _x + _dx
                _yn = _y + _dy
                if len(_active_layer.find('acline', _xn, _yn, _angle)) == 0:
                    _pts = _active_layer.find('point', _xn, _yn)
                    if len(_pts) == 0:
                        _lp1 = Point(_xn, _yn)
                    else:
                        _lp1 = _pts[0]
                    _ncl = ACLine(_lp1, _angle)
            elif isinstance(_conline, CLine):
                _p1, _p2 = _conline.getKeypoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                if abs(_x2 - _x1) < 1e-10: # vertical
                    _dx = _offset
                    _dy = 0.0
                elif abs(_y2 - _y1) < 1e-10: # horizontal
                    _dx = 0.0
                    _dy = _offset
                else:
                    _angle = math.atan2((_y2 - _y1), (_x2 - _x1))
                    if _angle < 0.0:
                        _angle = _angle + (2.0 * math.pi)
                    _sqlen = math.hypot((_x2 - _x1), (_y2 - _y1))
                    _sn = ((_y1 - _ry) * (_x2 - _x1)) - ((_x1 - _rx) * (_y2 - _y1))
                    _s = _sn/_sqlen
                    if _s < 0.0:
                        _perp = _angle + (math.pi/2.0)
                    else:
                        _perp = _angle - (math.pi/2.0)
                    _dx = math.cos(_perp) * _offset
                    _dy = math.sin(_perp) * _offset
                _x1n = _x1 + _dx
                _y1n = _y1 + _dy
                _x2n = _x2 + _dx
                _y2n = _y2 + _dy
                if len(_active_layer.find('cline', _x1n, _y1n, _x2n, _y2n)) == 0:
                    _pts = _active_layer.find('point', _x1n, _y1n)
                    if len(_pts) == 0:
                        _lp1 = Point(_x1n, _y1n)
                    else:
                        _lp1 = _pts[0]
                    _pts = _active_layer.find('point', _x2n, _y2n)
                    if len(_pts) == 0:
                        _lp2 = Point(_x2n, _y2n)
                    else:
                        _lp2 = _pts[0]
                    _ncl = CLine(_lp1, _lp2)
            else:
                raise TypeError, "Invalid Construction line type: " + `type(_conline)`
            if _ncl is not None:
                if _lp1 is not None and _lp1.getParent() is None:
                    _active_layer.addObject(_lp1)
                if _lp2 is not None and _lp2.getParent() is None:
                    _active_layer.addObject(_lp2)
                _active_layer.addObject(_ncl)
            self.reset()

