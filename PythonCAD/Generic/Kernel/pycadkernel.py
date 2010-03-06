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

from pycaddbexception   import *
from pycadundodb        import PyCadUndoDb
from pycadentdb         import PyCadEntDb
from pycadent           import PyCadEnt
from pycadbasedb        import PyCadBaseDb
from pycadrelation      import PyCadRelDb
from pycadsettings      import PyCadSettings

from Entity.point       import Point
from Entity.segment     import Segment
from Entity.pycadstyle  import PyCadStyle
from Entity.layer       import Layer

LEVELS = {'PyCad_Debug': logging.DEBUG,
          'PyCad_Info': logging.INFO,
          'PyCad_Warning': logging.WARNING,
          'PyCad_Error': logging.ERROR,
          'PyCad_Critical': logging.CRITICAL}

SUPPORTED_ENTITYS=(Point,Segment,PyCadStyle,Layer,PyCadSettings, PyCadEnt)

#set the debug level
level = LEVELS.get('PyCad_Debug', logging.NOTSET)
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
        self.__pyCadRelDb=PyCadRelDb(self.getConnection())
        # set the events
        self.__logger.debug('set events')
        self.saveEntityEvent=PyCadkernelEvent()
        self.deleteEntityEvent=PyCadkernelEvent()
        self.showEnt=PyCadkernelEvent()
        self.hideEnt=PyCadkernelEvent()
        # Some inizialization parameter
        #   set the default style
        self.__logger.debug('Set Style')        
        self.__activeStyleObj=PyCadStyle(0)
        self.__bulkCommit=False
        self.__entId=self.__pyCadEntDb.getNewEntId()
        self.__bulkUndoIndex=-1     # undo index are alweys positive so we do not breke in case missing entity id
        self.__settings=self.getDbSettingsObject()
        self.__logger.debug('Search / Create Main Layer')
        def createMainLayer():
            try:
                self.__activeLayer=self.getEntLayer(self.__settings.layerName)
            except EntityMissing:
                try:
                    self.__activeLayer=self.getEntLayer("ROOT")
                except EntityMissing:                
                    _settingsObjs=Layer("ROOT",None,self.__activeStyleObj.getId())
                    self.__activeLayer=self.saveEntity(_settingsObjs)
                    self.__settings.layerName="ROOT"
                    
        createMainLayer()
        self.__logger.debug('Done inizialization')

    def getLayerChild(self,layerName):
        """
            get all the entity of a layer 
        """            
        self.__logger.debug('getLayerChild')        
        _layerId=self.getEntLayer(layerName).getId()
        _childIds=self.__pyCadRelDb.getChildrenIds(_layerId)
        return _childIds

    def getLayer(self,layerName):
        """
            get the layer object from the layerName
            if not exsist create it
        """
        self.__logger.debug('getLayer')
        pyCadEntLayer=self.getEntLayer(layerName)
        _layersEnts=pyCadEntLayer.getConstructionElements()
        for key in _layersEnts:
            if _layersEnts[key].name==self.__settings.layerName:
                return _layersEnts[key]
        else:
            raise EntityMissing,"Layer %s not in the db"%str(layerName)                  

    def getEntLayer(self,layerName):
        """
            get the pycadent of type layer
        """
        self.__logger.debug('getEntLayer')
        _layersEnts=self.getEntityFromType('LAYER')
        for layersEnt in _layersEnts:
            unpickleLayers=layersEnt.getConstructionElements()
            for key in unpickleLayers:
                if unpickleLayers[key].name==self.__settings.layerName:
                    return layersEnt
            else:
                raise EntityMissing,"Layer name %s missing"%str(layerName)
        else:
            raise EntityMissing,"Layer name %s missing"%str(layerName)
        
    def getDbSettingsObject(self):
        """
            get the pythoncad settings object
        """
        self.__logger.debug('getDbSettingsObject')
        _settingsObjs=self.getEntityFromType('SETTINGS')
        if len(_settingsObjs)<=0:
            _settingsObjs=PyCadSettings('MAIN_SETTING')
            self.saveEntity(_settingsObjs)
        else:
            for sto in _settingsObjs:
                _setts=sto.getConstructionElements()
                for i in _setts:
                    if _setts[i].name=='MAIN_SETTING':
                        _settingsObjs=_setts[i]
                        break
        return _settingsObjs
    
    def startMassiveCreation(self):
        """
            suspend the undo for write operation
        """
        self.__logger.debug('startMassiveCreation')
        self.__bulkCommit=True
        self.__bulkUndoIndex=self.__pyCadUndoDb.getNewUndo()

    def stopMassiveCreation(self):
        """
            Reactive the undo trace
        """
        self.__logger.debug('stopMassiveCreation')
        self.__bulkCommit=False
        self.__bulkUndoIndex=-1

    def getEntity(self,entId):
        """
            get the entity from a given id
        """
        self.__logger.debug('getEntity')
        return self.__pyCadEntDb.getEntity(entId)
    
    def getEntityFromType(self,entityType):
        """
            get all the entity from a specifie type
        """
        self.__logger.debug('getEntityFromType')
        return self.__pyCadEntDb.getEntityFromType(entityType)
    
    def saveEntity(self,entity):
        """
            save the entity into the database
        """
        self.__logger.debug('saveEntity') 
        if not isinstance(entity,SUPPORTED_ENTITYS):
            msg="SaveEntity : Type %s not supported from pythoncad kernel"%type(entity)
            self.__logger.warning(msg)
            raise TypeError ,msg
        try:
            _obj=None
            self.__pyCadUndoDb.suspendCommit()
            self.__pyCadEntDb.suspendCommit()
            self.__pyCadRelDb.suspendCommit()
            if isinstance(entity,Point):
                _obj=self.savePoint(entity)
            if isinstance(entity,Segment):
                _obj=self.saveSegment(entity)
            if isinstance(entity,PyCadSettings):
                _obj=self.saveSettings(entity)
            if isinstance(entity,Layer):
                _obj=self.saveLayer(entity)
            if isinstance(entity,PyCadEnt):
                _obj=self.savePyCadEnt(entity)
            if not self.__bulkCommit:
                self.__pyCadUndoDb.reactiveCommit()
                self.__pyCadEntDb.reactiveCommit()
                self.__pyCadRelDb.reactiveCommit()
                self.performCommit()
            return _obj
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def savePoint(self,point):
        """
            save the point in to the db
        """
        self.__logger.debug('savePoint')
        self.__entId+=1
        _points={}
        _points['POINT']=point
        _obj=self.saveDbEnt('POINT',_points)
        self.__pyCadRelDb.saveRelation(self.__activeLayer,_obj)
        return _obj
        
    def saveSegment(self,segment):
        
        """
            seve the segment into the db
        """
        self.__logger.debug('saveSegment')
        self.__entId+=1
        _points={}
        p1,p2=segment.getEndpoints()
        _points['POINT_1']=p1
        _points['POINT_2']=p2
        _obj=self.saveDbEnt('SEGMENT',_points)
        self.__pyCadRelDb.saveRelation(self.__activeLayer,_obj)
        return _obj
    
    def saveSettings(self,settingsObj):
        """
            save the settings object
        """
        self.__logger.debug('saveSettings')
        self.__entId+=1
        _points={}
        _points['SETTINGS']=settingsObj
        return self.saveDbEnt('SETTINGS',_points)
    
    def saveLayer(self,layerObj):
        """
            save the layer object
        """
        self.__logger.debug('saveLayer')
        self.__entId+=1
        _points={}
        _points['LAYER']=layerObj
        return self.saveDbEnt('LAYER',_points)            

    def savePyCadEnt(self, pyCadEnt):
        """
            save the entity in the database 
            if this entity have an id mark pycad_visible = 0
            and then save the entity
        """
        #this is wrong 
        """
        todo: I do not need hide the entity ..
        i jast need to create a new record with the updatable value
        """
        #self.__pyCadEntDb.hideAllEntityIstance(pyCadEnt.getId(), 0)
        self.saveDbEnt(pyCadEnt=pyCadEnt)
    
    def saveDbEnt(self,entType=None,points=None, pyCadEnt=None):
        """
            save the DbEnt to db
        """
        self.__logger.debug('saveDbEnt')
        if pyCadEnt==None:
            _newDbEnt=PyCadEnt(entType,points,self.getActiveStyle(),self.__entId)
        else:
            _newDbEnt=pyCadEnt          
        if self.__bulkUndoIndex>=0:
            self.__pyCadEntDb.saveEntity(_newDbEnt,self.__bulkUndoIndex)
        else:
            self.__pyCadEntDb.saveEntity(_newDbEnt,self.__pyCadUndoDb.getNewUndo())
        self.saveEntityEvent(self,_newDbEnt)
        self.showEnt(self,_newDbEnt)
        return _newDbEnt
        
    def getActiveStyle(self):
        """
            Get the current style
        """
        self.__logger.debug('getActiveStyle')
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
        self.__logger.debug('getStyle')
        #todo get the style object of the give id
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
        self.__logger.debug('unDo')
        try:
            self.__pyCadEntDb.markUndoVisibility(self.__pyCadUndoDb.getActiveUndoId(),0)
            _newUndo=self.__pyCadUndoDb.dbUndo()
            self.__pyCadEntDb.performCommit()
        except UndoDb:
            raise
        
        
    def reDo(self):
        """
            perform a redo operation
        """
        self.__logger.debug('reDo')
        try:
            _activeRedo=self.__pyCadUndoDb.dbRedo()
            self.__pyCadEntDb.markUndoVisibility(_activeRedo, 1)
            self.__pyCadEntDb.performCommit()
        except UndoDb:
            raise
        
    def clearUnDoHistory(self):
        """
            perform a clear history operation
        """
        self.__logger.debug('clearUnDoHistory')
        #:TODO
        
        #self.__pyCadUndoDb.clearUndoTable()
        #compact all the entity 
        #self.__pyCadEntDb.compactByUndo()
        

    def deleteEntity(self,entityId):
        """
            Delete the entity from the database
        """
        self.__logger.debug('deleteEntity')
        entitys=self.__pyCadEntDb.getEntityEntityId(entityId)
        #self.
        pass
        # ToDo this will produce some plroblem need to fix it ..
        # the save entity will create a new record in the db ..
        # so it's wrong  ....
        # find a another way
        # May be we need to provide an update method..
        for ent in entitys:
            ent.state='DELETE'
            self.saveEntity(ent)
        
        # Fire event after all the operatoin are ok
        #self.deleteEntityEvent(entity)
        #self.hideEnt(entity)
        
        


class PyCadkernelEvent(object):
    """
        this class fire the envent from the python kernel
    """
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
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


"""
TODO:
    IMPROVE COMMIT SySTEM ...
    
"""

