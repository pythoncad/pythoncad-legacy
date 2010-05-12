

from PyQt4 import QtCore, QtGui

class Text(QtGui.QGraphicsTextItem):
    
    def __init__(self, entity):
        super(Text, self).__init__()
        pt_begin = None
        pt_end = None
        # get the geometry
        geometry = entity.getConstructionElements()
        keys=geometry.keys()
        #text,geometry[keys[2]] 
        #angle,geometry[keys[1]] 
        #location,geometry[keys[0]]
        #pointPosition,geometry[keys[3]]
        self.setPlainText(geometry[keys[2]] )#text
        x, y=geometry[keys[0]].getCoords() #location
        self.setPos(x, -1.0*y)
       
        # set pen accoording to layer
        #self.setPen(QtGui.QPen(QtGui.QColor.fromRgb(255, 0, 0)))
        return
    
