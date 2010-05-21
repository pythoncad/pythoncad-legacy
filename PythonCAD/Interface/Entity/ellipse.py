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
# qt ellipse class
#
import math
from PyQt4 import QtCore, QtGui

class Ellipse(QtGui.QGraphicsItem):
    
    def __init__(self, entity):
        super(Ellipse, self).__init__()
        pt_begin = None
        pt_end = None
        # get the geometry
        geometry = entity.getConstructionElements()
        self.style=entity.getInnerStyle()
        # Get Construction arc elements
        #self.__center, self.__major,self.__minor
        pCenter=geometry["ELLIPSE_0"]
        major=geometry["ELLIPSE_1"]
        minor=geometry["ELLIPSE_2"]
        self.ID=entity.getId()
        self.xc,self.yc=pCenter.getCoords()
       
        self.h=major/2.0
        self.w=minor/2.0
        return
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return QtCore.QRectF(self.xc,self.yc ,self.h ,self.w )
        
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        #   Set pen accoording to layer
        r, g, b=self.style.getStyleProp("entity_color") 
        painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
        #   Create Ellipse
        painter.drawEllipse(self.xc,self.yc ,self.h ,self.w)



    
    
    
    
    
    
    
    
  
