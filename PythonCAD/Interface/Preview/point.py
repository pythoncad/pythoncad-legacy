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
# qt pythoncad Point class
#

import math
#
from Interface.Preview.base         import *
from Kernel.GeoEntity.segment       import Segment as geoSegment
from Kernel.initsetting             import PYTHONCAD_PREVIEW_COLOR
#
from PyQt4 import QtCore, QtGui

class PreviewPoint(PreviewBase):
    """
        this class define the arcQT object
    """
    def __init__(self, command):

        super(PreviewPoint, self).__init__(command)

    def drawShape(self, painterPath):
        """
            overloading of the shape method
        """
        if len(self.value)<0:
            return
        qtPoinfF = self.value[0]
        painterPath.addRect(QtCore.QRectF(qtPoinfF.x()-self.shapeSize/2,qtPoinfF.y()-self.shapeSize/2 ,self.shapeSize ,self.shapeSize))

    def drawGeometry(self, painter, option, widget):
        """
            overloading of the paint method
        """
        if len(self.value)<0:
            return
        qtPoinfF = self.value[0]
        painter.drawRect(QtCore.QRectF(qtPoinfF.x()-self.shapeSize/2,qtPoinfF.y()-self.shapeSize/2 ,self.shapeSize ,self.shapeSize))
        painter.drawPoint(qtPoinfF)

    def boundingRect(self):
        if len(self.value)<0:
            return QtCore.QRectF(0, 0, 0, 0)
        qtPoinfF = self.value[0]
        return QtCore.QRectF(qtPoinfF.x()-self.shapeSize/2,qtPoinfF.y()-self.shapeSize/2 ,self.shapeSize ,self.shapeSize)








