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
# This  module provide all the global variable to be used from the pythoncad Application
#
#
# This Class define a QTreeWidget implementation for showing the layer structure
#
import sys
if sys.version_info <(2, 7):
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

from PyQt4                              import QtCore, QtGui

from Kernel.initsetting                 import MAIN_LAYER
from Kernel.layer                       import Layer

class LayerItem(QtGui.QTreeWidgetItem):
    """
        Single item
    """
    def __init__(self, kernelItem,type=0, id=None, active=False):
        super(LayerItem, self).__init__(type)
        self._kernelItem=kernelItem
        self._id=id
        self.setText(0, self.name)
        self.setActive(active)
    @property
    def name(self):
        """
            get the layer name
        """
        return self._kernelItem.name
        
    @property
    def id(self):
        """
            Get the id of the layer
        """
        return self._id
        
    def setActive(self, active):
        if active:
            self.setBackgroundColor(0, QtCore.Qt.lightGray)
        else:
            self.setBackgroundColor(0, QtCore.Qt.white)

class LayerTreeObject(QtGui.QTreeWidget):
    """
        Python
        CAD Layer tree Structure
    """
    def __init__(self, parent, document):
        super(LayerTreeObject, self).__init__(parent)
        self._document=document
        self._document.getTreeLayer.setCurrentEvent=self.setCurrentEvent
        self._document.getTreeLayer.deleteEvent=self.deleteEvent
        self._document.getTreeLayer.insertEvent=self.insertEvent
        self.setColumnCount(1)
        self.setHeaderLabel("Layer Name")
        self.populateStructure()
    #
    # Manage event
    #
    def setCurrentEvent(self, treeObject, layer):
        """
            use the set current event 
        """
        self.populateStructure()
        
    def deleteEvent(self,  layerId):    
        """
            use the delete event
        """
        self.populateStructure()
        pass
        
    def insertEvent(self, treeObject, layer):
        """
            use the insert event
        """
        self.populateStructure()
        
    def populateStructure(self):
        """
            populate the tree view structure
        """
        self.clear()
        layerTreeStructure=self._document.getTreeLayer.getLayerTree()
        activeLayer=self._document.getTreeLayer.getActiveLater()
        def populateChild(layers, parentItem, activeLayerId):
            for key in layers:
                c, childs=layers[key]
                if key==activeLayerId:
                    parent=LayerItem(c, id=key, active=True)
                else:
                    parent=LayerItem(c, id=key, active=False)
                self.expandItem(parent)
                if parentItem==None:
                    self.addTopLevelItem(parent)
                else:
                    parentItem.addChild(parent)
                if childs!=None:
                    populateChild(childs,parent,activeLayerId)
        populateChild(layerTreeStructure, None, activeLayerId=activeLayer.getId())

    def contextMenuEvent(self, event):
        """
            context menu event remapped
        """
        contexMenu=QtGui.QMenu(self)
        # Create Actions
        addAction=QtGui.QAction("Add Child", self, triggered=self._addChild)
        removeAction=QtGui.QAction("Remove", self, triggered=self._remove)
        hideAction=QtGui.QAction("Hide", self, triggered=self._hide)
        showAction=QtGui.QAction("Show", self, triggered=self._show)
        setCurrentAction=QtGui.QAction("Set Current", self, triggered=self._setCurrent)
        propertyAction=QtGui.QAction("Property", self, triggered=self._property)
        #
        contexMenu.addAction(addAction)
        contexMenu.addAction(removeAction)
        contexMenu.addAction(hideAction)
        contexMenu.addAction(showAction)
        contexMenu.addAction(setCurrentAction)
        contexMenu.addAction(propertyAction)
        #
        contexMenu.exec_(event.globalPos())
        del(contexMenu)
        
    def _addChild(self):
        """
            Add a child layer
        """
        # SHOW POP UP MENU FOR THE LAYER THE BEST IS IF WE PROMPT THE PROPERTY FORM
        layerName="New Layer"
        parentLayer=self._document.getTreeLayer.getActiveLater()
        newLayer=self._document.saveEntity(Layer(layerName))
        self._document.getTreeLayer.insert(newLayer, parentLayer)
        
    def _remove(self):
        """
            Remove the selected layer
        """
        layerId=self.currentIterfaceTreeObject.id
        self._document.getTreeLayer.delete(layerId)
        
    def _hide(self):
        """
            Hide the selected layer
        """
        pass
        
    def _show(self):
        """
            Show the selected layer
        """
        pass
        
    def _setCurrent(self):
        """
            set the current layer
        """
        cito=self.currentIterfaceTreeObject
        if cito!=None:
            self._document.getTreeLayer.setActiveLayer(cito.id)
            cito.setActive(True)
      
        
    def _property(self):
        """
            Show the layer property dialog
        """
        pass
        
    @property
    def currentIterfaceTreeObject(self):
        """
            return the current interface tree Object
        """
        exitLayer=None
        for item in self.selectedItems():
            if(item.id!=None):
                exitLayer=item           
            break
        return exitLayer
        
        
        
        
        
        