#
# Copyright (c) 2005, 2006 Art Haas
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
# code for adding graphical methods to drawing entities
#

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic.point import Point
    

#----------------------------------------------------------------------------------------------------
def _sample_polygon(self, viewport, color):
    # display properties
    lineweight = None
    linestyle = None
    # add points to list
    points = []
    # first sides
    x, y = self.getCoord(0)
    p1 = Point(x, y)
    points.append(p1)
    count = self.getSideCount()
    for i in range(1, count):
        x, y = self.getCoord(i)
        points.append(Point(x, y))
    # append first point to close
    points.append(p1)
    # do the actual draw of the linestring
    viewport.draw_linestring(color, lineweight, linestyle, points)    
