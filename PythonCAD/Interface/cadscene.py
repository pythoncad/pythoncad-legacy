#
# Copyright (c) 2010 Matteo Boscolo, Gertwin Groen
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
# This module the graphics scene class
#
#

import math

from PyQt4 import QtCore, QtGui

from Generic.application import Application

from Interface.pycadapp             import PyCadApp
from Interface.Entity.base          import BaseEntity
from Interface.Entity.segment       import Segment
from Interface.Entity.arc           import Arc
from Interface.Entity.text          import Text
from Interface.Entity.ellipse       import Ellipse
from Interface.Entity.arrowitem     import ArrowItem
from Interface.cadinitsetting       import *
from Interface.unitparser           import convertAngle
from Interface.dinamicentryobject   import DinamicEntryLine
from Interface.Preview.base         import BaseQtPreviewItem

from Kernel.pycadevent              import PyCadEvent

class CadScene(QtGui.QGraphicsScene):
    def __init__(self, document, parent=None):
        super(CadScene, self).__init__(parent)
        # current file
        #self.__filename = None
        # drawing limits
        self.__limits = None
        # scene custom event
        self.pyCadScenePressEvent=PyCadEvent()
        self.pyCadSceneApply=PyCadEvent()
        self.updatePreview=PyCadEvent()
        self.zoomWindows=PyCadEvent()
        self.keySpace=PyCadEvent()
        self.__document=document
        self.__oldClickPoint=None
        self.needPreview=False
        self.forceDirection=None
        # dinamic text editor
        self.qtInputPopUp=DinamicEntryLine()
        self.qtInputPopUp.onEnter+=self._qtInputPopUpReturnPressed
        self.addWidget(self.qtInputPopUp)
        # setGeometry 
        self.mouseX=0.0
        self.mouseY=0.0
        self.isInPan=False
        # Create 0,0 arrows
        #self.addItem(ArrowItem())
        #secondArrow=ArrowItem()
        #secondArrow.setRotation(-90.0)
        #self.addItem(secondArrow)
        #
        self._cmdZoomWindow=None
        
    def _qtInputPopUpReturnPressed(self):
        self.forceDirection="F"+self.qtInputPopUp.text
        
    def mouseMoveEvent(self, event):
        """
            mouse move event
        """
        if self.__oldClickPoint:
            distance=self.getDistance(event)
            x, y=self.getPosition(event.scenePos())
            point=QtCore.QPointF(x, y*-1.0)
            self.updatePreview(self,point, distance)
        self.mouseX=event.scenePos().x()
        self.mouseY=event.scenePos().y()
        super(CadScene, self).mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        if not self.isInPan:
            qtItem=self.itemAt(event.scenePos())
            p= QtCore.QPointF(event.scenePos().x(),event.scenePos().y())
            if qtItem:
                print "item : ", qtItem
                qtItem.setSelected(True)
                self.updateSelected()
            else:
                print "No item selected"
            #re fire the event
        super(CadScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.isInPan:
            x, y=self.getPosition(event.scenePos())
            self.updateSelected()
            qtItems=[item for item in self.selectedItems() if isinstance(item, BaseEntity)]
            distance=self.getDistance(event)
            self.__oldClickPoint=event.scenePos()
            pyCadEvent=((x, y), qtItems, distance)
            self.pyCadScenePressEvent(self, pyCadEvent)
            self.forceDirection=None
            #re fire the event
        if self._cmdZoomWindow:
            self.zoomWindows(self.selectionArea().boundingRect())
            self._cmdZoomWindow=None
        super(CadScene, self).mouseReleaseEvent(event)
        
    def getDistance(self, event):
        distance=None
        if self.__oldClickPoint:
            deltaX=abs(self.__oldClickPoint.x()-event.scenePos().x())
            deltaY=abs(self.__oldClickPoint.y()-event.scenePos().y())
            distance=math.sqrt(deltaX**2+deltaY**2)
        return distance
        
    def getPosition(self, eventPos):
        """
            correct the mouse cords 
        """
        x=eventPos.x()
        y=eventPos.y()
        if self.forceDirection and  self.__oldClickPoint:
            if self.forceDirection=="H":
                y=self.__oldClickPoint.y()
            elif self.forceDirection=="V":
                x=self.__oldClickPoint.x()
            elif self.forceDirection.find("F")>=0:
                angle=convertAngle(self.forceDirection.split("F")[1])
                if angle:
                    x=self.__oldClickPoint.x()+x
                    y=self.__oldClickPoint.y()+math.cos(angle)*x
        y=y*-1.0
        return x, y
    
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.qtInputPopUp.hide()
            self.clearSelection()
            self.updateSelected()
            self.forceDirection=None
        elif event.key()==QtCore.Qt.Key_Return:
            self.pyCadSceneApply()
        elif event.key()==QtCore.Qt.Key_Space:
            self.keySpace(self, event)
        elif event.key()==QtCore.Qt.Key_H:
            self.forceDirection='H'
        elif event.key()==QtCore.Qt.Key_V:
            self.forceDirection='V'
        elif event.key()==QtCore.Qt.Key_F:
            self.qtInputPopUp.setText('')
            self.qtInputPopUp.setPos(self.mouseX, self.mouseY)
            self.qtInputPopUp.show()
        super(CadScene, self).keyPressEvent(event)
    
    def updateSelected(self):
        """
            update all the selected items
        """
        for item in self.selectedItems():
            item.updateSelected()

    def clearPreview(self):
        entitys=[item for item in self.items() if isinstance(item, BaseQtPreviewItem)]
        for ent in entitys:
            self.removeItem(ent)
        self.__oldClickPoint=None
        
    @property    
    def Limits(self):
        """
            Gets the drawing limits
        """
        return self.__limits
        

    def initDocumentEvents(self):
        """
        Initialize the document events.
        """
        if not self.__document is None:
            self.__document.showEntEvent        += self.eventShow
            self.__document.updateShowEntEvent  += self.eventUpdate
            self.__document.deleteEntityEvent   += self.eventDelete
            self.__document.massiveDeleteEvent  += self.eventMassiveDelete
            self.__document.undoRedoEvent       += self.eventUndoRedo

    def populateScene(self, document):
        '''
        Traverse all entities in the document and add these to the scene.
        '''
        entities = self.__document.getEntityFromType(SCENE_SUPPORTED_TYPE)
        for entity in entities:
            self.addGraficalObject(entity)
 
    def addGraficalObject(self, entity):                
        """
        Add the single object
        """
        newQtEnt=None
        entityType=entity.getEntityType()
        if entityType in SCENE_SUPPORTED_TYPE:
            newQtEnt=SCANE_OBJECT_TYPE[entityType](entity)
            self.addGraficalItem(newQtEnt)
    
    def addGraficalItem(self, qtItem):
        """
            add item to the scene 
        """
        if qtItem:
            self.addItem(qtItem)
            # adjust drawing limits
            self.updateLimits(qtItem.boundingRect())  
    
    def eventUndoRedo(self, document, entity):
        """
        Manage the undo redo event
        """
        self.clear()
        self.populateScene(document)


    def eventShow(self, document, entity):        
        """
        Manage the show entity event
        """
        self.addGraficalObject(entity)
    
    
    def eventUpdate(self, document, entity):    
        """
        Manage the Update entity event  
        """
        self.updateItemsFromID([entity])
    

    def eventDelete(self, document, entity):    
        """
        Manage the Delete entity event
        """
        #import time 
        #startTime=time.clock()
        self.deleteEntity([entity])
        #endTime=time.clock()-startTime
        #print "eventDelete in %s"%str(endTime)
        
    def eventMassiveDelete(self, document,  entitys):
        """
            Massive delete of all entity event
        """
        #import time 
        #startTime=time.clock()
        self.deleteEntity(entitys)
        #endTime=time.clock()-startTime
        #print "eventDelete in %s"%str(endTime)    
    
    def deleteEntity(self, entitys):
        """
            delete the entity from the scene
        """
        dicItems=dict([( item.ID, item)for item in self.items() if isinstance(item, BaseEntity)])
        for ent in entitys:
            self.removeItem(dicItems[ent.getId()])

    def updateLimits(self, rect):
        # init size
        if self.__limits == None:
            self.__limits = rect
            return
        # left side
        if rect.left() < self.__limits.left():
            self.__limits.setLeft(rect.left())
        # right side
        if rect.right() > self.__limits.right():
            self.__limits.setRight(rect.right())
        # bottom side
        if rect.bottom() < self.__limits.bottom():
            self.__limits.setBottom(rect.bottom())
        # top side
        if rect.top() > self.__limits.top():
            self.__limits.setTop(rect.top())
        return
            
    
    def updateItemsFromID(self,entitys):
        """
        Update the scene from the Entity []
        """
        dicItems=dict([( item.ID, item)for item in self.items() if isinstance(item, BaseEntity)])
        for ent in entitys:
            if ent.getId() in dicItems:
                self.removeItem(dicItems[ent.getId()])
                self.addGraficalObject(ent)

        
    def updateItemsFromID_2(self,entities):
        """
            update the scene from the Entity []
        """
        ids=[ent.getId() for ent in entities]
        items=[item for item in self.items() if item.ID in ids]
        for item in items:
                self.removeItem(item)
        for ent in entities:
                self.addGraficalObject(ent)
