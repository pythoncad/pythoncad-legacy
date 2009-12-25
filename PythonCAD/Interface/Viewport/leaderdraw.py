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

from PythonCAD.Generic import color
from PythonCAD.Generic.point import Point

    
#----------------------------------------------------------------------------------------------------
def _draw_leader(self, viewport, col=None):
    color = col
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # display properties
    lineweight = self.getThickness()
    linestyle = self.getLinetype().getList()
    # get 3 points of the leader line
    p1, p2, p3 = self.getPoints()
    # add points to list
    points = []
    points.append(p1)
    points.append(p2)
    points.append(p3)
    # do the actual draw of the leaderline
    viewport.draw_linestring(color, lineweight, linestyle, points)
    # get 2 points of arrow
    pts = self.getArrowPoints()
    points = []
    points.append(Point(pts[0], pts[1]))
    points.append(p3)
    points.append(Point(pts[2], pts[3]))
    # do the actual draw of the arrow
    viewport.draw_polygon(color, lineweight, linestyle, points, True)

#----------------------------------------------------------------------------------------------------
def _erase_leader(self, viewport):
    self.draw(viewport, viewport.gimage.getOption('BACKGROUND_COLOR'))
    