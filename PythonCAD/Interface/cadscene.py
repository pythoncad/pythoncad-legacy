#
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

import math, time

from PyQt4 import QtCore, QtGui

from Generic.application import Application

from Interface.pycadapp             import PyCadApp
from Interface.Entity.base          import BaseEntity
from Interface.Entity.segment       import Segment
from Interface.Entity.arc           import Arc
from Interface.Entity.text          import Text
from Interface.Entity.ellipse       import Ellipse
from Interface.Entity.arrowitem     import ArrowItem
from Interface.Entity.actionhandler import PositionHandler
from Interface.Entity.dinamicentryobject   import DinamicEntryLine
from Interface.cadinitsetting       import *
from Interface.Preview.base         import PreviewBase

from Interface.DrawingHelper.snap import *
from Interface.DrawingHelper.polarguides import GuideHandler

from Kernel.pycadevent              import PyCadEvent
from Kernel.GeoEntity.point         import Point
from Kernel.exception               import *
from Kernel.entity                  import Entity

class CadScene(QtGui.QGraphicsScene):
    def __init__(self, document, parent=None):
        super(CadScene, self).__init__(parent)
        # drawing limits
        self.setSceneRect(-10000, -10000, 20000, 20000)
        # scene custom event
        self.zoomWindows=PyCadEvent()
        self.fireCommandlineFocus=PyCadEvent()
        self.fireKeyShortcut=PyCadEvent()
        self.fireKeyEvent=PyCadEvent()
        self.fireWarning=PyCadEvent()
        self.fireCoords=PyCadEvent()
        #fire Pan and Zoom events to the view
        self.firePan=PyCadEvent()
        self.fireZoomFit=PyCadEvent()
        self.__document=document
        self.needPreview=False
        self.forceDirectionEnabled=False
        self.forceDirection=None
        self.__lastPickedEntity=None
        self.isInPan=False
        self.forceSnap=None
        self._cmdZoomWindow=None
        self.showHandler=False
        self.posHandler=None
        #
        # new command implementation
        #
        self.__activeKernelCommand=None
        self.activeICommand=None
        #
        self.__grapWithd=20.0
        #
        # Input implemetation by carlo
        #
        self.fromPoint=None #frompoint is assigned in icommand.getClickedPoint() and deleted by applycommand and cancelcommand, is needed for statusbar coordinates dx,dy
        self.selectionAddMode=False

        # Init loading of snap marks
        self.initSnap()

        # Init loading of guides
        self.isGuided=None
        self.isGuideLocked=None
        self.initGuides()

        # scene aspect
        r, g, b=BACKGROUND_COLOR #defined in cadinitsetting
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(r, g, b), QtCore.Qt.SolidPattern))

    def initSnap(self):
        # Init loading of snap marks
        self.snappingPoint=SnapPoint(self)
        self.endMark=SnapEndMark(0.0, 0.0)
        self.addItem(self.endMark)

    def initGuides(self):
        self.GuideHandler=GuideHandler(self, 0.0, 0.0,0.0 )
        self.addItem(self.GuideHandler)
        self.GuideHandler.reset()

    @property
    def activeKernelCommand(self):
        """
            return the active command
        """
        return self.__activeKernelCommand
    @activeKernelCommand.setter
    def activeKernelCommand(self, value):
        self.__activeKernelCommand=value

    def setActiveSnap(self, value):
        if self.activeICommand!=None:
            self.activeICommand.activeSnap=value
            self.snappingPoint.activeSnap=value

    def _qtInputPopUpReturnPressed(self):
        self.forceDirection="F"+self.qtInputPopUp.text

