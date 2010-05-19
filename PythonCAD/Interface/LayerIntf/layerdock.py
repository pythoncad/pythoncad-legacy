

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui



class LayerDock(QtGui.QDockWidget):
    '''
    A dockable window containing a layer list object.
    The layer list contains all visible layers.
    '''
    
    def __init__(self, parent):
        '''
        Creates an edit line in which commands or expressions are evaluated.
        Evaluation of expressions is done by the FunctionHandler object.
        '''
        super(LayerDock, self).__init__('Layers', parent)
        # only dock at the bottom or top
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.__layer_ctrl = QtGui.QListWidget(self, itemDoubleClicked=self._itemActivated, itemActivated=self._itemActivated, itemSelectionChanged=self._itemSelectionChanged)
        self.setWidget(self.__layer_ctrl)
        # layer tree from the kernel
        self.__layer_tree = None


    #-------- properties -----------#
    
    def _getLayerTree(self):
        return self.__layer_tree
    
    def _setLayerTree(self, layer_tree):
        self.__layer_tree = layer_tree  
    
    LayerTree = property(_getLayerTree, _setLayerTree, None, 'get, set the layer tree object')
    
    
    #-------- properties -----------#


    def _itemActivated(self, item):
        '''
        Make the selected layer in the list the active layer
        '''
        
        return
    
    
    def _itemSelectionChanged(self, item):
        '''
        The user selects an layer from the list
        '''
        
        return
    
    
    def addLayer(self, layer):
        '''
        Add a new layer to the drawing
        '''
        
        return
    
    
