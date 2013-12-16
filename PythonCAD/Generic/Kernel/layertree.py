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
from Kernel.pycadevent          import PyCadEvent

class LayerTable(object):
    """
    Class used to interface with the database/save file
    """

    def __init__(self, kernel):
        self.__kr = kernel

        # TODO: Check why a layer is created without a document open
        # Add a default layer if none exists
        layer_count = self.getLayerCount()
        if not layer_count:
            new_layer = self.__kr.saveEntity(Layer('Default'))
            self.__activeLayer = new_layer
        else:
            # Set active layer to first visible layer it finds
            # TODO: Save active layer between sessions
            self.__activeLayer = self.getVisibleLayer()

        self.setCurrentEvent = PyCadEvent()
        self.deleteEvent = PyCadEvent()
        self.insertEvent = PyCadEvent()
        self.updateEvent = PyCadEvent()

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

    def getActiveLayer(self):
        """
            get the active layer
        """
        return self.__activeLayer

    def insert(self, layer):
        """
            Insert a new object in the class and set it as active
        """
        childEndDb = self.__kr.getEntity(layer.getId())
        if not childEndDb:
            childEndDb = self.__kr.saveEntity(layer)
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
            ### Unneeded ###
        """
        return self.__kr.getAllChildrenType(layer, 'LAYER')

    #************************************************************************
    #*************************layer managment********************************
    #************************************************************************
    def getLayerChildIds(self,layer):
        """
            get all the child id of a layer
            ### Unneeded ###
        """
        #manage in a better way the logger  self.__kr.__logger.debug('getLayerChild')
        _layerId=self.__kr.getEntLayerDb(layerName).getId()
        _childIds=self.__kr.__pyCadRelDb.getChildrenIds(_layerId)
        return _childIds

    def getLayerChildren(self,layer,entityType=None):
        """
            get all dbEnt from layer of type entityType
            ### Unneeded ###
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

    def getVisibleLayer(self, ignore = []):
        # TODO: Cleanup as in getEntLayerDb
        layer_entities = self.__kr.getEntityFromType('LAYER')
        for layer_entity in layer_entities:
            if layer_entity.getId() not in ignore:
                unpickled_layer = layer_entity.getConstructionElements()
                for layer in unpickled_layer.itervalues():
                    if layer.visible:
                        # TODO: Refactor, indent pretty deep
                        return layer_entity
        return False

    def getLayerCount(self):
        layers = self.__kr.getEntityFromType('LAYER')
        return len(layers)

    def getLayers(self):
        """
        Returns a dictionary of all the layers
        """
        layers = self.__kr.getEntityFromType('LAYER')
        layer_dict = {}
        for layer in layers:
            c = self._getLayerConstructionElement(layer)
            layer_dict[layer.getId()] = c
        return layer_dict

    def getLayerTree(self):
        """
            create a dictionary with all the layer nested
        """
        rootDbEnt=self.getEntLayerDb(MAIN_LAYER)
        def createNode(layer):
            childs={}
            c=self._getLayerConstructionElement(layer)
            layers=self.getLayerChildrenLayer(layer)
            for l in layers:
                ca=self._getLayerConstructionElement(l)
                childs[l.getId()]=(ca, createNode(l))
            return childs
        c=self._getLayerConstructionElement(rootDbEnt)
        exitDb={}
        exitDb[rootDbEnt.getId()]=(c,createNode(rootDbEnt) )
        return exitDb

    def getLayerdbTree(self):
        # TODO: Update DXF export/import
        """
            create a dictionary with all the layer nested as db entity
        """
        rootDbEnt=self.getEntLayerDb(MAIN_LAYER)
        def createNode(layer):
            childs={}
            layers=self.getLayerChildrenLayer(layer)
            for l in layers:
                childs[l.getId()]=(l, createNode(l))
            return childs
        exitDb={}
        exitDb[rootDbEnt.getId()]=(rootDbEnt,createNode(rootDbEnt) )
        return exitDb

    def getParentLayer(self,layer):
        """
            get the parent layer
            ToDo: to be tested
        """
        return self.__kr.getRelatioObject().getParentEnt(layer)

    def delete(self, layerId):
        """
            delete the current layer and all the entity related to it
        """
        deleteLayer = self.__kr.getEntity(layerId)

        # If layer is currently active, find the first visible layer and set it active
        if layerId is self.__activeLayer.getId():
            visible_layer = self.getVisibleLayer(ignore = [layerId, ])
            if not visible_layer:
                raise PythonCadWarning("Unable to delete the last visible layer")
                return False
            self.setActiveLayer(visible_layer.getId())

        # Delete all entities (SEGMENTS, TEXT, etc.)
        self.deleteLayerEntity(deleteLayer)

        # Delete the layer
        self.__kr.deleteEntity(layerId)
        self.deleteEvent(layerId)

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
        self.updateEvent(layerId) # fire update event

    def _rename(self, layer, newName):
        """
            rename the layer internal use
        """
        layer.getConstructionElements()['LAYER'].name=newName
        print layer.getConstructionElements()['LAYER'].__dict__
        self.__kr.saveEntity(layer)
        self.updateEvent(layer)

    def _show(self, layer):
        # Show all the children entity
        for entity in self.getLayerChildren(layer):
            self.__kr.unHideEntity(entity = entity)
        # Show and update the layer object
        layer.getConstructionElements()['LAYER'].visible = True
        self.__kr.saveEntity(layer)
        self.updateEvent(layer)

    def show(self, layer_id):
        layer = self.__kr.getEntity(layer_id)
        self._show(layer)

    def _hide(self, layer):
        # Hide all the children entity
        for entity in self.getLayerChildren(layer):
            self.__kr.hideEntity(entity = entity)

        # Hide and update the layer object
        layer.getConstructionElements()['LAYER'].visible = False
        self.__kr.saveEntity(layer)

        self.updateEvent(layer)

    def hide(self, layerId):
        # Prevent trying to hide the only layer 
        if self.getLayerCount() <= 1:
            raise PythonCadWarning("Unable to hide the only Layer")
            return False

        layer = self.__kr.getEntity(layerId)

        # If layer is currently active, find the first visible layer and set it active
        if layerId is self.__activeLayer.getId():
            visible_layer = self.getVisibleLayer(ignore = [layerId, ])
            if not visible_layer:
                raise PythonCadWarning("Unable to hide the last visible layer")
                return False
            self.setActiveLayer(visible_layer.getId())

        self._hide(layer)
