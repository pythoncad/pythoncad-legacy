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
    def __init__(self, parent, kernelTree):
        super(LayerTreeObject, self).__init__(parent)
        self._kernelTree=kernelTree
        self.setColumnCount(1)
        self.setHeaderLabel("Layer Name")
        self.populateStructure()
    
    def populateStructure(self):
        """
            populate the tree view structure
        """
        layerTreeStructure=self._kernelTree.getLayerTree()
        #tree[id]=(c, childs)
        for key in layerTreeStructure:
            c, childs=layerTreeStructure[key]
            self.addTopLevelItem(LayerItem(c))
        
        
        
        
        
        
        
        
        
        
        
        
