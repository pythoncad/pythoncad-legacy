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
from PythonCAD.Generic.Tools.utils import getSegmentSnap


class PolylineTool(Tool):
    """
        A specialized tool for drawing Polyline objects.
        The PolylineTool class is derived from the Tool class, so it
        shares all the attributes and methods of that class. 
    """
    def __init__(self):
        super(PolylineTool, self).__init__()
        self.__points = []

    def __len__(self):
        return len(self.__points)

    def storePoint(self,p):
        """
            Store a point that will define a Polyline.
            The arguments 'x' and 'y' should be float values. There is
            no limit as to how long a Polyline should be, so each invocation
            of this method appends the values to the list of stored points.
        """
        self.__points.append(p)

    def getPoint(self, i):
        """
            Retrieve a point used to define a Polyline.
            Argument 'i' represents the index in the list of points that
            defines the polyline. Negative indicies will get points from
            last-to-first. Using an invalid index will raise an error.
            This method returns a tuple holding the x/y coordinates.
        """
        return self.__points[i]

    def getPoints(self):
        """
            Get all the points that define the Polyline.
            This method returns a list of tuples holding the x/y coordinates
            of all the points that define the Polyline.
        """
        return self.__points[:]

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends Tool::reset().
        """
        super(PolylineTool, self).reset()
        del self.__points[:]

    def create(self, image):
        """
            Create a new Polyline and add it to the image.
            This method overrides the Tool::create() method.
        """
        if len(self.__points):
            _pts = []
            _active_layer = image.getActiveLayer()
            _sp=None
            for _pt in self.__points:
                if _sp is None:
                    _sp=_pt
                    _x,_y=_pt.point.getCoords()
                    _lpts = _active_layer.find('point', _x, _y)
                    if len(_lpts) == 0:
                        _p = Point(_x, _y)
                        _active_layer.addObject(_p)
                        _pts.append(_p)
                    else:
                        _pts.append(_lpts[0])
                else:
                    _x1, _y1 ,_x2, _y2 = getSegmentSnap(_sp,_pt)
                    _lpts = _active_layer.find('point', _x2, _y2)
                    if len(_lpts) == 0:
                        _p = Point(_x2, _y2)
                        _active_layer.addObject(_p)
                    else:
                        _p=_lpts[0]
                    _pts.append(_p)                    
                    _pt.point=_p                    
                    _sp=_pt
            _s = image.getOption('LINE_STYLE')
            _pline = Polyline(_pts, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _pline.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _pline.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _pline.setThickness(_t)
            _active_layer.addObject(_pline)
            self.reset()


            