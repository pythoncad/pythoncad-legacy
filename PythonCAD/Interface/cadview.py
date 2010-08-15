
import math
from PyQt4 import QtCore, QtGui

from Interface.Entity.base import *

class CadView(QtGui.QGraphicsView):   
    def __init__(self, scene, parent=None):
        super(CadView, self).__init__(scene, parent)
        self.scene=scene
        self.scaleFactor=1
        self.controlPress=False
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse) 

    def sizeHint(self):
        return QtCore.QSize(3000,3000)
    
    def wheelEvent(self, event):
        self.scaleFactor=math.pow(2.0,-event.delta() / 240.0)
        self.scaleView(self.scaleFactor)
    
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Control:
            self.controlPress=True
            self.scene.isInPan=True
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        super(CadView, self).keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        self.controlPress=False
        self.scene.isInPan=False
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        super(CadView, self).keyReleaseEvent(event)
    
    def fit(self):
        """
            fit all the item in the view
        """
        boundingRectangle=[item.boundingRect() for item in self.scene.items() if isinstance(item, BaseEntity)]
        qRect=None
        for bound in boundingRectangle:
            if not qRect:
                qRect=bound
            else:
                qRect=qRect.unite(bound)
        if qRect:
            self.zoomWindows(qRect) 
            
    def centerOnSelection(self):        
        """
            center the view on selected item
        """
        #TODO: if the item is in the border the centerOn will not work propely
        #more info at :http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qgraphicsview.html#ViewportAnchor-enum
        for item in self.scene.selectedItems():
            self.centerOn(item)
            return 
            
    def zoomWindows(self, qRect):
        """
            perform a windows zoom
        """
        zb=self.scaleFactor
        qRect.setX(qRect.x()-zb)
        qRect.setY(qRect.y()-zb)
        qRect.setWidth(qRect.width()+zb)
        qRect.setHeight(qRect.height()+zb)
        self.fitInView(qRect,1) #KeepAspectRatioByExpanding
        
    def scaleView(self, factor):
        self.scale(factor, factor)
