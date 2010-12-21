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

from PyQt4                      import QtCore, QtGui

from Kernel.initsetting                 import MAIN_LAYER
from Kernel.layer                       import Layer
class LayerItem(QtGui.QTreeWidgetItem):
    """
        Single item
    """
    def __init__(self, kernelItem,type=0):
        super(LayerItem, self).__init__(type)
        self._kernelItem=kernelItem
        self.setText(0, self.name)
    @property
    def name(self):
        """
            get the layer name
        """
        return self._kernelItem.name
        
class LayerTreeObject(QtGui.QTreeWidget):
    """
        PythonCAD Layer tree Structure
    """
    def __init__(self, parent, document):
        super(LayerTreeObject, self).__init__(parent)
        self._document=document
        self.setColumnCount(1)
        self.setHeaderLabel("Layer Name")
        self.populateStructure()
    
    def populateStructure(self):
        """
            populate the tree view structure
        """
        self.clear()
        layerTreeStructure=self._document.getTreeLayer.getLayerTree()
        #tree[id]=(c, childs)
        def populateChild(layers, parentItem):
            for key in layers:
                c, childs=layers[key]
                parent=LayerItem(c)
                self.expandItem(parent)
                if parentItem==None:
                    self.addTopLevelItem(parent)
                else:
                    parentItem.addChild(parent)
                if childs!=None:
                    populateChild(childs,parent )
        populateChild(layerTreeStructure, None)

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
        propertyAction=QtGui.QAction("Property", self, triggered=self._property)
        #
        contexMenu.addAction(addAction)
        contexMenu.addAction(removeAction)
        contexMenu.addAction(hideAction)
        contexMenu.addAction(showAction)
        contexMenu.addAction(propertyAction)
        #
        contexMenu.exec_(event.globalPos())
        del(contexMenu)
        
    def _addChild(self):
        """
            Add a child layer
        """
        # SHOW POP UP MENU FOR THE LAYER THE BEST IS IF WE PROMPT THE PROPERTY FORM
        layerName="Test Layer"
        parentLayer=self._document.getTreeLayer.getActiveLater()
        newLayer=self._document.saveEntity(Layer(layerName))
        self._document.getTreeLayer.insert(newLayer, parentLayer)
        self.populateStructure()
        pass
    def _remove(self):
        """
            Remove the selected layer
        """
        pass
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
    def _property(self):
        """
            Show the layer property dialog
        """
        pass
        
        
        
        
        
        
        
        
        
        
