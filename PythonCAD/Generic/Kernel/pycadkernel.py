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
#**************************************************System Import
import os
import sys
import cPickle as pickle
import logging
import time
#***************************************************Kernel Import
from pycadextformat import *
from Generic.Kernel.pycaddbexception        import *
from Generic.Kernel.pycadundodb             import PyCadUndoDb
from Generic.Kernel.pycadentdb              import PyCadEntDb
from Generic.Kernel.pycadent                import PyCadEnt
from Generic.Kernel.pycadbasedb             import PyCadBaseDb
from Generic.Kernel.pycadrelation           import PyCadRelDb
from Generic.Kernel.pycadsettings           import PyCadSettings
from Generic.Kernel.pycadlayertree          import PyCadLayerTree
from Generic.Kernel.pycadlayer              import Layer
#****************************************************Entity Import
from Generic.Kernel.Entity.point        import Point
from Generic.Kernel.Entity.segment      import Segment
from Generic.Kernel.Entity.arc          import Arc
from Generic.Kernel.Entity.pycadstyle   import PyCadStyle

# spatial index
from Generic.Kernel.pycadindex import PyCadIndex


LEVELS = {'PyCad_Debug': logging.DEBUG,
          'PyCad_Info': logging.INFO,
          'PyCad_Warning': logging.WARNING,
          'PyCad_Error': logging.ERROR,
          'PyCad_Critical': logging.CRITICAL}

DRAWIN_ENTITY={ Point:'POINT',
                Segment:'SEGMENT',
                Arc:'ARC'}
KERNEL_ENTITY=(PyCadStyle,PyCadEnt,PyCadSettings,Layer)

SUPPORTED_ENTITYS=KERNEL_ENTITY+tuple(DRAWIN_ENTITY.keys())

