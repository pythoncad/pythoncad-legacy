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

class Arc(QtGui.QGraphicsItem):
    """
        this class define the arcQT object 
    """
    def __init__(self, entity):
        super(Arc, self).__init__()
        # get the geometry
        geometry = entity.getConstructionElements()
        self.style=entity.getInnerStyle()
        # Get Construction arc elements
        pCenter=geometry["ARC_0"]
        radius=geometry["ARC_1"]
        startAngle=geometry["ARC_2"]
        spanAngle=geometry["ARC_3"]
        self.ID=entity.getId()
        self.xc,self.yc=pCenter.getCoords()
        self.yc=(-1.0*self.yc)- radius
        self.xc=self.xc-radius
        self.h=radius*2
        # By default, the span angle is 5760 (360 * 16, a full circle).
        # From pythoncad the angle are in radiant ..
        startAngle=(startAngle*180/math.pi)*16
        spanAngle=(spanAngle*180/math.pi)*16
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
        r, g, b=self.style.getStyleProp("entity_color") 
        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
        #Create Arc/Circle
        painter.drawArc(self.xc,self.yc ,self.h ,self.h ,self.startAngle,  self.spanAngle)

    
    
    
    
    
    
    
    
  
