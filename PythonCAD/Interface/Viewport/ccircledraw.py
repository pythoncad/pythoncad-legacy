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


  
#----------------------------------------------------------------------------------------------------
def _draw_ccircle(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _cp = self.getCenter()
    _x, _y = _cp.getCoords()
    _r = self.getRadius()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    _rx, _ry = gimage.coordToPixTransform((_x + _r), _y)
    _rad = _rx - _px
    _dlist = self.getLinetype().getList()
    if _col is None:
        _col = self.getColor()
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _dlist is not None:
            _ctx.set_dash(_dlist)
        _ctx.set_line_width(1.0)
        _ctx.arc(_px, _py, _rad, 0, (2.0 * pi))
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()        
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), 1)
        _cw = _ch = _rad * 2
        _pxmin = _px - _rad
        _pymin = _py - _rad
        gimage.getPixmap().draw_arc(_gc, False,
                                    _pxmin, _pymin,
                                    _cw, _ch,
                                    0, (360*64))

#----------------------------------------------------------------------------------------------------
def _erase_ccircle(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
