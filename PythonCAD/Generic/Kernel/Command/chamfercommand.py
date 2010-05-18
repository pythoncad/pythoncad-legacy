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
#This module provide a class for the champfer command
#
from Generic.Kernel.exception               import *
from Generic.Kernel.Command.basecommand     import *
from Generic.Kernel.Entity.segjoint         import Chamfer
from Generic.Kernel.Entity.segment          import Segment
from Generic.Kernel.composedentity          import ComposedEntity

class ChamferCommand(BaseCommand):
    """
        this class rappresent the champfer command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcEntity,
                        ExcEntity, 
                        ExcLenght, 
                        ExcLenght, 
                        ExcPoint, 
                        ExcPoint ]
        self.message=[  "Give Me the first  Entity ID", 
                        "Give Me the second Entity ID", 
                        "Give Me the first Lenght", 
                        "Give Me the seconf Lenght", 
                        "Give me the first point near the first entity",
                        "Give me the second point near the second entity"]
    def applyCommand(self):
        """
            apply the champfer command
        """
        if len(self.value)!=6:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        
        #objId,constructionElements, eType, style, childEnt=[]

        ent1=self.document.getEntity(self.value[0].getId())
        ent2=self.document.getEntity(self.value[1].getId())
        
        cel1=ent1.getConstructionElements()
        p1=cel1["SEGMENT_0"]
        p2=cel1["SEGMENT_1"]
        seg1=Segment(p1, p2)
        
        cel2=ent2.getConstructionElements()
        p1=cel2["SEGMENT_0"]
        p2=cel2["SEGMENT_1"]
        seg2=Segment(p1, p2)

        cmf=Chamfer(seg1,
                    seg2,  
                    self.value[2], 
                    self.value[3], 
                    self.value[4], 
                    self.value[5])
        seg1Mod, seg2Mod, chamferSegment = cmf.getReletedComponent()
        
        _cElements1, entityType=self.document._getCelements(seg1Mod)
        _cElements2, entityType=self.document._getCelements(seg2Mod)
       
        ent1.setConstructionElements(_cElements1)
        ent2.setConstructionElements(_cElements2)
        
        self.document.saveEntity(ent1)
        self.document.saveEntity(ent2)
        ent3=self.document.saveEntity(chamferSegment)
        
       
