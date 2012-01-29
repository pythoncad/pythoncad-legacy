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
from PyQt4 import QtCore, QtGui
from Interface.Preview.base         import PreviewBase
from Interface.Entity.arc           import Arc


#TODO+: find a good way to retrive the geometry staff from a item in Interface.Entity.arc ..
#extend it for all the preview entity

class PreviewArc(PreviewBase):
    def __init__(self,command):
        super(PreviewArc, self).__init__(command)
    
    @property
    def canPaint(self):
#        self.xc,
#        self.yc,
#        self.h,
#        self.h
#               
#        return self.value[0]!=None and self.value[1]!=None
        return False
    
    def arcRect(self):    
        return QtCore.QRectF(self.xc,
                             self.yc,
                             self.h,
                             self.h)
        
    def drawGeometry(self, painter,option,widget):
        """
            Overloading of the paint method
        """
        if self.canPaint:
            Arc.__dict['drawGeometry'](self, painter,option,widget)

    def drawShape(self, painterPath):
        """
            overloading of the shape method
        """
        if self.canPaint:
            Arc.__dict['drawShape'](self, painterPath)

      
        
        