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
_dtr = (pi/180.0)

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic.point import Point
    
#----------------------------------------------------------------------------------------------------
def _draw_polyline(self, viewport, col=None):
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
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
    
    
    
    #if not isinstance(gimage, gtkimage.GTKImage):
        #raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    #_col = col
    #if _col is not None and not isinstance(_col, color.Color):
        #raise TypeError, "Invalid Color: " + `type(_col)`
    #_pts = []
    #for _pt in self.getPoints():
        #_x, _y = _pt.getCoords()
        #_px, _py = gimage.coordToPixTransform(_x, _y)
        #_pts.append((_px, _py))
    #if _col is None:
        #_col = self.getColor()
    #_dlist = self.getLinetype().getList()
    #_lw = self.getThickness()#/gimage.getUnitsPerPixel()
    #_ctx = gimage.getCairoContext()
    #if _ctx is not None:
        #_ctx.save()
        #_r, _g, _b = _col.getColors()
        #_ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        #if _dlist is not None:
            #_ctx.set_dash(_dlist)
        #_ctx.set_line_width(_lw)
        #_px, _py = _pts[0]
        #_ctx.move_to(_px, _py)
        #for _px, _py in _pts[1:]:
            #_ctx.line_to(_px, _py)
        #_ctx.stroke()
        #_ctx.restore()
    #else:
        #_gc = gimage.getGC()
        #_set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
        #gimage.getPixmap().draw_lines(_gc, _pts)

#----------------------------------------------------------------------------------------------------
def _erase_polyline(self, viewport):
    self.draw(viewport, viewport.Image.getOption('BACKGROUND_COLOR'))


