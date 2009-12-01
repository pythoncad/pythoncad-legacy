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
from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import segjoint
from PythonCAD.Generic import conobject
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic import layer

from PythonCAD.Interface.Gtk import gtkimage


    
#----------------------------------------------------------------------------------------------------
def _draw_leader(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _p1, _p2, _p3 = self.getPoints()
    _p1x, _p1y = gimage.coordToPixTransform(_p1.x, _p1.y)
    _p2x, _p2y = gimage.coordToPixTransform(_p2.x, _p2.y)
    _p3x, _p3y = gimage.coordToPixTransform(_p3.x, _p3.y)
    _pts = self.getArrowPoints()
    _a1x, _a1y = gimage.coordToPixTransform(_pts[0], _pts[1])
    _a2x, _a2y = gimage.coordToPixTransform(_pts[2], _pts[3])
    if _col is None:
        _col = self.getColor()
    _dlist = self.getLinetype().getList()
    _lw = self.getThickness()#/gimage.getUnitsPerPixel()
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _dlist is not None:
            _ctx.set_dash(_dlist)
        _ctx.set_line_width(_lw)
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _ctx.line_to(_p3x, _p3y)
        _ctx.stroke()
        _ctx.move_to(_p3x, _p3y)
        _ctx.line_to(_a1x, _a1y)
        _ctx.line_to(_a2x, _a2y)
        _ctx.close_path()
        _ctx.fill()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
        _pixmap = gimage.getPixmap()
        _pts = [(_p1x, _p1y), (_p2x, _p2y), (_p3x, _p3y)]
        _pixmap.draw_lines(_gc, _pts)
        _apts = [(_p3x, _p3y), (_a1x, _a1y), (_a2x, _a2y)]
        _pixmap.draw_polygon(_gc, True, _apts)

#----------------------------------------------------------------------------------------------------
def _erase_leader(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    