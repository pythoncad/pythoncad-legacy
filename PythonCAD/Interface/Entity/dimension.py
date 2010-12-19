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
# qt text class
#

from math import degrees

from Kernel.GeoUtil.geolib                 import Vector

from Interface.Entity.base import *

class Dimension(BaseEntity):
    def __init__(self, entity):
        super(Dimension, self).__init__(entity)
        self.updateInfo()
        self.location=self.calculateTextPoint()       
        self.font=QtGui.QFont() # This have to be derived from the geoent as son is implemented       return
        #self.setPos(QtCore.QPointF(self.firstPoint.x, self.firstPoint.y) )
        #self.rotate(self.angle)        
        
    def updateInfo(self):
        geoEnt=self.geoItem
        self.firstPoint=geoEnt.firstPoint
        self.secondPoint=geoEnt.secondPoint
        self.thirdPoint=geoEnt.thirdPoint
        self.angle=degrees(geoEnt.angle)
        self.text=str(geoEnt.distance)  # TODO : take care of style in case of
                                        #        additional info at the text
        self.segments=self.getDimensioLines()
        
    def calculateTextPoint(self):       # TODO : test if the position is ok
        """
            calculate the text position
        """
        t=self.getDimensioLines()
        p1, p2=t[0]
        p1=Point(p1.x(), p1.y())
        v=Vector(p1, Point(p2.x(), p2.y()))
        vm=v.mag()
        vm.mult(v.norm/2)
        pe=p1+vm.point
        return QtCore.QPointF(pe.x, pe.y) 
        
    
    def getDimensioLines(self):
        """
            compute all the segment needed for the dimension
        """
        p1p2v=Vector(self.firstPoint, self.secondPoint) 
        v=Vector(self.firstPoint,self.thirdPoint)
        pp=self.firstPoint+p1p2v.map(v.point).point
        p3ppv=Vector(pp, self.thirdPoint)
        #
        fp=self.firstPoint+p3ppv.point
        fp=QtCore.QPointF(fp.x, fp.y*-1.0)
        sp=self.secondPoint+p3ppv.point
        sp=QtCore.QPointF(sp.x, sp.y*-1.0)
        #
        fp1=QtCore.QPointF(self.firstPoint.x, self.firstPoint.y*-1.0)
        sp1=QtCore.QPointF(self.secondPoint.x, self.secondPoint.y*-1.0)
        #
        return [(fp, sp), (fp, fp1), (sp, sp1)]
        
    def drawShape(self, painterPath):    
        """
            overloading of the shape method 
        """
        painterPath.addText(self.location, self.font, self.text) 
        for p1, p2 in self.segments:
            painterPath.moveTo(p1)
            painterPath.lineTo(p2)
        return
        
    def drawGeometry(self, painter, option, widget):
        #Create Text
        painter.drawText(self.location,  self.text)
        for p1, p2 in self.segments:
            painter.drawLine(p1, p2)
        
