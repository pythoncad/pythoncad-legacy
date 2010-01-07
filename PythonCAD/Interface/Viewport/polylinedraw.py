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
def _draw_polyline(self, viewport, col=None):
    color = col
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # display properties
    lineweight = self.getThickness()
    linestyle = self.getLinetype().getList()
    # get the pointlist
    points = self.getPoints()
    # do the actual draw of the linestring
    viewport.draw_linestring(color, lineweight, linestyle, points)    

#----------------------------------------------------------------------------------------------------
def _erase_polyline(self, viewport):
    self.draw(viewport, viewport.gimage.getOption('BACKGROUND_COLOR'))

#----------------------------------------------------------------------------------------------------
def _sample_polyline(self, viewport, color):
    # display properties
    lineweight = None
    linestyle = None
    # add points to list
    points = []
    # point tuples
    x_y_points = self.getPoints()
    # convert tuples to points
    for x_y_point in x_y_points:
        points.append(x_y_point.point)
    # append last point
    points.append(self.getCurrentPoint())
    # do the actual draw of the linestring
    viewport.draw_linestring(color, lineweight, linestyle, points)    

