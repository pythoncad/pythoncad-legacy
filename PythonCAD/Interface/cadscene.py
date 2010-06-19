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

from PyQt4 import QtCore, QtGui

from Generic.application import Application

from Interface.pycadapp         import PyCadApp
from Interface.Entity.segment   import Segment
from Interface.Entity.arc       import Arc
from Interface.Entity.text      import Text
from Interface.Entity.ellipse   import Ellipse
from Interface.cadinitsetting   import *

from Kernel.pycadevent          import PyCadEvent

class CadScene(QtGui.QGraphicsScene):
    def __init__(self, document, parent=None):
        super(CadScene, self).__init__(parent)
        # current file
        #self.__filename = None
        # drawing limits
        self.__limits = None
        #scene custom event
        self.pyCadViewPressEvent=PyCadEvent()
        self.__document=document
        #dinamic text editor
        #self.qtText=QtGui.QTextEdit()
        #self.qtText.hide()
        #self.addWidget(self.qtText)
    
    def mousePressEvent(self, event):
        qtItem=self.itemAt(event.scenePos())
        p= QtCore.QPointF(event.scenePos().x(),event.scenePos().y())
        if qtItem:
            print "item : ", qtItem.toolTipMessage, qtItem.zValue()
            qtItem.setSelected(True)
            self.updateSelected()
        else:
            print "No item selected"
        #items=self.items(p)
        #ii=0
        #for i in items:
        #    print ii,"item : ", i.toolTipMessage
        #    ii+=1
            
        pyCadEvent=((event.scenePos().x(), event.scenePos().y()*-1.0), qtItem)
        self.pyCadViewPressEvent(self, pyCadEvent)
        super(CadScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.updateSelected()
        super(CadScene, self).mouseReleaseEvent(event)
    
    
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
                self.clearSelection()
                self.updateSelected()
        super(CadScene, self).keyPressEvent(event)
    
    def updateSelected(self):
        """
            update all the selected items
        """
        for item in self.selectedItems():
            item.updateSelected()

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
            self.__document.showEntEvent += self.eventShow
            self.__document.updateShowEntEvent += self.eventUpdate
            self.__document.deleteEntityEvent += self.eventDelete
            self.__document.massiveDeleteEvent += self.eventMassiveDelete
            self.__document.undoRedoEvent += self.eventUndoRedo

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
            self.addItem(newQtEnt)
            # adjust drawing limits
            self.updateLimits(newQtEnt.boundingRect())  
 
    
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
        import time 
        startTime=time.clock()
        self.deleteEntity([entity])
        endTime=time.clock()-startTime
        print "eventDelete in %s"%str(endTime)
        
    def eventMassiveDelete(self, document,  entitys):
        """
            Massive delete of all entity event
        """
        import time 
        startTime=time.clock()
        self.deleteEntity(entitys)
        endTime=time.clock()-startTime
        print "eventDelete in %s"%str(endTime)    
    
    def deleteEntity(self, entitys):
        """
            delete the entity from the scene
        """
        dicItems=dict([( item.ID, item)for item in self.items()])
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
        dicItems=dict([( item.ID, item)for item in self.items()])
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
