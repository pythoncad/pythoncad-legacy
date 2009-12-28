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

from PythonCAD.Generic import error
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.Tools.tool import Tool
from PythonCAD.Generic.Tools.utils import getSegmentSnap


class SegmentTool(Tool):
    """
        A Specialized tool for drawing Segment objects.
        The SegmentTool class is derived from the Tool class, so
        it shares the attributes and methods of that class. The
        SegmentTool class has the following additional methods:
    """
    def __init__(self):
        super(SegmentTool, self).__init__()
        self.__first_point = None
        self.__second_point = None
        self.__direction = None

    def setFirstPoint(self, snapPoint):
        """
            Store the first point of the Segment.
            Arguments 'x' and 'y' should be floats.
        """
        self.__first_point = snapPoint

    def getFirstPoint(self):
        """
            Get the first point of the Segment.
            This method returns a tuple holding the coordinates stored
            by invoking the setFirstPoint() method, or None if that method
            has not been invoked.
        """
        return self.__first_point

    def setSecondPoint(self, snapPoint):
        """
            Store the second point of the Segment.
            Arguments 'x' and 'y' should be floats. If the
            tool has not had the first point set with setFirstPoint(),
            a ValueError exception is raised.
        """
        if self.__first_point is None:
            raise ValueError, "SegmentTool first snapPoint is not set."
        self.__second_point = snapPoint

    def getSecondPoint(self):
        """
            Get the second point of the Segment.
            This method returns a tuple holding the coordinates stored
            by invoking the setSecondPoint() method, or None if that method
            has not been invoked.
        """
        return self.__second_point

    def reset(self):
        """
            Restore the tool to its initial state.
            This method extends Tool::reset().
        """
        super(SegmentTool, self).reset()
        self.__first_point = None
        self.__second_point = None

    def create(self, image):
        """
            Create a new Segment and add it to the image.
            This method overrides the Tool::create() method.    
        """
        if (self.__first_point is not None and
            self.__second_point is not None):
            _active_layer = image.getActiveLayer()
            _x1, _y1 ,_x2, _y2 = getSegmentSnap(self.__first_point ,self.__second_point)
            _pts = _active_layer.find('point', _x1, _y1)
            if len(_pts) == 0:
                _p1 = Point(_x1, _y1)
                _active_layer.addObject(_p1)
            else:
                _p1 = _pts[0]
            _pts = _active_layer.find('point', _x2, _y2)
            if len(_pts) == 0:
                _p2 = Point(_x2, _y2)
                _active_layer.addObject(_p2)
            else:
                _p2 = _pts[0]
            _s = image.getOption('LINE_STYLE')
            _seg = Segment(_p1, _p2, _s)
            _l = image.getOption('LINE_TYPE')
            if _l != _s.getLinetype():
                _seg.setLinetype(_l)
            _c = image.getOption('LINE_COLOR')
            if _c != _s.getColor():
                _seg.setColor(_c)
            _t = image.getOption('LINE_THICKNESS')
            if abs(_t - _s.getThickness()) > 1e-10:
                _seg.setThickness(_t)
            _active_layer.addObject(_seg)
            self.reset()
    def setDirection(self,angle):
        """
            set orizontal
        """
        if angle is None:
            self.__direction=None 
            return
        _ang=float(angle)
        self.__direction=_ang
    def getDirection(self):
        """
            get the direction
        """
        return self.__direction
    direction=property(getDirection,setDirection,None,"Direction of the line")
        
