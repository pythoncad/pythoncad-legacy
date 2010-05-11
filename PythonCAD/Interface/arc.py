
import math
from PyQt4 import QtCore, QtGui

class Arc(QtGui.QGraphicsItem):
    
    def __init__(self, entity):
        super(Arc, self).__init__()
        pt_begin = None
        pt_end = None
        # get the geometry
        geometry = entity.getConstructionElements()
        # get the begin and endpoint from the geometry
        # self.__center, self.__radius,self.__sa,self.__ea
        pCenter=geometry["ARC_0"]
        radius=geometry["ARC_1"]
        startAngle=geometry["ARC_2"]
        spanAngle=geometry["ARC_3"]
        self.xc,self.yc=pCenter.getCoords()
        self.yc=(-1.0*self.yc)- radius
        self.xc=self.xc-radius
        self.h=radius*2
        # By default, the span angle is 5760 (360 * 16, a full circle).
        # From pythoncad the angle are in radiant ..
        startAngle=(startAngle*180/math.pi)*16
        spanAngle=(spanAngle*180/math.pi)*16
        if spanAngle==startAngle:
            spanAngle=5760
        else:
           spanAngle=spanAngle
        self.startAngle=startAngle
        self.spanAngle=spanAngle
        return
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return QtCore.QRectF(self.xc,self.yc ,self.h ,self.h )
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        # set pen accoording to layer
        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(255, 0, 0)))
        #Create Arc/Circle
        painter.drawArc(self.xc,self.yc ,self.h ,self.h ,self.startAngle,  self.spanAngle)

    
    
    
    
    
    
    
    
  
