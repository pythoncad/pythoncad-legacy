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

from PyQt4 import QtCore, QtGui

class Text(QtGui.QGraphicsTextItem):
    
    def __init__(self, entity):
        super(Text, self).__init__()
        pt_begin = None
        pt_end = None
        # get the geometry
        geometry = entity.getConstructionElements()
        keys=geometry.keys()
        #text,geometry[keys[2]] 
        #angle,geometry[keys[1]] 
        #location,geometry[keys[0]]
        #pointPosition,geometry[keys[3]]
        self.ID=entity.getId()
        self.setPlainText(geometry[keys[2]] )#text
        x, y=geometry[keys[0]].getCoords() #location
        self.setPos(x, -1.0*y)
       
        # set pen accoording to layer
        #self.setPen(QtGui.QPen(QtGui.QColor.fromRgb(255, 0, 0)))
        return
    
