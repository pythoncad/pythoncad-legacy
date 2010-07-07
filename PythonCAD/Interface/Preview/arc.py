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

from Interface.Preview.base         import *
from Kernel.GeoEntity.segment       import Segment as geoSegment

class Arc(Base):
    def __init__(self, command):
        super(Arc, self).__init__(command)
        
    def getPreviewObject(self):
        """
            return the preview object
        """
        if len(self._command.value)>0:
            return QtArcItem(self._command)
        else:
            return None

class QtArcItem(BaseQtPreviewItem):
    def __init__(self, command):
        super(QtArcItem, self).__init__(command)
        # get the geometry
    
    def drawGeometry(self, painter,option,widget):
        """
            overloading of the paint method
        """
        if self.center and self.radius:
            # By default, the span angle is 5760 (360 * 16, a full circle).
            # From pythoncad the angle are in radiant ..
            startAngle=(self.startAngle*180.0/math.pi)*16.0
            spanAngle=(self.spanAngle*180.0/math.pi)*16.0 
            xc=self.center.x()-self.radius
            yc=self.center.y()-self.radius
            h=self.radius*2.0
            painter.drawArc(xc,yc ,h ,h ,startAngle,  spanAngle)

    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        if self.center and self.radius:
            _s=self.radius
            
            xc=self.center.x()-_s
            print self.center.x(), _s, xc
            yc=self.center.y()-_s
            _h=(_s*2.0)
            print "boundingRect",self.center,xc,yc, _h
            return QtCore.QRectF(xc,yc,_h ,_h)
        return QtCore.QRectF(0,0 ,0.1,0.1)
    @property
    def center(self):
        return self.value[0]
    @center.setter
    def center(self, value):
        self.value[0]=value
        self.update(self.boundingRect())
    @property
    def radius(self):    
        return self.value[1]
    @radius.setter
    def radius(self, value):
        self.value[1]=value
        self.update(self.boundingRect())
    @property
    def startAngle(self):
        return self.value[2]
    @startAngle.setter
    def startAngle(self, value):
        self.value[2] =value
        self.update(self.boundingRect())
    @property
    def spanAngle(self):
        return self.value[3]
    @spanAngle.setter
    def spanAngle(self, value):
        self.value[3]=value
        self.update(self.boundingRect())
