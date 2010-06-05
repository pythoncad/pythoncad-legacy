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
#This module provide a class for the polyline command
#

from Kernel.exception               import *
from Kernel.Command.basecommand     import *
from Kernel.GeoEntity.point            import Point

class MirrorCommand(BaseCommand):
    """
        this class rappresent the mirror command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcEntity, ExcEntity]
        self.message=["Give me the reference line (Segmento or CLine)"]
        self.raiseStop=False
    def next(self):
        """
            performe iteration
            overwrite the default next into an infinite loop
            we do not know how mani entity the user whant to mirror
        """
        if self.raiseStop:
            raise StopIteration
        return (self.exception[0],self.message[0])
    def __setitem__(self, key, value):
        """
            overwrite the command to perform the stop operation
        """
        if isinstance(value, Point):
            self.value.append(value)    
        else:
           self.raiseStop=True 
    def performMirror(self):
        """
            perform the mirror of all the entity selected
            First entity is the reference mirror line
        """
        mirrorRef=self.document.getEntity(self.value[0])
        geoMirrorRef=self.document.convertToGeometricalEntity(mirrorRef)
        outEnt=[]
        for i in renge(1, len(self.value)):
            dbEnt=self.document.getEntity(self.value[i])
            geoEnt=self.document.convertToGeometricalEntity(dbEnt)
            geoEnt.mirror(mirrorRef)
            dbEnt.setConstructionElements(geoEnt.getConstructionElements())
            outEnt.append(dbEnt)
        
    def applyCommand(self):
        """
            perform the write of the entity
        """
        if len(self.value)>1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        
        try:
            self.document.startMassiveCreation()
            for _ent in self.performMirror():
                self.document.saveEntity(_ent)
        finally:
            self.document.stopMassiveCreation()
