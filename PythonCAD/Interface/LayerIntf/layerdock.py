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
# Command List
#

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
    
from PyQt4  import QtCore, QtGui

from Interface.pycadapp                         import PyCadApp
from Interface.LayerIntf.layertreeobject        import LayerView

class LayerDock(QtGui.QDockWidget):
    
    def __init__(self, parent, document, model):
        '''
        Creates an edit line in which commands or expressions are evaluated.
        Evaluation of expressions is done by the FunctionHandler object.
        '''
        super(LayerDock, self).__init__('Layers', parent)
        # only dock at the left or right
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        #self.__layer_ctrl = QtGui.QTreeWidget(self, itemDoubleClicked=self._itemActivated, itemActivated=self._itemActivated, itemSelectionChanged=self._itemSelectionChanged)
        #self.setWidget(self.__layer_ctrl)
        self._layerModel=LayerView(self, document, model)
        self.setWidget(self._layerModel)
  
    def ShowAllLayers(self):
        '''
            Show all layers from the kernel in the control
        '''
        if self._layerTreeObject:
            self._populateLayerCtrl(self.__layer_ctrl.invisibleRootItem(), layer_tree)
        return
        
    def RefreshStructure(self):
        '''
            refresh the tree view
        '''
        self._layerModel.updateView(None)
