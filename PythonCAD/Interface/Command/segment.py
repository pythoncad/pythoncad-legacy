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
# This Module provide a Interface Command 
#

from Kernel.initsetting             import SNAP_POINT_ARRAY
from Kernel.Command.segmentcommand  import SegmentCommand

class ICommand(object):
    """
        this class provide base command operation 
    """
    activeSnap=SNAP_POINT_ARRAY("ALL")
    drawPreview=True
    def __init__(self, scene):
        self.__scene=scene #this is needed for the preview creation
        self.__pointClick=[]
        self.__entClick=[]
        self.__distanceClick=[]
        self.__snapClick=[]
        self.__forceSnap=[]
        self.__index=-1
        
    def getPointClick(self, index):
        """
            return the index clicked entity
        """
        if len(self.__pointClick)>0 and len(self.__pointClick)<index:
            return self.__pointClick[index]
        raise IndexError
        
    def getEntityClick(self, index):
        """
            return the index clicked entity
        """
        if len(self.__entClick)>0 and len(self.__entClick)<index:
            return self.__entClick[index]
        raise IndexError

    def getDistanceClick(self, index):
        """
            return the index clicked entity
        """
        if len(self.__distanceClick)>0 and len(self.__distanceClick)<index:
            return self.__distanceClick[index]
        raise IndexError
        
    def getSnapClick(self, index):
        """
            return the index clicked entity
        """
        if len(self.__snapClick)>0 and len(self.__snapClick)<index:
            return self.__snapClick[index]
        raise IndexError 
        
    def getForceSnap(self, index):
        """
            return the index clicked entity
        """
        if len(self.__forceSnap)>0 and len(self.__forceSnap)<index:
            return self.__forceSnap[index]
        raise IndexError   
        
    def addMauseEvent(self, point, distance, entity, force):
        """
            add a clicked point
        """
        self.__index+=1
        self.updateMauseEvent( point, distance, entity, force)
        
    def updateMauseEvent(self, point, distance, entity, force):
        snap=getClickedPoint(point, entity, force)
        if len(self.__pointClick) <=self.index:
            self.__pointClick.append(point)
            self.__entClick.append(distance)
            self.__distance.append(entity)
            self.__snapClick.append(snap)
            self.__forceSnap.append(force)
        else:
            self.__pointClick[self.index]=(point)
            self.__entClick[self.index]=(distance)
            self.__distance[self.index]=(entity)
            self.__snapClick[self.index]=(snap)
            self.__forceSnap[self.index]=(force)
            
    @property
    def index(self):
        return self.__index
    @property
    def scene(self):
        """
            get the actual scene object
        """
        return self.__scene
    
    def getDummyBefore(self, func):
        """
            parametric function to return a previews element of an array
        """
        if self.index>0:
            return func(self.index+1)
        return None
        
    def getBeforeEntity(self):
        """
            get the before clicked entity
        """
        return self.getDummyBefore(self.getEntityClick)

    def getBeforeSnapClick(self):
        """
            get the before clicked snap point
        """
        return self.getDummyBefore(self.getSnapClick)
        
    def getLastForceSnap(self):    
        """
            get the before forced snap type
        """
        return self.getDummyBefore(self.getForceSnap)
        
    def getClickedPoint(self,  point, entity,force=None):
        """
            Get segment snapPoints
            Remarks:
            force:      [initsetting.SNAP_POINT_ARRAY]
            fromPoint:  [Geoent.Pointfloat]
            fromEnt:    [GeoEnt.*]
        """
        if force==None:
            force=SNAP_POINT_ARRAY["ALL"]
        snapPoint=None
        lastSnapType=self.getLastForceSnap()
        if SNAP_POINT_ARRAY["MID"] == force:
            snapPoint = self.getSnapMiddlePoint(entity)
            if lastSnapType: #Calculete in case of before constraint
                if lastSnapType==SNAP_POINT_ARRAY["ORTO"]:
                    snapPoint=self.getSnapOrtoPoint(snapPoint)
                elif lastSnapType==SNAP_POINT_ARRAY["TANGENT"]:
                    snapPoint=self.getSnapTangentPoint(snapPoint)
        elif SNAP_POINT_ARRAY["END"] == force:
            snapPoint =self.getSnapEndPoint(entity, point)
            if lastSnapType: #Calculete in case of before constraint
                if lastSnapType==SNAP_POINT_ARRAY["ORTO"]:
                    snapPoint=self.getSnapOrtoPoint(snapPoint)
                elif lastSnapType==SNAP_POINT_ARRAY["TANGENT"]:
                    snapPoint=self.getSnapTangentPoint(snapPoint)
        elif SNAP_POINT_ARRAY["ORTO"] == force:
            if lastSnapType:
                if lastSnapType==SNAP_POINT_ARRAY["TANGENT"]:    
                    snapPoint=self.getTangentOrtoSnap(entity)
                else:
                    snapPoint=self.getPointOrtoSnap(entity)
        elif SNAP_POINT_ARRAY["CENTER"]== force:
            snapPoint =self.getSnapCenterPoint(entity)
            if lastSnapType: #Calculete in case of before constraint
                if lastSnapType==SNAP_POINT_ARRAY["ORTO"]:
                    snapPoint=self.getSnapOrtoPoint(snapPoint)
                elif lastSnapType==SNAP_POINT_ARRAY["TANGENT"]:
                    snapPoint=self.getSnapTangentPoint(snapPoint) 
        elif SNAP_POINT_ARRAY["QUADRANT"]== force:
            snapPoint =self.getSnapQuadrantPoint(entity, point)
            if lastSnapType: #Calculete in case of before constraint
                if lastSnapType==SNAP_POINT_ARRAY["ORTO"]:
                    snapPoint=self.getSnapOrtoPoint(snapPoint)
                elif lastSnapType==SNAP_POINT_ARRAY["TANGENT"]:
                    snapPoint=self.getSnapTangentPoint(snapPoint) 
        elif SNAP_POINT_ARRAY["ORIG"]== force:
            snapPoint=Pointfloat(0.0, 0.0)
        elif SNAP_POINT_ARRAY["ALL"]== force:
            snapPoints=[]
            snapPoints.append(self.getSnapMiddlePoint(entity))
            snapPoints.append(self.getSnapEndPoint(entity, point))
            outPoint=(None, None)
            for p in snapPoints:
                if p:
                    distance=p.dist(fromPoint)
                    if outPoint[0]==None:
                        outPoint=(p, distance)
                    else:
                        if outPoint[1]>spoolDistance:
                            outPoint=(p, distance)
            else:
                snapPoint=outPoint[0]
                
        if snapPoint==None:
            return point
        return snapPoint
    ##
    ## here you can find all the function that compute the snap constraints
    ##
        
    def getSnapOrtoPoint(self, point):
        """
            this fucnticion compute the orto to point snap constraint
        """
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the orto point from the previews entity
        #   2) update the previews snap point
        return returnVal
        
    def getSnapTangentPoint(selfself, point):    
        """
            this fucnticion compute the Tangent to point snap constraint
        """
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the Tangent point from the previews entity
        #   2) update the previews snap point
        return returnVal
        
    def getSnapMiddlePoint(self, entity):    
        """
            this fucnticion compute midpoint snap constraint to the entity argument
        """
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the mid point from entity attributes if the entity have the mid
        #       point methods
        return returnVal
    
    def getSnapEndPoint(self, entity, point):
        """
            this fucnticion compute the  snap endpoint 
        """
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the end point from entity attributes if the entity 
        #       point methods
        return returnVal
        #snapPoint=self.getSnapTangentPointEnd(entity)
        #p1, p2=self.getEndpoints()
        #snapPoints.append(p1)
        #snapPoints.append(p2)
        
    def getTangentOrtoSnap(self, entity):
        """
            this fucnticion compute the snap from Tangent entity  to Orto entity
        """
        returnVal=None
        #this function have to be implemented as follow
        # no idea how to implements this think ..
        # may be somthing with simpy
        return returnVal
        
    def getPointOrtoSnap(self, entity):
        """
            this fucnticion compute the  snap from point to Ortogonal entity
        """
        returnVal=None
        #this function have to be implemented as follow
        # 1) ask to the entity the orto point from point
        return returnVal
    
    def getSnapCenterPoint(self, entity):
        """
            this fucnticion compute the  snap from the center of an entity
        """
        returnVal=None
        #this function have to be implemented as follow
        # 1) ask to the entity to get the center point
        return returnVal
     
    def getSnapQuadrantPoint(self, entity, point):
        """
            this fucnticion compute the  snap from the quadrant 
        """
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the quadrant point of an entity
        #   2) choose the nearest point 
        return returnVal
class ISegmentCommand(ICommand):
    """
        this class implements all the segment command interface
    """
    def __init__(self,scene):
        self.kernelCommand=SegmentCommand()
        super(ICommand, self).__init__(scene)
    
    def addMauseEvent(self, point, distance, entity, snap):
        """
            overwrite mouse click event
        """
        super(ICommand, self).addMauseEvent(self, point, distance, entity, snap)
        if(self.drawPreview):
            self.drawPreviewItem()
    
    def drawPreviewItem(self):
        """
            draw the segment preview item
        """
        pass

    def updateCommandValues(self):
        pass
    
   
    
