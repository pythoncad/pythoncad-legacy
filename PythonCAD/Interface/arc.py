

from PyQt4 import QtCore, QtGui

class Arc(QtGui.QGraphicsEllipseItem):
    
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
        endAngle=geometry["ARC_3"]
        xc, yc=pCenter.getCoords()
        h=radius*2
        self.setRect(xc, -1.0 *yc, h, h)
        # By default, the span angle is 5760 (360 * 16, a full ellipse).
        if endAngle==startAngle:
            endAngle=5760
        else:
           endAngle=5760.0-(endAngle*16) 
        self.setSpanAngle(endAngle)
        self.setStartAngle(startAngle)
        # set pen accoording to layer
        self.setPen(QtGui.QPen(QtGui.QColor.fromRgb(255, 0, 0)))
        return
    
