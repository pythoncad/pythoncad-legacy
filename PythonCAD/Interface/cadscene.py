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


from Interface.pycadapp import PyCadApp
from Generic.application import Application

from Interface.Entity.segment   import Segment
from Interface.Entity.arc       import Arc
from Interface.Entity.text      import Text
from Interface.Entity.ellipse   import Ellipse
from Interface.cadinitsetting   import *


class CadScene(QtGui.QGraphicsScene):
    
    def __init__(self, parent=None):
        super(CadScene, self).__init__(parent)
        # current file
        self.__filename = None
        # drawing limits
        self.__limits = None

    def __getLimits(self):
        return self.__limits
    
    Limits = property(__getLimits, None, None, "Gets the drawing limits")
    
        
    def newDocument(self):
        """
            create an empty document in temop file
        """
        document = PyCadApp.CreateNewDocument()
        if not document is None:
            self.__filename = document.dbPath
            self.initDocumentEvents()
        
        
    def openDocument(self, filename):
        '''
        Open an existing drawing with name 'filename' and
        Show this document in the graphical editor
        '''
        if (filename != None) and (len(filename) > 0):
            # Clear the scene
            self.clear()
            # Todo : check filename
            self.__filename = filename
            # open a new kernel
            document = PyCadApp.OpenDocument(self.__filename)
            if not document is None:
                self.initDocumentEvents()
                if document.haveDrawingEntitys():
                    # add entities to scene
                    self.populateScene(document)
        
                
    def initDocumentEvents(self):
        """
        Initialize the document events.
        """
        document = PyCadApp.ActiveDocument()
        if not document is None:
            document.showEntEvent += self.eventShow
            document.updateShowEntEvent += self.eventUpdate
            document.deleteEntityEvent += self.eventDelete
            document.massiveDeleteEvent += self.eventMassiveDelete
            document.undoRedoEvent += self.eventUndoRedo
        

    def importDocument(self, filename):        
        """
        Import a doc in the file
        """
        if (filename != None) and (len(filename) > 0):
            document = PyCadApp.ActiveDocument()
            if not document is None:
                document.importExternalFormat(filename)
                if document.haveDrawingEntitys():
                    # add entities to scene
                    self.populateScene(document)
            else:
                PyCadApp.critical("No document open.")
        return
              
                
    def saveAs(self, filename):            
        """
        Save the current document under an different name.
        """
        application = PyCadApp.Application()
        if not application is None:
            document = application.saveAs(filename)
            if not document is None:
                self.initDocumentEvents()
                if document.haveDrawingEntitys():
                    # add entities to scene
                    self.populateScene(document)
            
            
    def closeDocument(self):
        '''
        Close the current open document.
        '''
        if self.__filename != None:
            # close document from kernel
            application = PyCadApp.Application()
            if not application is None:
                application.closeDocument(self.__filename)
                # remove all items from the scene
                self.clear()
                # reset filename
                self.__filename = None
                # looking if there is other document in the application
                document = PyCadApp.ActiveDocument()
                if document:
                    self.__filename=document.dbPath
                    if document.haveDrawingEntitys():
                        # add entities to scene
                        self.populateScene(document) 
        else:
            # erase all entities
            self.clear()
        return

            
    def populateScene(self, document):
        '''
        Traverse all entities in the document and add these to the scene.
        '''
        entities = document.getEntityFromType(SCENE_SUPPORTED_TYPE)
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
            
