#!/usr/bin/env python
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
# You should have received a copy of the GNU General Public Licensesegmentcmd.py
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#This module provide a class for the segment command
#
from PyQt4 import QtCore, QtGui


from Kernel.exception       import *
from Kernel.GeoEntity.point import Point as GeoPoint
from Kernel.GeoUtil.geolib  import Vector
from Kernel.initsetting     import PYTHONCAD_COLOR, PYTHONCAD_PREVIEW_COLOR, MOUSE_GRAPH_DIMENSION

class PreviewBase(QtGui.QGraphicsItem):
    showShape=False # This Flag is used for debug porpoise
    showBBox=False  # This Flag is used for debug porpoise
    shapeSize=MOUSE_GRAPH_DIMENSION
    def __init__(self, command):
        super(PreviewBase, self).__init__()
        self.updateColor()
        self.value=[]
        for dValue in command.defaultValue:
            val=self.revertToQTObject(dValue)
            self.value.append(val)

    def updateColor(self):
        """
            update the preview color
        """
        r, g, b=PYTHONCAD_PREVIEW_COLOR
        self.color = QtGui.QColor.fromRgb(r, g, b)

    def updatePreview(self,  position, distance, kernelCommand):
        """
            update the data at the preview item
        """
        self.prepareGeometryChange() #qtCommand for update the scene
        for i in range(0, len(kernelCommand.value)):
            self.value[i]=self.revertToQTObject(kernelCommand.value[i])
        # Assing Command Values
        index=kernelCommand.valueIndex
        try:
            raise kernelCommand.exception[index](None)
        except(ExcPoint):
            self.value[index]=self.revertToQTObject(position)
        except(ExcLenght, ExcInt):
            if not distance or distance !=None:
                self.value[index]=distance
        except(ExcAngle):
            p1=GeoPoint(0.0, 0.0)
            p2=GeoPoint(position.x(), position.y())
            self.value[index]=Vector(p1, p2).absAng
        except:
            print "updatePreview: Exception not managed"
            return

    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        if self.showShape:
            r, g, b= PYTHONCAD_COLOR["cyan"]
            painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
            painter.drawPath(self.shape())

        if self.showBBox:
            r, g, b= PYTHONCAD_COLOR["darkblue"]
            painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
            painter.drawRect(self.boundingRect())

        self.drawGeometry(painter,option,widget)
        return
    
    def convertToQTObject(self, value):
        """
            convert the input value in a proper value
        """
        if isinstance(value, (float, int)):
            return value
        elif isinstance(value, tuple):
            return QtCore.QPointF(value[0], value[1])
        elif isinstance(value, GeoPoint):
            return QtCore.QPointF(value.x, value.y)
        else:
            return value
        
    def revertToQTObject(self, value):
        """
            convert the input value in a proper value GeoObject -> qtObject
        """
        if isinstance(value, (float, int)):
            return value
        elif isinstance(value, tuple):
            return QtCore.QPointF(value[0], value[1]*-1.0)
        elif isinstance(value, GeoPoint):
            return QtCore.QPointF(value.x, value.y*-1.0)
        else:
            return value

    def shape(self):
        """
            overloading of the shape method
        """
        PainterPath=QtGui.QPainterPath()
        self.drawShape(PainterPath)
        painterStrock=QtGui.QPainterPathStroker()
        painterStrock.setWidth(10)
        painterStrockPath=painterStrock.createStroke(PainterPath)
        return painterStrockPath

    def drawShape(self, path):
        pass

    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return self.shape().boundingRect()

