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
def _draw_fillet(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    if _col is None:
        _col = self.getColor()
    _cx, _cy = self.getCenter()
    _pcx, _pcy = gimage.coordToPixTransform(_cx, _cy)
    _p1, _p2 = self.getMovingPoints()
    _p1x, _p1y = gimage.coordToPixTransform(_p1.x, _p1.y)
    _p2x, _p2y = gimage.coordToPixTransform(_p2.x, _p2.y)
    _r = self.getRadius()
    _rx, _ry = gimage.coordToPixTransform((_cx + _r), _cy)
    _pr = _rx - _pcx
    _sa1, _sa2 = self.getAngles()
    _amin = min(_sa1, _sa2)
    _amax = max(_sa1, _sa2)
    if _amax - _amin > 180.0:
        _a1 = _amax
        _a2 = _amin
    else:
        _a1 = _amin
        _a2 = _amax
    # print "a1: %g" % _a1
    # print "a2: %g" % _a2
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
        _ra1 = _a1 * _dtr
        _ra2 = _a2 * _dtr
        #
        # arc drawing relies on Cairo transformations
        #
        _ctx.scale(1.0, -1.0)
        _ctx.translate(_pcx, -(_pcy))
        _ctx.arc(0, 0, _pr, _ra1, _ra2)
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)        
        _pxmin = _pcx - _pr
        _pymin = _pcy - _pr
        _cw = _ch = _pr * 2
        if _a1 > _a2:
            _sweep = 360.0 - (_a1 - _a2)
        else:
            _sweep = _a2 - _a1
        gimage.getPixmap().draw_arc(_gc, False,
                                    _pxmin, _pymin,
                                    _cw, _ch,
                                    int(round(_a1 * 64)),
                                    int(round(_sweep * 64)))

#----------------------------------------------------------------------------------------------------
def _erase_fillet(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

