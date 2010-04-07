#!/usr/bin/env python
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
# This  module provide the main api interface of pythoncad
#
#
import sys
from Generic.Kernel.pycaddbexception    import *
from Generic.Kernel.pycadkernel         import *
from Generic.Kernel.pycadcommands       import *
from Generic.Kernel.Entity.point        import Point


class PyCadApplication(object):
    """
        this class provide the real pythoncad api interface ..
    """
    def __init__(self, **args):
        self.kernel=PyCadDbKernel()
        self.__applicationCommand=APPLICATION_COMMAND
        # Setting up Application Events
        self.startUpEvent=PyCadkernelEvent()
        self.beforeOpenDocumentEvent=PyCadkernelEvent()
        self.afterOpenDocumentEvent=PyCadkernelEvent()
        self.beforeCloseDocumentEvent=PyCadkernelEvent()
        self.afterCloseDocumentEvent=PyCadkernelEvent()
        self.activeteDocumentEvent=PyCadkernelEvent()
        
        # manage Document inizialization
        self.__Docuemnts={}
        if args.has_key('open'):
            openDocument(args['open'])
        else:
            self.__ActiveDocument=None
        # Fire the Application inizialization
        self.startUpEvent(self)

    def setActiveDocument(self, document):    
        """
            set the document to active
        """
        if document:
            if self.__Docuemnts.has_key(document.dbPath):
                self.__ActiveDocument=self.__Docuemnts[document.dbPath]
            else:
                raise EntityMissing("Unable to set active the document %s"%str(document.dbPath))
        else:
            self.__ActiveDocument=document
        self.activeteDocumentEvent(self, self.__ActiveDocument)   

    def getCommand(self,commandType):
        """
            Get a command of commandType
        """
        if not self.__ActiveDocument:
            raise EntityMissing("Miss Active document in the application")
        if self.__applicationCommand.has_key(commandType):
            cmd=self.__applicationCommand[commandType]
            cmdIstance=cmd(self.__ActiveDocument) # fixme : c'e' un errore qui ... controllare
            return cmdIstance
        else:
            raise PyCadWrongCommand("") 
    
    def openDocument(self, fileName):
        """
            open a new document 
        """
        self.beforeOpenDocumentEvent(self, fileName)
        if not self.__Docuemnts.has_key(fileName):
            self.__Docuemnts[fileName]=PyCadDbKernel(fileName)
        self.afterOpenDocumentEvent(self, self.__Docuemnts[fileName])   #   Fire the open document event
        self.setActiveDocument(self.__Docuemnts[fileName])              #   Set Active the document

    def closeDocument(self, fileName):
        """
            close the document
        """
        self.beforeCloseDocumentEvent(self, fileName)
        if self.__Docuemnts.has_key(fileName):
            del(self.__Docuemnts[fileName])
            for keyDoc in self.__Docuemnts:
                self.setActiveDocument(self.__Docuemnts[keyDoc])
                break
            else:
                self.setActiveDocument(None)
        else:
            raise IOError, "Unable to remove the file %s"%str(fileName)
        self.afterCloseDocumentEvent(self)
        
    def getActiveDocuemnt(self):
        """
            get The active Document
        """
        return self.__ActiveDocument
        
    def getDocuments(self):
        """
            get the Docuemnts Collection
        """    
        return self.__Docuemnts



