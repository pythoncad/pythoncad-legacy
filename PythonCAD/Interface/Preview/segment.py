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
# SegmentPreview object
#
import math



from Interface.Preview.basepreview  import *
from Kernel.GeoEntity.segment       import Segment as geoSegment
from Kernel.initsetting             import PYTHONCAD_HIGLITGT_COLOR


class Segment(BasePreview):
    def __init__(self, command):
        super(Segment, self).__init__(command)
        
    def getPreviewObject(self, point, value):
        """
            return the preview object
        """
        if len(self._command.value)>0:
            x, y=self._command.value[0].getCoords()
            p1=QtCore.QPointF(x,y*-1.0)
            p2=QtCore.QPointF(point.x,point.y*-1.0)
            return QtSegmentItem(p1,p2)
        else:
            return None

class QtSegmentItem(BaseQtPreviewItem):
    def __init__(self, p1, p2):
        super(QtSegmentItem, self).__init__()
        self.p1=p1
        self.p2=p1
        r, g, b=PYTHONCAD_HIGLITGT_COLOR
        self.color = QtGui.QColor.fromRgb(r, g, b)
        
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        #painter.setPen(QtGui.QPen(self.color, self.lineWith))
        painter.setPen(QtGui.QPen(self.color))
        #draw geometry
        #painter.drawPath(self.shape()
        painter.drawLine(self.p1,self.p2)
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        x=min(self.p1.x(), self.p2.x())-100.0
        y=min(self.p1.y(), self.p2.y())-100.0
        d1=abs(self.p1.x()-self.p2.x())**2
        d2=abs(self.p1.y()-self.p2.y())**2
        d=math.sqrt(d1+d2)**2
        return QtCore.QRectF(x,y ,d,d)
        
    def firstPoint(self, p):
        self.p1=p
        
    def secondPoint(self, p):
        self.p2=p
        
