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
# This  module all the interface to store the layer
#
#TODO : REPAIR THE LOGGER FOR THIS CLASS

from Kernel.layer               import Layer
from Kernel.exception           import *
from Kernel.initsetting         import MAIN_LAYER
from Kernel.pycadevent          import PyCadEvent

class LayerTree(object):
    """
        this class represents the layer tree structure
    """
    def __init__(self,kernel):
        self.__kr=kernel
        try:
            self.__mainLayer=self.getEntLayerDb(MAIN_LAYER)
        except EntityMissing:
            mainLayer=Layer(MAIN_LAYER)
            self.__mainLayer=self.__kr.saveEntity(mainLayer)
        except:
            raise StructuralError, "Unable to inizialize LayerTree"
        self.__activeLayer=self.__mainLayer
        self.setCurrentEvent=PyCadEvent()
        self.deleteEvent=PyCadEvent()
        self.insertEvent=PyCadEvent()
        self.update=PyCadEvent()
        
    def setActiveLayer(self, layerId):
        """
            set the active layer
        """
        activeLayer=self.__kr.getEntity(layerId)
        if activeLayer:
            self.__activeLayer=activeLayer
            self.setCurrentEvent(activeLayer)
        else:
            raise EntityMissing, "Unable to find the layer %s"%str(layerName)

    def getActiveLater(self):
        """
            get the active layer
        """
        return self.__activeLayer

    def insert(self, layer, parentLayer):
        """
            Insert a new object in the class and set it as active
        """
        parentEntDb=self.__kr.getEntity(parentLayer.getId())
        if not parentEntDb:
            raise  EntityMissing, "Unable to find the root layer %s id %s "%(str(parentLayer), str(parentLayer.getId()))
        childEndDb=self.__kr.getEntity(layer.getId())
        if not childEndDb:
            childEndDb=self.__kr.saveEntity(layer)
        if not self.__kr.getRelatioObject().relationExsist(parentEntDb.getId(),childEndDb.getId() ):
            self.__kr.getRelatioObject().saveRelation(parentEntDb, childEndDb)
        self.__activeLayer=childEndDb
        self.insertEvent(childEndDb) #Fire Event
        
    def _getLayerConstructionElement(self, pyCadEnt):
        """
            Retrive the ConstructionElement in the pyCadEnt
        """
        unpickleLayers=pyCadEnt.getConstructionElements()
        for key in unpickleLayers:
            return unpickleLayers[key]
        return None

    def getLayerChildrenLayer(self,layer):
        """
            get the layer children
        """
        return self.__kr.getAllChildrenType(layer, 'LAYER')

    #************************************************************************
    #*************************layer managment********************************
    #************************************************************************
    def getLayerChildIds(self,layer):
        """
            get all the child id of a layer
        """
        #manage in a better way the logger  self.__kr.__logger.debug('getLayerChild')
        _layerId=self.__kr.getEntLayerDb(layerName).getId()
        _childIds=self.__kr.__pyCadRelDb.getChildrenIds(_layerId)
        return _childIds

    def getLayerChildren(self,layer,entityType=None):
        """
            get all dbEnt from layer of type entityType
        """
        _children=self.__kr.getAllChildrenType(layer,entityType)
        return _children

    def getEntLayerDb(self,layerName):
        """
            get the pycadent  layer by giving a name
        """
        #TODO: manage logger self.__logger.debug('getEntLayerDb')
        _layersEnts=self.__kr.getEntityFromType('LAYER')
        #TODO: Optimaze this loop with the build in type [...] if possible
        for layersEnt in _layersEnts:
            unpickleLayers=layersEnt.getConstructionElements()
            for key in unpickleLayers:
                if unpickleLayers[key].name==layerName:
                    return layersEnt
        else:
            raise EntityMissing,"Layer name %s missing"%str(layerName)

    def getLayerTree(self):
        """
            create a dictionary with all the layer nested
        """
        rootDbEnt=self.getEntLayerDb(MAIN_LAYER)
        def createNode(layer):
            childs={}
            c=self._getLayerConstructionElement(layer)
            id=layer.getId()
            layers=self.getLayerChildrenLayer(layer)
            for l in layers:
                ca=self._getLayerConstructionElement(l)
                childs[l.getId()]=(ca, createNode(l))
            return childs
        c=self._getLayerConstructionElement(rootDbEnt)
        exitDb={}
        exitDb[rootDbEnt.getId()]=(c,createNode(rootDbEnt) )
        return exitDb

    def getParentLayer(self,layer):
        """
            get the parent layer
            ToDo: to be tested
        """
        return self.__kr.getRelatioObject().getParentEnt(layer)

    def delete(self,layerId):
        """
            delete the current layer an all the entity releted to it
        """
        self.__kr.startMassiveCreation()
        deleteLayer=self.__kr.getEntity(layerId)
        if deleteLayer is self.__activeLayer:
            self.setActiveLayer(self.getParentLayer(deleteLayer).getId())
        #
        def recursiveDelete(layer):
            # delete all children layer
            for layer in self.getLayerChildrenLayer(deleteLayer):
                recursiveDelete(layer)
            # delete all the children entity
            self.deleteLayerEntity(layer)
            # finally delete the layer
            layerId=layer.getId()
            self.__kr.deleteEntity(layerId)
            self.deleteEvent(layerId) # Fire Event
        recursiveDelete(deleteLayer)    
        self.__kr.stopMassiveCreation()
        
    def deleteLayerEntity(self, layer):
        """
            delete all layer entity
        """
        for ent in self.getLayerChildren(layer):
                self.__kr.deleteEntity(ent.getId())
                
    def rename(self, layerId, newName):
        """
            rename the layer
        """
        layer=self.__kr.getEntity(layerId)
        self._rename(layer, newName)
        self.update(layerId) # fire update event
        
    def _rename(self, layer, newName):
        """
            rename the layer internal use
        """
        layer.getConstructionElements()['LAYER'].name=newName
        self.__kr.saveEntity(layer)
        self.update(layer)
        
    def _Hide(self, layer, hide=True):
        """
            inner function for hiding the layer
        """
        # Hide/Show all the children entity
        self.hideLayerEntity(layer, hide)
        # Hide and update the layer object    
        layer.getConstructionElements()['LAYER'].Visible=not hide
        self.__kr.saveEntity(layer)
        self.update(layer)
        
    def isMainLayer(self, layer):
        """
            check if the layer is the main layer
        """
        if layer.getConstructionElements()['LAYER'].name==MAIN_LAYER:
            return True
        return False
        
    def Hide(self, layerId, hide=True):
        self.__kr.startMassiveCreation()
        topLayer=self.__kr.getEntity(layerId)  
        if self.isMainLayer(topLayer):
            raise PythonCadWarning("Unable to hide/show the main Layer")   
        if topLayer is self.__activeLayer:
            self.setActiveLayer(self.getParentLayer(topLayer).getId())
        #
        def recursiveHide(layer):
            self._Hide(layer, hide)
            # hide/show all children layer
            for layer in self.getLayerChildrenLayer(layer):
                recursiveHide(layer)
           
        recursiveHide(topLayer)    
        self.__kr.stopMassiveCreation()
    
    def hideLayerEntity(self, layer, hide=True):    
        """
            hide all the entity of the layer
        """
        if hide:
            for ent in self.getLayerChildren(layer):
                self.__kr.hideEntity(entity=ent)
        else:
            for ent in self.getLayerChildren(layer):
                self.__kr.unHideEntity(entity=ent)
