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


from Interface.globals import *
from Interface.segment  import Segment
from Interface.arc      import Arc
from Interface.text     import Text


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
    
    
#    def getApplication(self):
#        """
#            get The application object 
#        """
#        return self.__application
        
    def newDocument(self):
        """
            create an empty document in temop file
        """
        self.__application.newDocument()
        
    def openDocument(self, filename):
        if (filename != None) and (len(filename) > 0):
            # Clear the scene
            self.clear()
            # todo: check filename
            self.__filename = filename
            # open a new kernel
            application = Application()
            if not application is None:
                application.openDocument(self.__filename)
                document = application.getActiveDocument()
                #if self._cadkernel.getEntityFromType('SEGMENT'):
                if document.haveDrawingEntitys():
                    # add entities to scene
                    self.populateScene(document)
        return
    
            
    def importDocument(self, filename):        
        """
            import a doc in the file
        """
        if (filename != None) and (len(filename) > 0):
            appl = Application()
            if not appl is None:
                doc = appl.getActiveDocument()
                if doc:
                    doc.importExternalFormat(filename)
                    if doc.haveDrawingEntitys():
                        # add entities to scene
                        self.populateScene(doc)
                else:
                    critical("No document open.")
            else:
                critical("No application constructed.")
        return
              
                
    def closeDocument(self):
        if self.__filename != None:
            # close document from kernel
            appl = Application()
            if appl:
                appl.closeDocument(self.__filename)
                # remove all items from the scene
                self.clear()
                # reset filename
                self.__filename = None
                #looking if there is other document in the appl
                document=appl.getActiveDocument()
                if document:
                    if document.haveDrawingEntitys():
                        # add entities to scene
                        self.populateScene(document) 
        else:
            self.clear()
        return

            
    def populateScene(self, document):
        for entName in ("SEGMENT", "ARC", "TEXT"):
            entities = document.getEntityFromType(entName)
            for entity in entities:
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
        return
    
                    
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
            
