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
# You should have received a copy of the GNU General Public License
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#This module provide basic command function
#

from Generic.Kernel.exception           import *
from Generic.Kernel.Entity.segment      import Segment
from Generic.Kernel.Entity.arc          import Arc

class BaseCommand(object):
    """
        this class provide a base command 
    """
    def __init__(self, kernel):
        """
            kernel is a PyCadKernel object
        """
        self.exception=[]
        self.value=[]
        self.message=[]
        self.index=-1
        self.kernel=kernel
    def __iter__(self):
        return self
    def next(self):
        """
            performe iteration
        """
        self.index+=1
        TotNIter=len(self.exception)
        if self.index>=TotNIter:
            raise StopIteration
        return (self.exception[self.index],self.message[self.index])
        
    def __setitem__(self, key, value):
        """
            set the value of the command
        """
        self.value.append(value)
    def applyCommand(self):
        """
            this method here must be defined
        """
        pass
        
class SegmentCommand(BaseCommand):
    """
        this class rappresent the segment command
    """
    def __init__(self, kernel):
        BaseCommand.__init__(self, kernel)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcPoint, ExcPoint]
        self.message=["Give Me the first Point","Give Me The Second Point"]
    def applyCommand(self):
        if len(self.value)!=2:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        seg=Segment(self.value[0], self.value[1])
        self.kernel.saveEntity(seg)
        
class ArcCommand(BaseCommand):
    """
        this class rappresent the segment command
    """
    def __init__(self, kernel):
        BaseCommand.__init__(self, kernel)
        self.exception=[ExcPoint, ExcLenght, ExcAngle, ExcAngle]
        self.message=["Give Me the center Point", "Give Me the radius", "Give Me the first Angle (Could Be None)", "Give Me the second Angle (Could Be None)"]
    def applyCommand(self):
        if len(self.value)<2:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        arc=Arc(self.value[0], self.value[1], self.value[2], self.value[3])
        self.kernel.saveEntity(arc)
        
        
#Command list
APPLICATION_COMMAND={'SEGMENT':SegmentCommand,'ARC':ArcCommand}