#set the debug level
level = LEVELS.get('PyCad_Warning', logging.NOTSET)
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
        # set the events
        self.__logger.debug('set events')
        self.saveEntityEvent=PyCadkernelEvent()
        self.deleteEntityEvent=PyCadkernelEvent()
        self.showEnt=PyCadkernelEvent()
        self.hideEnt=PyCadkernelEvent()
        self.handledError=PyCadkernelEvent()
        #create Connection
        self.createConnection(dbPath)
        # inizialize extentionObject
        self.__pyCadUndoDb=PyCadUndoDb(self.getConnection())
        self.__pyCadEntDb=PyCadEntDb(self.getConnection())
        self.__pyCadRelDb=PyCadRelDb(self.getConnection())
        # Some inizialization parameter
        #   set the default style
        self.__logger.debug('Set Style')
        self.__activeStyleObj=PyCadStyle(0)
        self.__bulkCommit=False
        self.__bulkUndoIndex=-1     # undo index are alweys positive so we do not breke in case missing entity id
        self.__entId=self.__pyCadEntDb.getNewEntId()
        self.__settings=self.getDbSettingsObject()
        #************************
        #Inizialize Layer structure
        #************************
        self.__logger.debug('Inizialize layer structure')
        try:
            self.__pyCadLayerTree=PyCadLayerTree(self)
        except StructuralError:
            raise StructuralError, 'Unable to create PycadLayerTree structure'

        self.__logger.debug('Done inizialization')

    def getSpIndex(self):
        """
        returns a new constructed spatial index object
        """
        try:
            index = PyCadIndex(self.getConnection())
            return index
        except:
            self.__logger.debug('Unable to create indexobject')
        return None

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
        return self.__pyCadEntDb.getEntityEntityId(entId)

    def getEntityFromType(self,entityType):
        """
            get all the entity from a specifie type
        """
        self.__logger.debug('getEntityFromType')
        return self.__pyCadEntDb.getEntityFromType(entityType)

    def getAllDrawingEntity(self):
        """
            get all drawing entity from the db
        """
        return self.__pyCadEntDb.getEntityFromTypeArray([DRAWIN_ENTITY[key] for key in DRAWIN_ENTITY.keys()])
    
    def haveDrawingEntitys(self):
        """
            check if the drawing have some data in it
        """
        return self.__pyCadEntDb.haveDrwEntitys([DRAWIN_ENTITY[key] for key in DRAWIN_ENTITY.keys()])
        
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
            #self.__pyCadUndoDb.suspendCommit()
            #self.__pyCadEntDb.suspendCommit()
            #self.__pyCadRelDb.suspendCommit()
            PyCadBaseDb.commit=False
            if isinstance(entity,tuple(DRAWIN_ENTITY.keys())):
                _obj=self.saveDrwEnt(entity)
            if isinstance(entity,PyCadSettings):
                _obj=self.saveSettings(entity)
            if isinstance(entity,Layer):
                _obj=self.saveLayer(entity)
            if isinstance(entity,PyCadEnt):
                _obj=self.savePyCadEnt(entity)
            if not self.__bulkCommit:
                #self.__pyCadUndoDb.reactiveCommit()
                #self.__pyCadEntDb.reactiveCommit()
                #self.__pyCadRelDb.reactiveCommit()
                PyCadBaseDb.commit=True
                self.performCommit()
            return _obj
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def saveDrwEnt(self,ent):
        """
            Save a PythonCad drawing entity
        """
        self.__logger.debug('saveArc')
        for t in DRAWIN_ENTITY :
            if isinstance(ent, t):
                entityType=DRAWIN_ENTITY[t]
                break
        self.__entId+=1
        _cElements={}
        i=0
        for _p in ent.getConstructionElements():
            _key='%s_%s'%(str(entityType),str(i))
            _cElements[_key]=_p
            i+=1
        _obj=self.saveDbEnt(entityType,_cElements)
        self.__pyCadRelDb.saveRelation(self.__pyCadLayerTree.getActiveLater(),_obj)
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
        self.saveDbEnt(pyCadEnt=pyCadEnt)

    def saveDbEnt(self,entType=None,points=None, pyCadEnt=None):
        """
            save the DbEnt to db
        """
        self.__logger.debug('saveDbEnt')
        if pyCadEnt==None:
            _newDbEnt=PyCadEnt(entType,points,self.__activeStyleObj.getId(),self.__entId)
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
        #ToDO: set active style
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

    def release(self):
        """
            release the current drawing
        """
        try:
            # For Best Performance
            self.startMassiveCreation()
            # Clear the undo table
            self.__pyCadUndoDb.clearUndoTable()
            # Relese all the entity
            goodEntity=self.__pyCadEntDb.getEntityFromType('ALL')
            for entity in goodEntity:
                entity.relese()
                self.saveEntity(entity)
            # Clear the old entity
            self.__pyCadEntDb.clearEnt()
            # Increse the revision index
            self.__pyCadEntDb.increaseRevisionIndex()
            # Commit all the change
            self.performCommit()
        except:
            self.__pyCadEntDb.decreseRevisionIndex()
            print "Unable to perform the release operation"
        finally:
            self.stopMassiveCreation()

    def deleteEntity(self,entityId):
        """
            Delete the entity from the database
        """
        self.__logger.debug('deleteEntity')
        entity=self.__pyCadEntDb.getEntityEntityId(entityId)
        entity.delete()
        self.saveEntity(entity)
        self.deleteEntityEvent(entity)

    def hideEntity(self, entity=None, entityId=None):
        """
            Hide an entity
        """
        self._hide(entity, entityId, 0)
        self.hideEnt(self, entity) # Event

    def unHideEntity(self, entity=None, entityId=None):
        """
            Unhide an entity
        """
        self._hide(entity, entityId, 1)
        self.showEnt(self, entity) #Event

    def _hide(self,entity=None, entityId=None,  visible=0):
        """
            make the hide/unhide of an entity
        """
        if entity is None and entityId is None:
            raise EntityMissing, "All function attribut are null"
        activeEnt=None
        if entity != None:
            activeEnt=self.__pyCadEntDb.getEntityEntityId(entity.getId())
        if activeEnt == None and entityId is not None:
            activeEnt=self.__pyCadEntDb.getEntityEntityId(entityId)
        if activeEnt.visible!=visible:
            activeEnt.visible=visible
            self.__pyCadEntDb.uptateEntity(activeEnt)

    def importExternalFormat(self, fileName):
        """
            This method allow you to import a file from an external format
        """
        try:
            extFormat=ExtFormat(self)
            extFormat.openFile(fileName)
        except DxfReport:
            self.__logger.error('DxfReport')
            _err={'object':extFormat, 'error':DxfReport}
            self.handledError(self,_err)#todo : test it not sure it works
        except DxfUnsupportedFormat:
            self.__logger.error('DxfUnsupportedFormat')
            _err={'object':extFormat, 'error':DxfUnsupportedFormat}
            self.handledError(self,_err)#todo : test it not sure it works
    def getTreeLayer(self):
        """
            retrive the layer from the tree
        """
        return self.__pyCadLayerTree

    def getAllChildrenType(self, parentObject, childrenType):
        """
            Get all the entity children from an pyCadDb object
        """
        return self.__pyCadRelDb.getAllChildrenType(parentObject, childrenType)

    def getRelatioObject(self):
        """
            getRelationObject
        """
        return self.__pyCadRelDb

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
TODO: create a layer structure

"""
