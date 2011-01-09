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
#This module provide a class for the Trim command
#
from Kernel.exception               import *
from Kernel.Command.basecommand     import *
from Kernel.GeoEntity               import *
from Kernel.GeoEntity.segment       import Segment
from Kernel.GeoUtil.intersection    import *
from Kernel.GeoUtil.util            import *

class TrimCommand(BaseCommand):
    """
        this class represent the Trim command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcEntityPoint,
                        ExcEntityPoint,  
                        ExcText]
        self.defaultValue=[None, None,"BOTH"]
        self.message=[  "Give me the First Entity: ", 
                        "Give me the Second Entity: ",
                        "Give me The Trim Mode (First,Second,Both)[Both]: "]

    def performTrim(self):
        """
            get the chamfer segments
        """
        id0, p0=self.value[0]
        id1, p1=self.value[1]
        
        updEnts=[]
        geoEnt1=self.document.getEntity(id0)
        seg1=geoEnt1.toGeometricalEntity()
        geoEnt2=self.document.getEntity(id1)
        seg2=geoEnt2.toGeometricalEntity()
        intPoint=findSegmentExtendedIntersectionPoint(seg1, seg2)
        if len(intPoint)<=0:
            raise PythopnCadWarning("No intersection Found") 
        
        def getNearestPoint(pointArray, referencePoint):              
            distance=None
            exitPoint=None
            for p in pointArray:
                if distance==None:
                    distance=p.dist(referencePoint)
                    exitPoint=p
                    continue
                else:
                    newDistance=p.dist(exitPoint)
                    if newDistance<distance:
                        distance=newDistance
                        exitPoint=p
            return exitPoint 
            
        def getSegmentCelements(obj, pickPoint, intersectionPoint):
            if isinstance(obj, Segment):
                geoEntTrim=None
                geoEntTrim=updateSegment(obj, pickPoint, intersectionPoint)
                _cElements, entityType=self.document._getCelements(geoEntTrim)
                return _cElements
            else:
                return None
            
        if self.value[2].upper()=='FIRST' or self.value[2].upper()=='F' or self.value[2].upper()=='BOTH' or self.value[2].upper()=='B':
            nearestIntersectionPoint=getNearestPoint(intPoint, p0)
            if nearestIntersectionPoint!=None:
                _cElements=getSegmentCelements(seg1, p0,nearestIntersectionPoint)
                if _cElements!= None:
                    geoEnt1.setConstructionElements(_cElements)
                    updEnts.append(geoEnt1)
            
        if self.value[2].upper()=='SECOND' or self.value[2].upper()=='S' or self.value[2].upper()=='BOTH' or self.value[2].upper()=='B':
            nearestIntersectionPoint=getNearestPoint(intPoint, p1)
            if nearestIntersectionPoint!=None:
                _cElements=getSegmentCelements(seg2, p1,nearestIntersectionPoint)
                if _cElements!= None:
                    geoEnt2.setConstructionElements(_cElements)
                    updEnts.append(geoEnt2)
        return updEnts
        
    def applyCommand(self):
        """
            apply the trim command
        """
        if len(self.value)<2:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        if len(self.value)==2:
            self.value.append("BOTH")   # TODO: MAKE A GLOBAL VARIABLE TO SET THIS VALUE
                                        # AS A SETTING VALUE
        try:
            self.document.startMassiveCreation()
            for _ent in self.performTrim():
                self.document.saveEntity(_ent)
        finally:
            self.document.stopMassiveCreation()
       
