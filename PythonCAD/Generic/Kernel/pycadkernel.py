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
# This  module all the interface needed to talk with pythoncad database
#

import os
import sys
import cPickle
import logging
import time

from pycadundodb    import PyCadUndoDb
from pycadentdb     import PyCadEntDb
from pycadent       import PyCadEnt
from pycadbasedb    import PyCadBaseDb
from pycadstyle     import PyCadStyle
from pycaddbexception import EmptyDbSelect
from Entity.point import *

LEVELS = {'PyCad_Debug': logging.DEBUG,
          'PyCad_Info': logging.INFO,
          'PyCad_Warning': logging.WARNING,
          'PyCad_Error': logging.ERROR,
          'PyCad_Critical': logging.CRITICAL}

#set the debug level
level = LEVELS.get('PyCad_Error', logging.NOTSET)
logging.basicConfig(level=level)
#

class PyCadDbKernel(PyCadBaseDb):
    """
        This class provide basic operation on the pycad db database
        dbPath: is the path the database if None look in the some directory.
    """
    def __init__(self,dbPath=None):
        """
            init of the kernel
        """
        self.__logger=logging.getLogger('PyCadDbKernel')
        self.__logger.debug('__init__')
        PyCadBaseDb.__init__(self)
        self.createConnection(dbPath)
        # inizialize extentionObject
        self.__pyCadUndoDb=PyCadUndoDb(self.getConnection())
        self.__pyCadEntDb=PyCadEntDb(self.getConnection())
        # set the default style
        self.__activeStyleObj=PyCadStyle(0)
        # set the events
        self.__logger.debug('set events')
        self.saveEntityEvent=PyCadkernelEvent()
        self.deleteEntityEvent=PyCadkernelEvent()
        self.__logger.debug('Done inizialization')
        self.__bulkCommit=False
        self.__entId=self.__pyCadEntDb.getNewEntId()
        self.__bulkUndoIndex=-1 #undo index are alweys positive so we do not breke incase missing entity id

    def startMassiveCreation(self):
        """
            suspend the undo for write operation
        """
        self.__bulkCommit=True
        self.__bulkUndoIndex=self.__pyCadUndoDb.getNewUndo()

    def stopMassiveCreation(self):
        """
            Reactive the undo trace
        """
        self.__bulkCommit=False
        self.__bulkUndoIndex=-1

    def getEntity(self,entId):
        """
            get the entity from a given id
        """
        self.__logger.debug('getEntity')
        return self.__pyCadEntDb.getEntity(entId)

    def saveEntity(self,entity):
        """
            save the entity into the database
        """
        try:
            self.__pyCadUndoDb.suspendCommit()
            self.__pyCadEntDb.suspendCommit()
            if isinstance(entity,Point):
                self.savePoint(entity)
            else:
                raise TypeError ,"Type %s not supported from pythoncad kernel"%type(entity)
            if not self.__bulkCommit:
                self.__pyCadUndoDb.reactiveCommit()
                self.__pyCadEntDb.reactiveCommit()
                self.performCommit()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
         
    def savePoint(self,point):
        """
            save the point in to the dartabase
        """
        self.__entId+=1
        _points={}
        _points['POINT']=point

        _newDbEnt=PyCadEnt('POINT',_points,self.getActiveStyle(),self.__entId)
        if self.__bulkUndoIndex>=0:
            self.__pyCadEntDb.saveEntity(_newDbEnt,self.__bulkUndoIndex)
        else:
            self.__pyCadEntDb.saveEntity(_newDbEnt,self.__pyCadUndoDb.getNewUndo())
        

    def getActiveStyle(self):
        """
            Get the current style
        """
        self.__logger.debug('getActiveStyle')
        #return the id of the active style
        if self.__activeStyleObj==None:
            self.setActiveStyle(0) # in this case get the first style
        return self.__activeStyleObj

    def setActiveStyle(self,id,name=None):
        """
            set the current style
        """
        self.__logger.debug('setActiveStyle')
        # check if the style id is in the db
        # if not create the style in the db with default settings
        # get from db the object style pickled
        # set in a global variable self.__activeStyleObj=_newStyle
        pass

    def getStyle(self,id,name=None):
        """
            get the style object
        """
        #get the style object of the give id
        pass
    def getStyleList(self):
        """
            get all the style from the db
        """
        self.__logger.debug('getStyleList')
        # Make a query at the style Table and return an array of (stylesName,id)
        # this method is used for populate the style form ..
        pass

    activeStyleId=property(getActiveStyle,setActiveStyle)


    def unDo(self):
        """
            perform an undo operation
        """
        try:
            _newUndo=self.__pyCadUndoDb.dbUndo()
            self.setUndoVisible(_newUndo)
            self.setUndoHide(self.__pyCadUndoDb.getActiveUndoId())
        except UndoDb:
            print "Unable to perform undo : no elemnt to undo"
            # manage with a new raise or somthing else
        
        
    def reDo(self):
        """
            perform a redo operation
        """
        try:
            _activeRedo=self.__pyCadUndoDb.dbRedo()
            self.setUndoVisible(_newUndo)
        except UndoDb:
            print "Unable to perform redo : no element to redo"

    def setUndoVisible(self,undoId):
        """
            mark as undo visible all the entity with undoId
        """
        self.__pyCadEntDb.markUndoVisibility(undoId,1)
        #toto : perform an event call for refresh
        
    def setUndoHide(self,undoId):
        """
            mark as  undo hide all the entity with undoId
        """
        self.__pyCadEntDb.markUndoVisibility(undoId,0)
        #toto : perform an event call for refresh
        
    def clearUnDoHistory(self):
        """
            perform a clear history operation
        """
        self.__pyCadUndoDb.clearUndoTable()

    def deleteEntity(self,entity):
        """
            delete the entity from the database
        """
        pass


class PyCadkernelEvent(object):
    """
        this class fire the envent from the python kernel
    """
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handler.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("PythonCad Handler is not handling this event.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount

def test():
    logging.debug( "Create db kernel")
    kr=PyCadDbKernel()
    logging.debug("Create a point")
    startTime=time.clock()
    nEnt=1
    #kr.startMassiveCreation()
    for i in range(nEnt):
        basePoint=Point(10,i)
        kr.saveEntity(basePoint)
    #kr.performCommit()
    endTime=time.clock()-startTime
    print "Create n: %s entity in : %ss"%(str(nEnt ),str(endTime))

    kr.unDo()  
    kr.reDo()
    
#test()

"""
    to be tested :
    deleteEntity
    setUndoHide
    setUndoVisible
    saveEntity
"""

