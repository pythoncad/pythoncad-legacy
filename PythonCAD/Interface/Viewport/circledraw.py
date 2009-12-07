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

import types
from math import pi
pi2 = 2 * pi
from math import cos
from math import sin

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic.point import Point


#----------------------------------------------------------------------------------------------------
def _draw_circle(self, viewport, col=None):
    print "_draw_circle()"
    # display quality (higher value = better circle draw) 
    stroke_value = 5
    #
    color = col
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # display properties
    lineweight = self.getThickness()
    linestyle = self.getLinetype().getList()
    # centerpoint of the circle
    center = self.getCenter()
    x, y = center.getCoords()
    # circle radius
    radius = self.getRadius()
    size = viewport.WorldToViewportSize(radius)
    if size < 10:
        size = 10
    increment_angle = stroke_value * pi / size
    # start angle
    angle = 0.0
    # pointlist
    points = []
    # calculate points
    while angle < pi2:
        x1 = x + radius * cos(angle)
        y1 = y + radius * sin(angle)
        points.append(Point(x1, y1))
        # next angle
        angle += increment_angle
    # add close point
    points.append(points[0])
    # do the actual draw of the linestring
    viewport.draw_linestring(color, lineweight, linestyle, points)    

#----------------------------------------------------------------------------------------------------
def _erase_circle(self, viewport):
    self.draw(viewport, viewport.Image.getOption('BACKGROUND_COLOR'))

