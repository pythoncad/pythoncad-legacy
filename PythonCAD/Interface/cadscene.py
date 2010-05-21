
from PyQt4 import QtCore, QtGui
from Generic.Kernel.application import Application

from Interface.Entity.segment   import Segment
from Interface.Entity.arc       import Arc
from Interface.Entity.text      import Text
from Interface.Entity.ellipse   import Ellipse
from Interface.cadinitsetting   import *

class CadScene(QtGui.QGraphicsScene):
    
    def __init__(self, parent=None):
        super(CadScene, self).__init__(parent)
        self.__application = Application()
        # current file
        self.__filename = None
        # drawing limits
        self.__limits = None

    def __getLimits(self):
        return self.__limits
    
    Limits = property(__getLimits, None, None, "Gets the drawing limits")
    def getApplication(self):
        """
            get The application object 
        """
        return self.__application
        
    def newDocument(self):
        """
            create an empty document in temop file
        """
        self.__application.newDocument()
        self.documentEvent()
        
    def openDocument(self, filename):
        if (filename != None) and (len(filename) > 0):
            # Clear the scene
            self.clear()
            # Todo : check filename
            self.__filename = filename
            # open a new kernel
            self.__application.openDocument(self.__filename)
            document = self.__application.getActiveDocument()
            self.documentEvent()
            if document.haveDrawingEntitys():
                # add entities to scene
                self.populateScene(document)
                
    def documentEvent(self):
        """
            set the document event
        """
        document = self.__application.getActiveDocument()
        document.showEntEvent+=self.eventShow
        document.updateShowEntEvent+=self.eventUpdate
        document.deleteEntityEvent+=self.eventDelete
        document.undoRedoEvent+=self.eventUndoRedo
        
    def importDocument(self, filename):        
        """
            import a document in the file
        """
        if (filename != None) and (len(filename) > 0):
            document = self.__application.getActiveDocument()
            document.importExternalFormat(filename)
            if document.haveDrawingEntitys():
                # add entities to scene
                self.populateScene(document)
                
    def closeDocument(self):
        if self.__filename != None:
            # close document from kernel
            self.__application.closeDocument(self.__filename)
            # remove all items from the scene
            self.clear()
            # reset filename
            self.__filename = None
            #looking if there is other document in the application
            document=self.__application.getActiveDocument()
            if document:
                if document.haveDrawingEntitys():
                    # add entities to scene
                    self.populateScene(document) 
        else:
            self.clear()    
            
    def populateScene(self, document):
        
        entities = document.getEntityFromType(SCENE_SUPPORTED_TYPE)
        for entity in entities:
            self.addGraficalObject(entity)
 
    def addGraficalObject(self, entity):                
        """
            add the single object
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
            manage the undo redo event
        """
        self.clear()
        self.populateScene(document)

    def eventShow(self, document, entity):        
        """
            manage the show entity event
        """
        self.addGraficalObject(entity)
    
    def eventUpdate(self, document, entity):    
        """
            manage the Update entity event  
        """
        self.updateItemsFromID([entity])
    def eventDelete(self, document, entity):    
        """
            manage the Delete entity event
        """
        self.deleteEntity([entity])
        
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
    
    def updateItemsFromID(self,entitys):
        """
            update the scene from the Entity []
        """
        dicItems=dict([( item.ID, item)for item in self.items()])
        for ent in entitys:
            if ent.getId() in dicItems:
                self.removeItem(dicItems[ent.getId()])
                self.addGraficalObject(ent)
