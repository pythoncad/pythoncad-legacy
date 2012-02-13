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
import sys
if sys.version_info <(2, 7):
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

import math
from PyQt4  import QtCore, QtGui

from Kernel.initsetting         import PYTHONCAD_HIGLITGT_COLOR, PYTHONCAD_COLOR, MOUSE_GRAPH_DIMENSION

from Kernel.GeoEntity.point     import Point

class BaseEntity(QtGui.QGraphicsItem):
    shapeSize=MOUSE_GRAPH_DIMENSION
    showShape=False #This Flag is used for debug porpoise
    showBBox=False  #This Flag is used for debug porpoise
    def __init__(self, entity):
        super(BaseEntity, self).__init__()
        self.setAcceptsHoverEvents(True)                        #Fire over events
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        #Get the geometry
        self._entity=entity
        self.setToolTip(str(self.toolTipMessage))
        #Set color from style
        r, g, b= self.style.getStyleProp("entity_color")
        color = QtGui.QColor.fromRgb(r, g, b)
        #set line thickness
        lineWith=self.style.getStyleProp("entity_thickness")
        #set line style
        penStyle=self.style.getStyleProp("entity_linetype")
        pen=QtGui.QPen(color)
        #TODO: Actually disable because the line with is not very nice
        #in the drawing ..
        #pen.setWidthF(float(lineWith))
        pen.setStyle(int(penStyle))
        self.pen=pen
        return

    def nearestSnapPoint(self, qtPointEvent, snapForceType=None, fromEntity=None):
        """
            compute the nearest point and return a qtPoint
        """
        pClick=Point(qtPointEvent.x(), qtPointEvent.y()*-1.0)
        ePoint=None
        for p in self.geoItem.getUpdatedSnapPoints(snapForceType, pClick,fromEntity):
            distance=p.dist(pClick)
            if ePoint==None:
                oldDistance=distance
                ePoint=p
            else:
                if oldDistance>distance:
                    oldDistance=distance
                    ePoint=p
        if ePoint==None:
            return qtPointEvent
        return QtCore.QPointF(ePoint.x, ePoint.y*-1.0)

    @property
    def entity(self):
        return self._entity
    @property
    def ID(self):
        return self._entity.getId()
    @property
    def geoItem(self):
        return self._entity.toGeometricalEntity()
    @property
    def style(self):
        return self._entity.getInnerStyle()
    @property
    def toolTipMessage(self):
        toolTipMessage=self.geoItem.info
        return toolTipMessage

    def updateSelected(self):
        self.setColor()
        self.update(self.boundingRect())
        return

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            #self.setColor(value==1)
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
        color = QtGui.QColor.fromRgb(r, g, b)
        self.pen.setColor(color)
        return

    def setHiglight(self):
        r, g, b=PYTHONCAD_HIGLITGT_COLOR
        color = QtGui.QColor.fromRgb(r, g, b)
        self.pen.setColor(color)
        return

    def hoverEnterEvent(self, event):
        self.setHiglight()
        super(BaseEntity, self).hoverEnterEvent(event)
        return

    def hoverLeaveEvent(self, event):
        self.setColor()
        super(BaseEntity, self).hoverLeaveEvent(event)
        return

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
        painterStrock.setWidth(self.shapeSize)
        path1=painterStrock.createStroke(path)
        return path1

    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        #draw geometry
        if self.showShape:
            r, g, b= PYTHONCAD_COLOR["cyan"]
            painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
            painter.drawPath(self.shape())

        if self.showBBox:
            r, g, b= PYTHONCAD_COLOR["darkblue"]
            painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
            painter.drawRect(self.boundingRect())

        painter.setPen(self.pen)
        self.drawGeometry(painter,option,widget)
        return

    def getDistance(self, qtPointF_1, qtPointF_2):
        """
            calculate the distance betwing the two line
        """
        x=abs(qtPointF_1.x()-qtPointF_2.x())
        y=abs(qtPointF_1.y()- qtPointF_2.y())
        return math.sqrt(x**2+y**2)

    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return self.shape().boundingRect()




