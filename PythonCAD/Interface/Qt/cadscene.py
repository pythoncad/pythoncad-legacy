

from PyQt4 import QtCore, QtGui
from Generic.Kernel.application import Application
from Interface.Qt.segment import Segment


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
    

    def openDocument(self, filename):
        if (filename != None) and (len(filename) > 0):
            # todo: check filename
            self.__filename = filename
            # open a new kernel
            self.__application.openDocument(self.__filename)
            document = self.__application.getActiveDocument()
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
        
            
    def populateScene(self, document):
        
        entities = document.getEntityFromType("SEGMENT")
        
        for entity in entities:
            # add segment to scene port
            segment = Segment(entity)
            self.addItem(segment)
            # adjust drawing limits
            self.updateLimits(segment.boundingRect())
            
        
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

            
