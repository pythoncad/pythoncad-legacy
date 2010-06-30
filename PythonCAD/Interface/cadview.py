
import math
from PyQt4 import QtCore, QtGui

from Interface.Entity.baseentity import BaseEntity
class CadView(QtGui.QGraphicsView):   
              
    def __init__(self, scene, parent=None):
        super(CadView, self).__init__(scene, parent)
        self.scene=scene
        self.scaleFactor=1
        self.controlPress=False
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setResizeAnchor(QtGui.QGraphicsView.NoAnchor)
        

    def sizeHint(self):
        return QtCore.QSize(800,600)
    
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
        qRect.setX(qRect.x()-2)
        qRect.setY(qRect.y()-2)
        qRect.setWidth(qRect.width()+2)
        qRect.setHeight(qRect.height()+2)
        self.fitInView(qRect,1) #KeepAspectRatioByExpanding
        
    def scaleView(self, factor):
        self.scale(factor, factor)
