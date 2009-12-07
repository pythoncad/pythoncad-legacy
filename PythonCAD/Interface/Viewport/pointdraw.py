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
#from PythonCAD.Generic import dimension
#from PythonCAD.Generic import layer
#
#from PythonCAD.Interface.Gtk import gtkimage

_point_color = color.Color(255, 255, 255) # white


#----------------------------------------------------------------------------------------------------
def _draw_point(self, viewport, col=None):
    print "_draw_point()"
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    if color is None:
        color = _point_color
    # point coordinates
    x, y = self.getCoords()
    # transformation to viewport coordinates
    px, py = viewport.WorldToViewport(x, y)
    # cairo context
    ctx = viewport.CairoContext
    if ctx is not None:
        ctx.save()
        r, g, b = color.getColors()
        ctx.set_source_rgb((r/255.0), (g/255.0), (b/255.0))
        ctx.move_to(px, py)
        ctx.line_to(px, py)
        ctx.stroke()
        ctx.restore()
    # draw the point in highlight color
    if viewport.Image.getOption('HIGHLIGHT_POINTS'):
        count = 0
        for user in self.getUsers():
            if not isinstance(user, dimension.Dimension):
                count = count + 1
            if count > 1:
                break
        # 
        if count > 1:
            color = viewport.Image.getOption('MULTI_POINT_COLOR')
        else:
            color = viewport.Image.getOption('SINGLE_POINT_COLOR')
        # use cairo to draw
        if ctx is not None:
            ctx.save()
            r, g, b = color.getColors()
            ctx.set_source_rgb((r/255.0), (g/255.0), (b/255.0))
            ctx.rectangle((px - 5), (py - 5), 10, 10)
            ctx.stroke()
            ctx.restore()

#----------------------------------------------------------------------------------------------------
def _erase_point(self, viewport):
    _x, _y = self.getCoords()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    _w, _h = gimage.getSize()
    if (((_px + 5) < 0) or
        ((_py + 5) < 0) or
        ((_px - 5) > _w) or
        ((_py - 5) > _h)):
        return
    _image = gimage.getImage()
    _col = _image.getOption('BACKGROUND_COLOR')
    _pixmap = _gc = None
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        if(_col!=None):
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        _ctx.move_to(_px, _py)
        _ctx.line_to(_px, _py)
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _gc.set_foreground(gimage.getColor(_col))
        _pixmap = gimage.getPixmap()
        _pixmap.draw_point(_gc, _px, _py)
    if _image.getOption('HIGHLIGHT_POINTS'):
        if _ctx is not None:
            _ctx.save()
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            _ctx.rectangle((_px - 5), (_py - 5), 10, 10)
            _ctx.stroke()
            _ctx.restore()
        else:
            _gc.set_function(gtk.gdk.COPY)
            _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                    gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_MITER)
            _pixmap.draw_rectangle(_gc, False, (_px - 5), (_py - 5), 10, 10)

