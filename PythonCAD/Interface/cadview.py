
import math
from PyQt4 import QtCore, QtGui
from Kernel.pycadevent              import PyCadEvent

class CadView(QtGui.QGraphicsView):   
    def __init__(self, parent=None):
        super(CadView, self).__init__(parent)
        self.pyCadViewPressEvent=PyCadEvent()
        self.scaleFactor=1
                
    def __init__(self, scene, parent=None):
        super(CadView, self).__init__(scene, parent)
        self.pyCadViewPressEvent=PyCadEvent()
        self.scaleFactor=1
        
    def sizeHint(self):
        return QtCore.QSize(800,600)
    
    def wheelEvent(self, event):
        self.scaleFactor=math.pow(2.0, -event.delta() / 240.0)
        self.scaleView(self.scaleFactor)
    
    def mousePressEvent(self, event):
        qtItem=self.itemAt(event.pos())
        pyCadEvent=((event.x(), event.y()*-1.0), qtItem)
        self.pyCadViewPressEvent(self, pyCadEvent)
        
        
    def scaleView(self, factor):
##        factor = self.matrix().scale(factor, factor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
##
##        if factor < 0.07 or factor > 100:
##            return

        self.scale(factor, factor)
        
        