# ###############################################MOUSE EVENTS
# ##########################################################

    def mouseMoveEvent(self, event):
        scenePos=event.scenePos()
        mouseOnSceneX=scenePos.x()
        mouseOnSceneY=scenePos.y()*-1.0
        self.geoMousePointOnScene=Point(mouseOnSceneX,mouseOnSceneY)
        #
        # This event manages middle mouse button PAN
        #
        if self.isInPan:
            self.firePan(None, event.scenePos())
        #
        #This event manages the status bar coordinates display (relative or absolute depending on self.fromPoint)
        #
        else:
            if self.fromPoint==None:
                self.fireCoords(mouseOnSceneX, mouseOnSceneY, "abs")
            else:
                x=mouseOnSceneX-self.fromPoint.getx()
                y=mouseOnSceneY-self.fromPoint.gety()
                self.fireCoords(x, y, "rel")
        #
        #This seems needed to preview commands
        #
        ps=self.geoMousePointOnScene
        if self.activeICommand:
            #SNAP PREVIEW
            if self.activeKernelCommand.activeException()==ExcPoint or self.activeKernelCommand.activeException()==ExcLenght:
                item=self.activeICommand.getEntity(ps)
                if item:
                    ps=self.snappingPoint.getSnapPoint(self.geoMousePointOnScene, item)
                    if ps!=self.geoMousePointOnScene:
                        self.endMark.move(ps.getx(), ps.gety()*-1.0)
                else:
                    self.hideSnapMarks()
            qtItem=[self.itemAt(scenePos)]
            self.activeICommand.updateMauseEvent(ps, qtItem)
        super(CadScene, self).mouseMoveEvent(event)
        return



    def mousePressEvent(self, event):
        if event.button()==QtCore.Qt.MidButton:
            self.isInPan=True
            self.firePan(True, event.scenePos())
        if not self.isInPan:
            qtItem=self.itemAt(event.scenePos())
            if qtItem:
                qtItem.setSelected(True)
                self.updateSelected()
                if event.button()==QtCore.Qt.RightButton:
                    self.showContextMenu(qtItem, event)
        super(CadScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button()==QtCore.Qt.MidButton:
            self.isInPan=False
            self.firePan(False, None)
        if not self.isInPan:
            self.updateSelected()
            if self.activeICommand:
                if event.button()==QtCore.Qt.RightButton:
                    try:
                        self.activeICommand.applyDefault()
                    except PyCadWrongInputData:
                        self.fireWarning("Wrong input value")
                if event.button()==QtCore.Qt.LeftButton:
                    point=Point(event.scenePos().x(), event.scenePos().y()*-1.0)
                    qtItems=[item for item in self.selectedItems() if isinstance(item, BaseEntity)]
                    if self.showHandler:
                        if self.posHandler==None:
                            self.posHandler=PositionHandler(event.scenePos())
                            self.addItem(self.posHandler)
                        else:
                            self.posHandler.show()
                    # fire the mouse to the ICommand class
                    self.activeICommand.addMauseEvent(point=point,
                                                    entity=qtItems,
                                                    force=self.forceDirection)
            else:
                self.hideHandler()

        if self._cmdZoomWindow:
            self.zoomWindows(self.selectionArea().boundingRect())
            self._cmdZoomWindow=None
            self.clearSelection() #clear the selection after the window zoom, why? because zoom windows select entities_>that's bad

        super(CadScene, self).mouseReleaseEvent(event)
        return

    def showContextMenu(self, selectedQtItems, event):
        """
            show a context menu
        """
        def delete():
            self.fireKeyShortcut('DELETE')

        def property():
            self.fireKeyShortcut('PROPERTY')

        contexMenu=QtGui.QMenu()
        # Create Actions
        removeAction=contexMenu.addAction("Delete")
        QtCore.QObject.connect(removeAction, QtCore.SIGNAL('triggered()'), delete)

        propertyAction=contexMenu.addAction("Property")
        QtCore.QObject.connect(propertyAction, QtCore.SIGNAL('triggered()'), property)
        contexMenu.exec_(event.screenPos())
        del(contexMenu)

    def hanhlerDoubleClick(self):
        """
            event add from the handler
        """
        point=Point(self.posHandler.scenePos.x(), self.posHandler.scenePos.y()*-1.0)
        self.activeICommand.addMauseEvent(point=point,
                                            distance=self.posHandler.distance,
                                            angle=self.posHandler.angle)
        self.hideHandler()

    def hideHandler(self):
        """
            this function is used to hide the handler
        """
        if self.posHandler!=None:
            self.posHandler.hide()

    def hideSnapMarks(self):
        """
            this function is used to hide the handler
        """
        self.endMark.hide()

    def mouseDoubleClickEvent(self, event):
        if event.button()==QtCore.Qt.MidButton:
            self.fireZoomFit()
        else:
            return QtGui.QGraphicsScene.mouseDoubleClickEvent(self, event)

    def cancelCommand(self):
        """
            cancel the active command
        """
        self.clearSelection()
        self.updateSelected()
        #self.forceDirection=None
        self.__activeKernelCommand=None
        self.activeICommand=None
        self.showHandler=False
        self.clearPreview()
        self.hideSnapMarks()
        self.fromPoint=None
        self.GuideHandler.reset()

# ################################################# KEY EVENTS
# ##########################################################

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Return:
            if self.activeICommand!=None:
                self.activeICommand.applyCommand()
        elif event.key()==QtCore.Qt.Key_Escape:
            self.cancelCommand()
        elif event.key()==QtCore.Qt.Key_Space:
            self.fireCommandlineFocus(self, event)
        elif event.key()==QtCore.Qt.Key_Shift:
            if self.isGuided==True:
                self.isGuideLocked=True
                print "GUIDE LOCKED"
            else:
                self.selectionAddMode=True

#        elif event.key()==QtCore.Qt.Key_F8:  <<<<this must maybe be implemented in cadwindow
#            if self.forceDirection is None:
#                self.forceDirection=True
#            else:
#                self.forceDirection=None
#            print self.forceDirection
#            self.forceDirection='H'        <<<<<<<H and V are substituted by ortho mode, for future implementations it could be nice if shift pressed locks the direction of the mouse pointer
#        elif event.key()==QtCore.Qt.Key_V:  <<<Ortho mode should be rewritten allowing to enter step angles and snap direction
#            self.forceDirection='V'
        elif event.key()==QtCore.Qt.Key_Q: #Maybe we could use TAB
            self.showHandler=True
        else:
            if self.activeICommand!=None:
                self.fireCommandlineFocus(self, event)
                self.fireKeyEvent(event)
            elif event.key() in KEY_MAP:
                    #exec(KEY_MAP[event.key()])
                    self.fireKeyShortcut(KEY_MAP[event.key()])
        super(CadScene, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key()==QtCore.Qt.Key_Shift:
#            if self.activeICommand!=None:
#                if self.activeKernelCommand.activeException()==ExcMultiEntity:
            if self.isGuided==True:
                self.isGuideLocked=None
                self.isGuided=None
                self.GuideHandler.hideGuides()
            else:
                self.selectionAddMode=False
        else:
            pass

    def textInput(self, value):
        """
            someone give some test imput at the scene
        """
        if self.activeICommand!=None:
            #self.forceDirection=None # reset force direction for the imput value
            self.updateSelected()
            self.activeICommand.addTextEvent(value)
        return

    def updateSelected(self):
        """
            update all the selected items
        """
        for item in self.selectedItems():
            item.updateSelected()

    def clearPreview(self):
        """
            remove the preview items from the scene
        """
        entitys=[item for item in self.items() if isinstance(item, PreviewBase)]
        for ent in entitys:
            self.removeItem(ent)

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
            self.__document.hideEntEvent        += self.eventDelete

    def populateScene(self, document):
        """
            Traverse all entities in the document and add these to the scene.
        """
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
        if qtItem!=None:
            self.addItem(qtItem)

    def eventUndoRedo(self, document, entity):
        """
            Manage the undo redo event
        """
        self.clear()
        self.populateScene(document)
        self.initSnap()
        self.initGuides()


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
            if ent.eType!="LAYER":
                itemId=ent.getId()
                if dicItems.has_key(itemId):
                    self.removeItem(dicItems[itemId])

    def getEntFromId(self, id):
        """
            get the grafical entity from an id
        """
        dicItems=dict([( item.ID, item)for item in self.items() if isinstance(item, BaseEntity) and item.ID==id])
        if len(dicItems)>0:
            return dicItems[0][1]
        return None

    def updateItemsFromID(self,entitys):
        """
            Update the scene from the Entity []
        """
        dicItems=self.getAllBaseEntity()
        for ent in entitys:
            if ent.getId() in dicItems:
                self.removeItem(dicItems[ent.getId()])
                self.addGraficalObject(ent)

    def getAllBaseEntity(self):
        """
            get all the base entity from the scene
        """
        return dict([( item.ID, item)for item in self.items() if isinstance(item, BaseEntity)])

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
