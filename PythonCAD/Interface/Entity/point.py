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

import math
from PyQt4 import QtCore, QtGui

class Point(QtGui.QGraphicsItem):
    """
        this class define the arcQT object 
    """
    def __init__(self, entity):
        super(Point, self).__init__()
        # get the geometry
        geometry = entity.getConstructionElements()
        self.style=entity.getInnerStyle()
        # Get Construction arc elements
        self.xc=geometry["POINT_0"]
        self.yc=geometry["POINT_1"]
        self.yc=(-1.0*self.yc)
        return
       
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return QtCore.QRectF(self.xc-2,self.yc-2 ,4 ,4)
        
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        # set pen accoording to layer
        r, g, b=self.style.getStyleProp("entity_color") 
        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
        #Create Arc/Circle
        p=QtCore.QPoint(self.xc, self.yc)
        painter.drawRect(self.boundingRect())
        painter.drawPoint(p)

    
    
    
    
    
    
    
    
  
