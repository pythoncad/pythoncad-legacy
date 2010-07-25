
from Interface.Entity.base import *

class Segment(BaseEntity):
    
    def __init__(self, entity):
        super(Segment, self).__init__(entity)
        p1, p2=self.geoItem.getEndpoints()
        self.x, self.y=p1.getCoords()
        self.x1, self.y1=p2.getCoords()
        self.y=self.y*-1.0
        self.y1=self.y1*-1.0
        #self.snapItem=[QtCore.QPointF(self.x,self.y), QtCore.QPointF(self.x1,self.y1 )]
        return
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        x=min(self.x, self.x1)
        y=min(self.y, self.y1)
        deltax=abs(self.x-self.x1)
        deltay=abs(self.y-self.y1)
        return QtCore.QRectF(x,y ,deltax,deltay)

    def drawShape(self, painterPath):    
        """
            overloading of the shape method 
        """
        painterPath.moveTo(self.x, self.y)
        painterPath.lineTo(self.x1, self.y1)
        
    def drawGeometry(self, painter, option, widget):
        #Create Segment
        p1=QtCore.QPointF(self.x, self.y)
        p2=QtCore.QPointF(self.x1, self.y1)
        painter.drawLine(p1,p2)
        #painter.drawRect(self.boundingRect()) #Used for debugging porpouse
