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
# How it works:
#
#
#
#Qt Import
#
from PyQt4 import QtCore, QtGui

import math, string
#
#Kernel Import
#
from Kernel.initsetting             import SNAP_POINT_ARRAY, ACTIVE_SNAP_POINT, ACTIVE_SNAP_LIST
from Kernel.GeoEntity.point         import Point
from Kernel.GeoUtil.geolib          import Vector
from Kernel.GeoUtil.intersection    import *
from Kernel.pycadevent              import *
from Kernel.exception               import *
from Kernel.unitparser              import *
#
# Interface Import
#
from Interface.cadinitsetting       import RESTART_COMMAND_OPTION
from Interface.Entity.base          import BaseEntity
from Interface.Dialogs.property     import Property
from Interface.Preview.factory      import *
from Interface.DrawingHelper.snap   import *

class ICommand(object):
    """
        this class provide base command operation
    """
    #self.scene.snappingPoint.activeSnap=SNAP_POINT_ARRAY["LIST"]  # Define the active snap system
    drawPreview=True                    # Enable the preview system
    automaticApply=True                 # Apply the command at the last insert value
    #restartCommandOption=False         # moved to Interface.cadinitsetting  > RESTART_COMMAND_OPTION

    def __init__(self, scene):
        self.__scene=scene              # This is needed for the preview creation
        self.__previewItem=None
        self.__point=[]
        self.__entity=[]
        self.__distance=[]
        self.__angle=[]
        self.__snap=[]
        self.__forceSnap=[]
        self.__index=-1
        self.updateInput=PyCadEvent()
        #self.scene.snappingPoint.activeSnap=#SNAP_POINT_ARRAY["LIST"]  # Define the active snap system
    @property
    def forceDirection(self):
        """
            get scene force direction
        """
        return self.__scene.forceDirection
    @property
    def kernelCommand(self):
        """
            get scene the kernel command
        """
        return self.scene.activeKernelCommand
    @property
    def scene(self):
        """
            get scene
        """
        return self.__scene
    @property
    def index(self):
        return self.__index

    def restartCommand(self):
        """
            reuse the command
        """
        if self.kernelCommand!=None:
            self.kernelCommand.reset()
        self.__point=[]
        self.__entity=[]
        self.__distance=[]
        self.__angle=[]
        self.__snap=[]
        self.__forceSnap=[]
        self.__index=-1
        self.removePreviewItemToTheScene()

    def addMauseEvent(self, point, entity,distance=None,angle=None , text=None, force=None, correct=True):
        """
            add value to a new slot of the command
        """
        #
        # Compute snap distance and position force
        #
        #print "log: addMauseEvent", str(point), str(entity), str(distance), str(angle), str(text), str(force)
        if correct!=None:
            snap=self.scene.snappingPoint.getSnapPoint(point,self.getEntity(point))
            snap=self.correctPositionForcedDirection(snap, self.__scene.forceDirection)
        else:
            snap=point
        if angle==None:
            angle=self.calculateAngle(snap)
        if distance==None:
            distance=self.getDistance(snap)
        #
        # Assing value to the object arrays
        #
        try:
            self.kernelCommand[self.__index]=(snap,entity,distance, angle, text)
            self.scene.fromPoint=snap
            if self.kernelCommand.activeException()==ExcPoint or self.kernelCommand.activeException()==ExcLenght:
                if snap!=None:
                    self.scene.GuideHandler.place(snap.getx(), snap.gety())
                if self.scene.forceDirectionEnabled==True:
                    self.scene.GuideHandler.show()
        except:
            self.updateInput("msg")
            self.updateInput(self.kernelCommand.activeMessage)
            self.scene.clearSelection()
            return
        self.__point.append(point)
        self.__entity.append(entity)
        self.__distance.append(distance)
        self.__angle.append(angle)
        self.__snap.append(snap)
        self.__forceSnap.append(force)
        #self.updatePreview(point,distance,entity )
        self.__index+=1
        try:
            self.kernelCommand.next()
        except StopIteration:
            self.applyCommand()
            return

        self.updateInput(self.kernelCommand.activeMessage)
        if self.automaticApply and self.kernelCommand.automaticApply:
            if(self.__index>=self.kernelCommand.lenght-1): #Apply the command
                self.applyCommand()

        if self.kernelCommand.activeException()==ExcDicTuple:
            dialog=Property(parent =self.scene.parent(),  entity=entity)
            if dialog.changed:
                self.kernelCommand[self.__index]=(None,entity,None, None, dialog.value)
                self.applyCommand()
            else:
                self.restartCommand()

    def applyDefault(self):
        """
            apply the default value command
        """
        try:
            self.kernelCommand.performDefaultValue()
            self.kernelCommand.next()
            self.updateInput(self.kernelCommand.activeMessage)
        except NoDefaultValue:
            return
        except StopIteration:
                self.applyCommand()
                return

    def applyCommand(self):
        """
            apply the command
        """
        self.scene.hideSnapMarks()
        try:
            self.kernelCommand.applyCommand()
            if RESTART_COMMAND_OPTION:
                self.restartCommand()
                self.updateInput(self.kernelCommand.activeMessage)
                self.scene.clearSelection()
                self.scene.fromPoint=None
                self.scene.isGuided=None
                self.scene.isGuideLocked=None
                self.scene.GuideHandler.reset()
            else:
                self.scene.cancelCommand()
                self.updateInput("Ready")
                self=None
        except Exception as e:
            print type(e)     # the exception instance
            print "ICommand applyCommand Errore ", str(e)
            self.restartCommand()
        self.removePreviewItemToTheScene()
        return

    def getEntity(self, position):
        """
            get the entity nearest at the mouse position
        """
        if position ==None:
            return None
        p=QtCore.QPointF(position.x, position.y*-1.0)
        ents=self.__scene.items(p)
        if len(ents)>1: # bug: it was 0
            #TODO: here it will be nice to have a sort of control for chosing one entity
            #in case of overlapping entity selection
            print "more than one entity under the mouse"
        for e in ents:
            if isinstance(e, BaseEntity):
                return e
        return None

    def updateMauseEvent(self, point, distance, entity, force=None):
        """
            update value to the active slot of the command
        """
        if self.index>-1:
            self.__point[self.index]=point
            self.__entity[self.index]=entity
            self.__distance[self.index]=distance
            self.__snap[self.index]=point
            self.__forceSnap[self.index]=force
        self.updatePreview(point, distance, entity) #   mange preview

    def addTextEvent(self, value):
        """
            compute imput from text
        """
        if value=="":
            self.kernelCommand.applyDefault()
            self.applyCommand()
            return
        elif value.upper()=="UNDO":
            #TODO: perform a back operatio to the command
            return
        elif value.upper()=="REDO":
            #TODO: perform a forward operatio to the command
            return
        else:
            try:
                tValue=self.decodeText(value)
                self.addMauseEvent(tValue[0], tValue[1], tValue[2], tValue[3], tValue[4], correct=None)
            except PyCadWrongImputData, msg:
                print "Problem on ICommand.addTextEvent"
                self.updateInput(msg)
                self.updateInput(self.kernelCommand.activeMessage)
                return

    def getDistance(self, point):
        """
            Get The distance from 2 points
        """
        prPoint=self.getActiveSnapClick()
        if prPoint!=None and point!=None:
            d=prPoint.dist(point)
            return d
        else:
            return None

    def calculateAngle(self, snap):
        """
            calculate the angle betwin the point clicked
        """
        if snap==None:
            return None

        for snapPoint in self.__snap:
            if snapPoint!=None:
                v=Vector(snapPoint,snap )
                return v.absAng
        else:
            return None

    def decodeText(self, value):
        """
            encode the text given from the user
        """
        point=None
        distance=None
        entitys=None
        text=None
        angle=None
        try:
            try:
                raise self.kernelCommand.activeException()(None)
            except ExcPoint:
                if value.find(',')>-1:              # ABSOLUTE CARTESIAN INPUT
                    x, y=value.split(',')
                    point=Point(convertLengh(x), convertLengh(y))
                elif value.find(';')>-1:            # RELATIVE CARTESIAN INPUT
                    x, y=value.split(';')
                    x=self.scene.fromPoint.getx()+convertLengh(x)
                    y=self.scene.fromPoint.gety()+convertLengh(y)
                    point=Point(x, y)
                elif value.find('>')>-1:
                    ang, distance=value.split('>')
                    ang=convertAngle(ang)
                    distance=convertLengh(distance)
                    x=math.cos(float(ang))*float(distance)
                    y=math.sin(float(ang))*float(distance)
                    x=self.scene.fromPoint.getx()+float(x)
                    y=self.scene.fromPoint.gety()+float(y)
                    point=Point(x, y)
                else: # DISTANCE+ANGLE FROM SCENE set coordinate based on distance input and angle from mouse position on the scene
                    d=float(value)
                    pX=self.scene.mouseOnSceneX
                    pY=self.scene.mouseOnSceneY
                    if self.scene.forceDirection is not None:
                        pc=Point(pX, pY)
                        pc=self.correctPositionForcedDirection(pc, self.scene.forceDirection)
                        pX, pY=pc.getCoords()
                    #if frompoint is not none else exception
                    dx=pX-self.scene.fromPoint.getx()
                    dy=pY-self.scene.fromPoint.gety()
                    a=math.atan2(dy, dx)
                    x=self.scene.fromPoint.getx()+d*math.cos(a)
                    y=self.scene.fromPoint.gety()+d*math.sin(a)
                    point=Point(x, y)
            except (ExcEntity,ExcMultiEntity):
                entitys=self.getIdsString(value)
            except ExcEntityPoint:
                #(4@10,20)
                id, p=value.split('@')
                x, y=p.split(',')
                point=Point(float(x), float(y))
                entitys=self.getIdsString(id)
                return
            except (ExcLenght, ExcInt, ExcBool):
                distance=value
            except(ExcAngle):
                angle=value
            except(ExcText):
                text=value
        except:
            raise PyCadWrongImputData("BaseCommand : Wrong imput parameter for the command")
        return (point,entitys, distance,angle, text)

    def getIdsString(self, value):
        """
            return the entity from a string value (id)
        """
        return self.scene.getEntFromId(value)

    def updatePreview(self, point, distance, entity):
        """
            make update of the preview
        """
        if self.drawPreview:
            if self.__previewItem==None:
                self.__previewItem=getPreviewObject(self.kernelCommand)
                self.addPreviewItemToTheScene()
            if self.__previewItem!=None:
                self.__previewItem.updatePreview(point,
                                                distance,
                                                    self.kernelCommand)
    def addPreviewItemToTheScene(self):
        """
            add the preview item at the scene
        """
        if self.__previewItem!=None:
            self.__scene.addItem(self.__previewItem)
    def removePreviewItemToTheScene(self):
        """
            Remove all the preview items from the scene
        """
        if self.__previewItem!=None:
            self.__scene.clearPreview()

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
        return self.getDummyElement(self.__distance, index)

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
        """
            generic function to get an item from a generic array
        """
        if len(array)>=0 and index<=self.index:
            return array[index]
        raise IndexError


    def getDummyActive(self, func):
        """
            parametric function to return an element of an array
        """
        if self.index>=0:
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

    def correctPositionForcedDirection(self, point, force):
        """
            correct the POINT coords
            FORCE is the angle the defines the correction direction

            return the projection point of the POINT to the straight line defined by FORCE angle

            FORCE angle, in current inplementation, is setted by polarguides module when the mouse cursor is over a guide item
        """
        if point ==None:
            return None
        if force==None:
            return point
        lastSnap=self.__scene.fromPoint
        pF=point
        if force!=None and lastSnap!=None:
            v=Vector(lastSnap, Point(lastSnap.x+10.0*math.cos(force),  lastSnap.y+10.0*math.sin(force)))
            v1=Vector(lastSnap,point)
            pF=v.map(v1.point).point
            pF=pF+lastSnap

#            if abs(x-lastSnap.x)>abs(y-lastSnap.y):
#                y=lastSnap.y
#            else:
#                x=lastSnap.x

        return pF #Point(x, y)

    def getIntersection(self, entity, point):
        """
            this fucnticion compute the  snap intersection point
        """
        print "intersection"
        returnVal=None
        distance=None
        if entity!=None:
            geoEntityFrom=entity.geoItem
            entityList=self.__scene.collidingItems(entity)
            for ent in entityList:
                intPoint=find_intersections(ent.geoItem,geoEntityFrom)
                for tp in intPoint:
                    iPoint=Point(tp[0], tp[1])
                    if distance==None:
                        distance=iPoint.dist(point)
                        returnVal=iPoint
                    else:
                        spoolDist=iPoint.dist(point)
                        if distance>spoolDist:
                            distance=spoolDist
                            returnVal=iPoint
        return returnVal
