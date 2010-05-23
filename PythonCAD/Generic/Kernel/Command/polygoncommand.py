#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
#
# Copyright (c) 2010 Matteo Boscolo
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
# Polygon command
#

import math
import array
from Generic.Kernel.exception               import *
from Generic.Kernel.Command.basecommand     import *
from Generic.Kernel.Entity.point            import Point
from Generic.Kernel.Entity.segment          import Segment

class PolygonCommand(BaseCommand):
    """
        A specialized to for creating Polygons from Segments.
        The PolygonTool will create an uniformly sized polygon from Segment
        entities. The minimum number of sides is three, creating an equilateral
        triangle. There is no maximum number of sides, though realistically any
        polygon with more than 20 or so sides is unlikely to be drawn.
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcPoint, 
                        ExcPoint, 
                        ExcInt, 
                        ExcBool]
        self.message=["Give Me the first Point",
                        "Give Me The Second Point", 
                        "Give Me The Number of Segment", 
                        "Give Me External or Internal"]
        self.__xpts = array.array("d")
        self.__ypts = array.array("d")
        
        
    def setSideCount(self, count):
        """
            Set the number of sides of the polygon to create.
            Argument "count" should be an integer value greater than 2.
        """
        _count = count
        if not isinstance(_count, int):
            _count = int(count)
        if _count < 3:
            raise ValueError, "Invalid count: %d" % _count
        self.__nsides = _count
        self.__increment = (math.pi*2)/float(_count)
        for _i in range(_count):
            self.__xpts.insert(_i, 0.0)
            self.__ypts.insert(_i, 0.0)

    def getSideCount(self):
        """
            Get the number of sides of the polygon to be created.
            A ValueError exception is raised if the side count has not been
            set with setSideCount()
        """
        if self.__nsides is None:
            raise ValueError, "No side count defined."
        return self.__nsides

    def setExternal(self, value):
        """
            Create the polygon on the outside of a reference circle.
            By default the polygon is drawing completely contained within a
            circle. Invoking this method will created the polygon so that all
            sides are outside the circle.
        """
        if value:
            self.__external = True
        else:
            self.__external = False

    def getExternal(self):
        """
            Test if the polygon will be created outside a circle.
            If the setExternal() method has been called, this method will
            return True. By default this method will return False.
        """
        return self.__external

    def setCenter(self, p):
        """
            Define the center of the polygon.
            Arguments 'x' and 'y' should be float values.
        """
        if isinstance(p, Point):
            self.__center = p
        else:
            raise TypeError, "p must be a of type Point"

    def getCenter(self):
        """
            Retrieve the center of the polygon to be created.
        """
        if self.__center is None:
            raise ValueError, "Center is undefined."
        return self.__center

    def getCoord(self, i):
        """
            Get one of the coordinates of the polygon corners.
            Argument "i" should be an integer value such that:
            0 <= i <= number of polygon sides
        """
        _x = self.__xpts[i]
        _y = self.__ypts[i]
        return _x, _y

    def CalculatePoint(self):
        """
            This method calculates the polygon
            points.
        """
        _x, _y = self.__externalPoint.getCoords()
        _count = self.__nsides
        _inc = self.__increment
        if self.__external:
            _offset = _inc/2.0
        else:
            _offset = 0.0
        _cx, _cy = self.__center.getCoords()
        _xsep = _x - _cx
        _ysep = _y - _cy
        _angle = math.atan2(_ysep, _xsep) + _offset
        _rad = math.hypot(_xsep, _ysep)/math.cos(_offset)
        _xp = self.__xpts
        _yp = self.__ypts
        for _i in range(_count):
            _xp[_i] = _cx + (_rad * math.cos(_angle))
            _yp[_i] = _cy + (_rad * math.sin(_angle))
            _angle = _angle + _inc

    def getEntsToSave(self):
        """
            return a list of segment
        """
        objEnt=[]
        self.CalculatePoint()
        if len(self.__xpts):
            _count = self.__nsides
            _xp = self.__xpts
            _yp = self.__ypts
            _x = _xp[0]
            _y = _yp[0]
            #
            # find starting point ...
            #
            _p0 = Point(_x, _y)
            #
            # make segments for all the points ...
            #
            _p1 = _p0
            for _i in range(1, _count):
                _x = _xp[_i]
                _y = _yp[_i]
                _pi = Point(_x, _y)
                segArg={"SEGMENT_0":_p1, "SEGMENT_1":_pi}
                objEnt.append(Segment(segArg))
                _p1 = _pi
            #
            # now add closing segment ...
            #
            segArg={"SEGMENT_0":_p1, "SEGMENT_1":_p0}
            objEnt.append(Segment(segArg))
        return  objEnt   
    def applyCommand(self):
        """
            Create a Polygon from Segments and add it to the kernel.
        """
                
        self.setSideCount(self.value[2])
        self.__externalPoint=self.value[1]
        self.__external = self.value[3]
        self.setCenter(self.value[0])
        try:
            self.document.startMassiveCreation()
            for _ent in self.getEntsToSave():
                self.document.saveEntity(_ent)
        finally:
            self.document.stopMassiveCreation()
 
