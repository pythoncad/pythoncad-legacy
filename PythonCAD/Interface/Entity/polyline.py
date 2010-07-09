#
# Copyright (c) ,2010 Matteo Boscolo
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
# qt arc class
#

from Interface.Entity.base import *

class Polyline(BaseEntity):
    """
        this class define the polyline object 
    """
    def __init__(self, entity):
        super(Polyline, self).__init__(entity)
        # get the geometry
        geometry = self.entity.getConstructionElements()
        geoPoints=[geometry[k] for k in geometry]
        coordPoints=[point.getCoords() for point in geoPoints]
        
        #self.qtPoints=[QtCore.QPointF(x, y*-1.0 ) for x, y in coordPoints]
        self.qtPoints=self.getQtPointF()
        
        X=[x for x,y in coordPoints]
        max_x=max(X)
        min_x=min(X)
        Y=[y*-1.0 for x,y in coordPoints]
        max_y=max(Y)
        min_y=min(Y)
        w=abs(max_y-min_y)
        h=abs(max_x-min_x)
        self.bbox=QtCore.QRectF(min_x,min_y ,h ,w )
        return
        
    def getQtPointF(self):
        qtPoints=[]
        geoPolyline=self.geoItem
        for p in geoPolyline.points():
            x, y=p.getCoords()
            qtPointf=QtCore.QPointF(x, y*-1.0 )
            qtPoints.append(qtPointf)
        return qtPoints
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return self.bbox
        
    def drawShape(self, painterPath):    
        """
            overloading of the shape method 
        """
        painterPath.moveTo(self.qtPoints[0])
        for i in range(1,len(self.qtPoints)):
            painterPath.lineTo(self.qtPoints[i])    
    
    def drawGeometry(self, painter, option, widget):
        """
            overloading of the paint method
        """
        #Create poliline Object
        pol=QtGui.QPolygonF(self.qtPoints)
        painter.drawPolyline(pol)
        #painter.drawRect(self.boundingRect())
    
    
    
    
    
    
    
    
  
