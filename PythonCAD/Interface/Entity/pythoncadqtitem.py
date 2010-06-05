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
# qt base item
#

import math
from PyQt4 import QtCore, QtGui

class PythoncadQtItem(QtGui.QGraphicsItem):
    
    def __init__(self, entity):
        super(PythoncadQtItem, self).__init__()
        self.__geometry = entity.getConstructionElements()
        self.__style=entity.getInnerStyle()
        self.__ID=entity.getId()
        return

    @property
    def ID(self):
        return self.__ID
    @property
    def style(self):
        return self.__style
    @property
    def geometry(self):
        return self.__geometry

