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
        this class provide basic operation on the pycad db database
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
        #inizialize extentionObject
        self.__pyCadUndoDb=PyCadUndoDb(self.getConnection())
        self.__pyCadEntDb=PyCadEntDb(self.getConnection())
        # set the default style
        self.__activeStyleObj=PyCadStyle(0)
        # set the events
        self.__logger.debug('set events')
        self.saveEntityEvent=PyCadkernelEvent()
        self.deleteEntityEvent=PyCadkernelEvent()
        self.__logger.debug('Done inizialization')
        self.__undoActive=True
    def suspendUndo(self):
        """
            suspend the undo for write operation
        """
        self.__undoActive=False
    def activeUndo(self):
        """
            Reactive the undo trace
        """
        self.__undoActive=True
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
        if isinstance(entity,Point):
            self.savePoint(entity)
        else:
            raise TypeError ,"Type %s not supported from pythoncad kernel"%type(entity)


    def savePoint(self,point):
        """
            save the point in to the dartabase
        """
        startTime=time.clock()
        _newId=self.__pyCadEntDb.getNewEntId()
        endTime=time.clock()-startTime
        print "Get New id in : %ss"%(str(endTime))
        _newId+=1
        _points={}
        _points['POINT']=point
        startTime=time.clock()
        _newDbEnt=PyCadEnt('POINT',_points,self.getActiveStyle(),_newId)
        endTime=time.clock()-startTime
        print "Create PyCadEnt in : %ss"%(str(endTime))
        startTime=time.clock()
        self.__pyCadEntDb.saveEntity(_newDbEnt)
        endTime=time.clock()-startTime
        print "Save PyCadEnt in : %ss"%(str(endTime))
        if self.__undoActive:
            startTime=time.clock()
            self.__pyCadUndoDb.getNextUndo(_newId)
            endTime=time.clock()-startTime
            print "getNextUndo  in : %ss"%(str(endTime))

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
    #kr.suspendUndo()
    for i in range(nEnt):
        basePoint=Point(10,i)
        kr.saveEntity(basePoint)
    endTime=time.clock()-startTime
    print "Create n: %s entity in : %ss"%(str(nEnt ),str(endTime))


# GGR test()
