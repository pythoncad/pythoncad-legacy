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
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        #Get the geometry
        self.__entity=entity
        self.setToolTip(str(self.toolTipMessage))
        r, g, b= self.style.getStyleProp("entity_color")
        self.color = QtGui.QColor.fromRgb(r, g, b)
        self.lineWith=1.0
        return
    
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
    def updateSelected(self):    
        self.setColor()
        self.update(self.boundingRect())
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            selected, spool=value.toUInt()
            self.setColor(selected==True)
            self.update(self.boundingRect())
        return QtGui.QGraphicsItem.itemChange(self, change, value)
        
    def setColor(self, forceHilight=None):
        if forceHilight==None:
            if self.isSelected() or forceHilight:
                r, g, b=PYTHONCAD_HIGLITGT_COLOR
            else:
                r, g, b=self.style.getStyleProp("entity_color")
        else:
            if forceHilight:
                r, g, b=PYTHONCAD_HIGLITGT_COLOR
            else:
                r, g, b=self.style.getStyleProp("entity_color")
        self.color = QtGui.QColor.fromRgb(r, g, b)       
    
    def setHiglight(self):
        r, g, b=PYTHONCAD_HIGLITGT_COLOR
        self.color = QtGui.QColor.fromRgb(r, g, b)
    
    def hoverEnterEvent(self, event):
        self.setHiglight()
        self.update(self.boundingRect())
        super(BaseEntity, self).hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setColor()
        self.update(self.boundingRect())
        super(BaseEntity, self).hoverLeaveEvent(event)
        
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
        painterStrock.setWidth(self.lineWith)
        path1=painterStrock.createStroke(path)
        return path1
        
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        #painter.setPen(QtGui.QPen(self.color, self.lineWith))
        painter.setPen(QtGui.QPen(self.color))
        #draw geometry
        #painter.drawPath(self.shape())
        self.drawGeometry(painter,option,widget)

    def getDistance(self, qtPointF_1, qtPointF_2):
        """
            calculate the distance betwing the two line
        """
        x=abs(qtPointF_1.x()-qtPointF_2.x())
        y=abs(qtPointF_1.y()- qtPointF_2.y())
        return math.sqrt(x**2+y**2)
