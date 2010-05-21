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
#This module provide a class for the Rectangle command
#
from Generic.Kernel.exception               import *
from Generic.Kernel.Command.basecommand     import *
from Generic.Kernel.Entity.point            import Point
from Generic.Kernel.Entity.segment          import Segment

class RectangleCommand(BaseCommand):
    """
        this class rappresent the segment command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcPoint, ExcPoint]
        self.message=["Give Me the first Point","Give Me The second Point"]
    def applyCommand(self):
        if len(self.value)!=2:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        p1=self.value[0]
        p2=self.value[1]
        x1, y1=p1.getCoords()
        x2, y2=p2.getCoords()
        p3=Point(x1, y2)
        p4=Point(x2, y1)
        s1=Segment(p1, p4)
        s2=Segment(p4, p2)
        s3=Segment(p2, p3)
        s4=Segment(p3, p1)
        self.document.saveEntity(s1)
        self.document.saveEntity(s2)
        self.document.saveEntity(s3)
        self.document.saveEntity(s4)
        
