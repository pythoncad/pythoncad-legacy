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
# This Module provide a Interface Command managing the preview the and the snap
# system
#
from Kernel.initsetting             import SNAP_POINT_ARRAY
from Kernel.GeoEntity.point         import Point
from Interface.Preview.factory      import *

class ICommand(object):
    """
        this class provide base command operation 
    """
    activeSnap=SNAP_POINT_ARRAY["ALL"] #define the active snap system
    drawPreview=False   # enable the preview system
    automaticApply=True # apply the command at the last insert value
    def __init__(self, scene):
        self.__scene=scene                      # This is needed for the preview creation
        self.__kernelCommand = scene.activeCommand
        self.__previewItem=getPreviewObject(self.__kernelCommand)
        scene.addItem( self.__previewItem)      # Add preview item on creation
        self.__point=[]
        self.__entity=[]
        self.__distance=[]
        self.__snap=[]
        self.__forceSnap=[]
        self.__index=-1
        self.__forceDirection=self.__scene.forceDirection

    def addMauseEvent(self, point, distance, entity, force=None):
        """
            add value to a new slot of the command 
        """
        try:
            cmdIndex=self.__kernelCommand.next()
        except StopIteration:
            self.__kernelCommand.applyCommand()
            return
            
        exception,message=cmdIndex
        snap=self.getClickedPoint(point, entity, force)
        self.__kernelCommand[cmdIndex]=(snap,entity,distance)
        self.__point.append(point)
        self.__entity.append(entity)
        self.__distance.append(distance)
        self.__snap.append(snap)
        self.__forceSnap.append(force)
        self.updatePreview()   
        self.__index+=1
        if self.automaticApply:
            if(self.__index>=self.__kernelCommand.lenght-1): #Apply the command
                self.__kernelCommand.applyCommand()    
        
    def updateMauseEvent(self, point, distance, entity, force=None):
        """
            update value to the active slot of the command
        """
        snap=self.getClickedPoint(point, entity, force)
        print len(self.__snap)
        if self.index>-1:
            self.__point[self.index]=point
            self.__entity[self.index]=entity
            self.__distance[self.index]=distance
            self.__snap[self.index]=snap
            self.__forceSnap[self.index]=force
#            self.__point.append(point)
#            self.__entity.append(entity)
#            self.__distance.append(distance)
#            self.__snap.append(snap)
#            self.__forceSnap.append(force)

        #
        #   mange preview
        #
        self.updatePreview()
        
    def updatePreview(self):        
        if self.drawPreview:
            self.__previewItem.updatePreview(self.getActiveSnapClick()
                    , self.getActiveDistanceClick(), self.__kernelCommand)

    def getPointClick(self, index):
        """
            return the index clicked entity
        """
        return self.getDummyElement(self.__point, index)
        
    def getEntityClick(self, index):
        """
            return the index clicked entity
        """
        return self.getDummyElement(self.__entity, index)

    def getDistanceClick(self, index):
        """
            return the index clicked entity
        """
        return self.getDummyElement(self.__distanceClick, index)
        
    def getSnapClick(self, index):
        """
            return the index clicked entity
        """
        return self.getDummyElement(self.__snap, index)
        
    def getForceSnap(self, index):
        """
            return the index clicked entity
        """
        return self.getDummyElement(self.__forceSnap, index)
    
    def getDummyElement(self, array, index):
        if len(array)>0 and index<self.index:
            return array[index]
        raise IndexError   

            
    @property
    def index(self):
        return self.__index
    @property
    def scene(self):
        """
            get the actual scene object
        """
        return self.__scene
    
    def getDummyActive(self, func):
        """
            parametric function to return an element of an array
        """
        if self.index>0:
            return func(self.index)
        return None
    def getActiveSnapClick(self):
        """
            get the clicked snap point
        """
        return self.getDummyActive(self.getSnapClick)    
    
    def getActiveDistanceClick(self):
        """
            get the clicked distance
        """
        return self.getDummyActive(self.getDistanceClick)  
        
    def getDummyBefore(self, func):
        """
            parametric function to return a previews element of an array
        """
        if self.index>0:
            return func(self.index-1)
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
    
    def correctPositionForcedDirection(self, point):
        """
            correct the point cords 
        """
        x, y=point.getCoords()
        lastSnap=None
        if self.index>-1:
            lastSnap=self.getLastForceSnap()
        
        if self.__forceDirection and  lastSnap !=None:
            if self.__forceDirection=="H":
                y=lastSnap.y
            elif self.forceDirection=="V":
                x=lastSnap.x
            #elif self.forceDirection.find("F")>=0:
            #    angle=convertAngle(self.forceDirection.split("F")[1])
            #    if angle:
            #        x=self.lastSnap.x+x
            #        y=self.lastSnap.y+math.cos(angle)*x
        return Point(x, y)

    def getClickedPoint(self,  point, entity,force=None):
        """
            Get segment snapPoints
            Remarks:
            force:      [initsetting.SNAP_POINT_ARRAY element]
            fromPoint:  [Geoent.Pointfloat]
            fromEnt:    [GeoEnt.*]
        """
        point=self.correctPositionForcedDirection(point)
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
        #TODO: getSnapOrtoPoint
        #this function have to be implemented as follow
        #   1) get the orto point from the previews entity
        #   2) update the previews snap point
        return returnVal
        
    def getSnapTangentPoint(selfself, point):    
        """
            this fucnticion compute the Tangent to point snap constraint
        """
        #TODO: getSnapTangentPoint
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
        if getattr(entity, 'getMiddlePoint', None):
            returnVal=entity.getMiddlePoint()
        return returnVal
    
    def getSnapEndPoint(self, entity, point):
        """
            this fucnticion compute the  snap endpoint 
        """
        if getattr(entity, 'getEndpoints', None):
            p1, p2=entity.getEndpoints()
            if point.dist(p1)>point.dist(p2):
                return p1
            else:
                return p2
        else:
            return None
        
    def getTangentOrtoSnap(self, entity):
        """
            this fucnticion compute the snap from Tangent entity  to Orto entity
        """
        #TODO: getTangentOrtoSnap
        returnVal=None
        #this function have to be implemented as follow
        # no idea how to implements this think ..
        # may be somthing with simpy
        return returnVal
        
    def getPointOrtoSnap(self, entity):
        """
            this fucnticion compute the  snap from point to Ortogonal entity
        """
        #TODO: getPointOrtoSnap
        returnVal=None
        #this function have to be implemented as follow
        # 1) ask to the entity the orto point from point
        return returnVal
    
    def getSnapCenterPoint(self, entity):
        """
            this fucnticion compute the  snap from the center of an entity
        """
        #TODO: getSnapCenterPoint
        returnVal=None
        #this function have to be implemented as follow
        # 1) ask to the entity to get the center point
        return returnVal
     
    def getSnapQuadrantPoint(self, entity, point):
        """
            this fucnticion compute the  snap from the quadrant 
        """
        #TODO: getSnapQuadrantPoint
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the quadrant point of an entity
        #   2) choose the nearest point 
        return returnVal
