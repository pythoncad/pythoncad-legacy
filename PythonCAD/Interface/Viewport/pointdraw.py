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
#from PythonCAD.Generic import point
#from PythonCAD.Generic import segment
#from PythonCAD.Generic import circle
#from PythonCAD.Generic import arc
#from PythonCAD.Generic import leader
#from PythonCAD.Generic import polyline
#from PythonCAD.Generic import segjoint
#from PythonCAD.Generic import conobject
#from PythonCAD.Generic import hcline
#from PythonCAD.Generic import vcline
#from PythonCAD.Generic import acline
#from PythonCAD.Generic import cline
#from PythonCAD.Generic import ccircle
#from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
#from PythonCAD.Generic import layer
#
#from PythonCAD.Interface.Gtk import gtkimage

_point_color = color.Color(255, 255, 255) # white


#----------------------------------------------------------------------------------------------------
def _draw_point(self, viewport, col=None):
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    if color is None:
        color = _point_color
    # point coordinates
    x, y = self.getCoords()
    # transformation to viewport coordinates
    px, py = viewport.world_to_view(x, y)
    # cairo context
    ctx = viewport.cairo_context
    if ctx is not None:
        # draw the point itself
        ctx.save()
        r, g, b = color.getColors()
        ctx.set_source_rgb((r/255.0), (g/255.0), (b/255.0))
        # set path
        ctx.move_to(px, py)
        ctx.line_to(px, py)
        ctx.stroke()
        ctx.restore()
    # draw the point in highlight color
    if viewport.gimage.getOption('HIGHLIGHT_POINTS'):
        count = 0
        for user in self.getUsers():
            if not isinstance(user, dimension.Dimension):
                count = count + 1
            if count > 1:
                break
        # 
        if count > 1:
            color = viewport.gimage.getOption('MULTI_POINT_COLOR')
        else:
            color = viewport.gimage.getOption('SINGLE_POINT_COLOR')
        # use cairo to draw
        if ctx is not None:
            # draw the point representation as a rectangle
            ctx.save()
            r, g, b = color.getColors()
            ctx.set_source_rgb((r/255.0), (g/255.0), (b/255.0))
            # set path
            ctx.rectangle((px - 5), (py - 5), 10, 10)
            ctx.stroke()
            ctx.restore()

#----------------------------------------------------------------------------------------------------
def _erase_point(self, viewport):
    # point coordinates
    x, y = self.getCoords()
    # transformation to viewport coordinates
    px, py = viewport.world_to_view(x, y)
    
    _x, _y = self.getCoords()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    _w, _h = gimage.getSize()
    _image = gimage.getImage()
    color = viewport.gimage.getOption('BACKGROUND_COLOR')
    
    # cairo context
    ctx = viewport.cairo_context    
    if ctx is not None:
        # erase the point itself
        ctx.save()
        if(color != None):
            r, g, b = color.getColors()
            ctx.set_source_rgb((r/255.0), (g/255.0), (b/255.0))
        # set path
        ctx.move_to(px, py)
        ctx.line_to(px, py)
        ctx.stroke()
        ctx.restore()

    if viewport.gimage.getOption('HIGHLIGHT_POINTS'):
        if ctx is not None:
            ctx.save()
            r, g, b = color.getColors()
            ctx.set_source_rgb((r/255.0), (g/255.0), (b/255.0))
            ctx.rectangle((px - 5), (py - 5), 10, 10)
            ctx.stroke()
            ctx.restore()

