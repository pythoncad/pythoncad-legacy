#!/usr/bin/env python
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
# You should have received a copy of the GNU General Public Licensesegmentcmd.py
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#This module provide a class for the segment command
#
from Kernel.exception               import *
from Kernel.Command.basecommand     import *
from Kernel.GeoUtil.geolib          import Vector
from Kernel.GeoEntity.dimension     import Dimension

class DimensionCommand(BaseCommand):
    """
        This class represents the segment command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcPoint,ExcPoint,ExcPoint, ExcAngle]
        self.defaultValue=[None, None, None, 0]
        self.message=["Give Me The First Point: ",
                        "Give Me The Second Point: ",
                        "Give Me Dimesion Position: ",
                        "Give Me The Orientation Angle"]   # what does it mean???
    @property
    def getAngle(self):
        """
            Calculate the angle based on the starting and ending point
        """
        v=Vector(self.value[0], self.value[1])
        return v.absAng

    def applyCommand(self):
        if len(self.value)==3: #assing the angle
            self.value.append(self.getAngle)
        if len(self.value)!=4:
            raise PyCadWrongInputData("Wrong number of input parameter")
        dimArgs={"DIMENSION_1":self.value[0],
                    "DIMENSION_2":self.value[1],
                    "DIMENSION_3":self.value[2],
                    "DIMENSION_4":self.value[3]}
        dimension=Dimension(dimArgs)
        self.document.saveEntity(dimension)
