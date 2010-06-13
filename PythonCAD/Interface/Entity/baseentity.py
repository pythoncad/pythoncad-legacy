#
# Copyright (c) 2010 Matteo Boscolo
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
# This module provide basic class for all  the qtitems to be displayed
#
import math
from PyQt4 import QtCore, QtGui
from Kernel.initsetting import PYTHONCAD_HIGLITGT_COLOR

class BaseEntity(QtGui.QGraphicsItem):
    def __init__(self, entity):
        super(BaseEntity, self).__init__()
        self.setAcceptsHoverEvents(True)    #Fire over events
        #self.setSelected(True)              #Accept to be selected
        self.GraphicsItemFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        #self.setFlag(QtGui.QGraphicsItem.ItemClipsToShape, True)
        # get the geometry
        self.__entity=entity
        self.setToolTip(str(self.toolTipMessage))
        r, g, b=self.style.getStyleProp("entity_color")
        self.color = QtGui.QColor.fromRgb(r, g, b)
        return
    
    def setColor(self):
        r, g, b=self.style.getStyleProp("entity_color")
        self.color = QtGui.QColor.fromRgb(r, g, b)       
    
    def setHiglight(self):
        r, g, b=PYTHONCAD_HIGLITGT_COLOR
        self.color = QtGui.QColor.fromRgb(r, g, b)
        
    @property
    def entity(self):
        return self.__entity 
    @property
    def ID(self):
        return self.__entity.getId()
    @property
    def geoItem(self):
        return self.__entity.toGeometricalEntity()
    @property
    def style(self):
        return self.__entity.getInnerStyle()
    
    @property
    def toolTipMessage(self):
        toolTipMessage=self.geoItem.info
        return toolTipMessage
    
    def hoverEnterEvent(self, event):
        self.setSelected(True)
        self.setHiglight()
        self.update()
    
    def hoverLeaveEvent(self, event):
        self.setSelected(False)
        self.setColor()
        self.update()
        
    def drawGeometry(self, painter, option, widget):
        """
             this method must be inerit from qtPycadObject
        """
        pass
        
    def drawShape(self, painterPath):
        """
            overloading of the shape method 
        """
        pass
        
    def shape(self):            
        """
            overloading of the shape method 
        """
        painterStrock=QtGui.QPainterPathStroker()
        path=QtGui.QPainterPath()
        self.drawShape(path)
        path1=painterStrock.createStroke(path)
        return path1
        
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        
        painter.setPen(QtGui.QPen(self.color, 1))
        #draw geometry
        #painter.drawPath(self.shape())
        self.drawGeometry(painter,option,widget)
    
