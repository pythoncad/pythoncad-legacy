
from PyQt4 import QtCore, QtGui
from Generic.Kernel.application import Application
from Interface.segment  import Segment
from Interface.arc      import Arc
from Interface.text     import Text

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
        document = self.__application.getActiveDocument()
        document.showEnt+=self.eventShow
        
    def openDocument(self, filename):
        if (filename != None) and (len(filename) > 0):
            # Clear the scene
            self.clear()
            # todo: check filename
            self.__filename = filename
            # open a new kernel
            self.__application.openDocument(self.__filename)
            document = self.__application.getActiveDocument()
            document.showEnt+=self.eventShow
            #if self._cadkernel.getEntityFromType('SEGMENT'):
            if document.haveDrawingEntitys():
                # add entities to scene
                self.populateScene(document)
            
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
        for entName in ("SEGMENT", "ARC", "TEXT"):
            entities = document.getEntityFromType(entName)
            for entity in entities:
                addGraficalObject(entity)
 
    def addGraficalObject(self, entity):                
        """
            add the single object
        """
        newQtEnt=None
        if entity.getEntityType()=="SEGMENT":
            # add segment to scene port
            newQtEnt= Segment(entity)
        elif entity.getEntityType()=="ARC":
            # add arc to scene port
            newQtEnt = Arc(entity)
        elif entity.getEntityType()=="TEXT":
            # add Text to scene port
            newQtEnt = Text(entity)
        if newQtEnt:
            self.addItem(newQtEnt)
            # adjust drawing limits
            self.updateLimits(newQtEnt.boundingRect())  
    
    def eventShow(self, document, entity):        
        """
            manage the fired event
        """
        self.addGraficalObject(entity)
        
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

            
