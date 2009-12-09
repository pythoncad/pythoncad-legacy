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
from math import cos
from math import sin

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic.point import Point


#----------------------------------------------------------------------------------------------------
def _draw_arc(self, viewport, col=None):
    print "_draw_arc()"
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
#    size = viewport.WorldToViewportSize(radius)
#    if size < 10:
#        size = 10
#    increment_angle = stroke_value * pi / size
    # start and end angle
    start = self.getStartAngle()
    end = self.getEndAngle()
    # do the actual draw of the arc
    viewport.draw_arc(color, lineweight, linestyle, center, radius, start, end)
#    # pointlist
#    points = []
#    # calculate points
#    while startangle < endangle:
#        x1 = x + radius * cos(startangle)
#        y1 = y + radius * sin(startangle)
#        points.append(Point(x1, y1))
#        # next angle
#        startangle += increment_angle
#    # add close point
#    #points.append(points[0])
#    # do the actual draw of the linestring
#    viewport.draw_linestring(color, lineweight, linestyle, points)
#
#
#
#
#
#
#    if not isinstance(gimage, gtkimage.GTKImage):
#        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
#    _col = col
#    if _col is not None and not isinstance(_col, color.Color):
#        raise TypeError, "Invalid Color: " + `type(_col)`
#    _layer = self.getParent()
#    if _layer is None:
#        raise RuntimeError, "No parent Layer for Arc"
#    _cp = self.getCenter()
#    _x, _y = _cp.getCoords()
#    _r = self.getRadius()
#    _sa = self.getStartAngle()
#    _ea = self.getEndAngle()
#    _px, _py = gimage.coordToPixTransform(_x, _y)
#    _rx, _ry = gimage.coordToPixTransform((_x + _r), _y)
#    _rad = _rx - _px
#    if _col is None:
#        _col = self.getColor()
#    _dlist = self.getLinetype().getList()
#    _lw = self.getThickness()#/gimage.getUnitsPerPixel()
#    _ctx = gimage.getCairoContext()
#    if _ctx is not None:
#        _ctx.save()
#        _r, _g, _b = _col.getColors()
#        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
#        if _dlist is not None:
#            _ctx.set_dash(_dlist)
#        _ctx.set_line_width(_lw)
#        _rsa = _sa * _dtr
#        _rea = _ea * _dtr
#        #
#        # arc drawing relies on Cairo transformations
#        #
#        _ctx.scale(1.0, -1.0)
#        _ctx.translate(_px, -(_py))
#        if abs(_sa - _ea) < 1e-10:
#            _ctx.arc(0, 0, _rad, _rsa, (_rsa + (2.0 * pi)))
#        else:
#            _ctx.arc(0, 0, _rad, _rsa, _rea)
#        _ctx.stroke()
#        _ctx.restore()

#----------------------------------------------------------------------------------------------------
def _erase_arc(self, viewport):
    self.draw(viewport, viewport.Image.getOption('BACKGROUND_COLOR'))
    
