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
from PythonCAD.Generic import util

from PythonCAD.Interface.Gtk import gtkimage

def _set_gc_values(gc, dl, c, t):
    if dl is None:
        _lt = gtk.gdk.LINE_SOLID
    else:
        _lt = gtk.gdk.LINE_DOUBLE_DASH
        gc.set_dashes(0, dl)
    gc.set_foreground(c)
    _t = t
    if not isinstance(_t, int):
        _t = int(round(t))
    if _t < 1: # no zero-pixel lines
        _t = 1
    gc.set_function(gtk.gdk.COPY)
    gc.set_line_attributes(_t, _lt, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_MITER)

_point_color = color.Color(255, 255, 255) # white

def _draw_point(self, gimage, col=None):
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _x, _y = self.getCoords()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    _w, _h = gimage.getSize()
    if (((_px + 5) < 0) or
        ((_py + 5) < 0) or
        ((_px - 5) > _w) or
        ((_py - 5) > _h)):
        return
    if _col is None:
        _col = _point_color
    _pixmap = _gc = None    
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
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
    _image = gimage.getImage()
    if _image.getOption('HIGHLIGHT_POINTS'):
        _count = 0
        for _user in self.getUsers():
            if not isinstance(_user, dimension.Dimension):
                _count = _count + 1
            if _count > 1:
                break
        if _count > 1:
            _col = _image.getOption('MULTI_POINT_COLOR')
        else:
            _col = _image.getOption('SINGLE_POINT_COLOR')
        if _ctx is not None:
            _ctx.save()
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            _ctx.rectangle((_px - 5), (_py - 5), 10, 10)
            _ctx.stroke()
            _ctx.restore()
        else:
            _set_gc_values(_gc, None, gimage.getColor(_col), 1)
            _pixmap.draw_rectangle(_gc, False, (_px - 5), (_py - 5), 10, 10)

def _erase_point(self, gimage):
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

def _draw_segment(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _xmin, _ymin, _xmax, _ymax = gimage.getView()
    _coords = self.clipToRegion(_xmin, _ymin, _xmax, _ymax)
    if _coords is not None:
        _p1, _p2 = self.getEndpoints()
        _x1, _y1, _x2, _y2 = _coords
        _p1x, _p1y = gimage.coordToPixTransform(_x1, _y1)
        _p2x, _p2y = gimage.coordToPixTransform(_x2, _y2)
        if _col is None:
            _col = self.getColor()
        _dlist = self.getLinetype().getList()
        _lw = self.getThickness() #/gimage.getUnitsPerPixel()
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
            _ctx.stroke()
            _ctx.restore()
        else:
            _gc = gimage.getGC()
            _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
            gimage.getPixmap().draw_line(_gc, _p1x, _p1y, _p2x, _p2y)

def _erase_segment(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

def _draw_circle(self, gimage, col=None):
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
        _ctx.arc(_px, _py, _rad, 0, (2.0 * pi))
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
        _pxmin = _px - _rad
        _pymin = _py - _rad
        _cw = _ch = _rad * 2
        gimage.getPixmap().draw_arc(_gc, False,
                                    _pxmin, _pymin,
                                    _cw, _ch,
                                    0, (360*64))

def _erase_circle(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

def _draw_arc(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _layer = self.getParent()
    if _layer is None:
        raise RuntimeError, "No parent Layer for Arc"
    _cp = self.getCenter()
    _x, _y = _cp.getCoords()
    _r = self.getRadius()
    _sa = self.getStartAngle()
    _ea = self.getEndAngle()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    _rx, _ry = gimage.coordToPixTransform((_x + _r), _y)
    _rad = _rx - _px
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
        _rsa = _sa * _dtr
        _rea = _ea * _dtr
        #
        # arc drawing relies on Cairo transformations
        #
        _ctx.scale(1.0, -1.0)
        _ctx.translate(_px, -(_py))
        if abs(_sa - _ea) < 1e-10:
            _ctx.arc(0, 0, _rad, _rsa, (_rsa + (2.0 * pi)))
        else:
            _ctx.arc(0, 0, _rad, _rsa, _rea)
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        for _ep in self.getEndpoints():
            _ex, _ey = _ep
            _pts = _layer.find('point', _ex, _ey)
            if len(_pts) == 0:
                raise RuntimeError, "No Arc endpoint at: " + str(_ep)
            _ept = None
            for _pt in _pts:
                for _user in _pt.getUsers():
                    if _user is self:
                        _ept = _pt
                        break
                if _ept is not None:
                    break
            if abs(_sa - _ea) < 1e-10:
                break
        _pxmin = _px - _rad
        _pymin = _py - _rad
        _cw = _ch = _rad * 2
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
        if abs(_sa - _ea) < 1e-10:
            _sweep = 360.0
        elif _sa > _ea:
            _sweep = 360.0 - (_sa - _ea)
        else:
            _sweep = _ea - _sa
        gimage.getPixmap().draw_arc(_gc, False,
                                    _pxmin, _pymin,
                                    _cw, _ch,
                                    int(round(_sa * 64)),
                                    int(round(_sweep * 64)))
def _erase_arc(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
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

def _erase_leader(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
def _draw_polyline(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _pts = []
    for _pt in self.getPoints():
        _x, _y = _pt.getCoords()
        _px, _py = gimage.coordToPixTransform(_x, _y)
        _pts.append((_px, _py))
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
        _px, _py = _pts[0]
        _ctx.move_to(_px, _py)
        for _px, _py in _pts[1:]:
            _ctx.line_to(_px, _py)
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
        gimage.getPixmap().draw_lines(_gc, _pts)

def _erase_polyline(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

def _draw_chamfer(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _p1, _p2 = self.getMovingPoints()
    _p1x, _p1y = gimage.coordToPixTransform(_p1.x, _p1.y)
    _p2x, _p2y = gimage.coordToPixTransform(_p2.x, _p2.y)
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
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), _lw)
        gimage.getPixmap().draw_line(_gc, _p1x, _p1y, _p2x, _p2y)

def _erase_chamfer(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

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

def _erase_fillet(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

def _draw_hcline(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _lp = self.getLocation()
    _x, _y = _lp.getCoords()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    if _col is None:
        _col = self.getColor()
    _dlist = self.getLinetype().getList()
    _w, _h = gimage.getSize()
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _dlist is not None:
            _ctx.set_dash(_dlist)
        _ctx.set_line_width(1.0)
        _ctx.move_to(0, _py)
        _ctx.line_to(_w, _py)
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), 1)
        gimage.getPixmap().draw_line(_gc, 0, _py, _w, _py)

def _erase_hcline(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
def _draw_vcline(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _lp = self.getLocation()
    _x, _y = _lp.getCoords()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    if _col is None:
        _col = self.getColor()
    _dlist = self.getLinetype().getList()
    _w, _h = gimage.getSize()
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _dlist is not None:
            _ctx.set_dash(_dlist)
        _ctx.set_line_width(1.0)
        _ctx.move_to(_px, 0)
        _ctx.line_to(_px, _h)
        _ctx.stroke()
        _ctx.restore()
    else:
        _gc = gimage.getGC()        
        _set_gc_values(_gc, _dlist, gimage.getColor(_col), 1)
        gimage.getPixmap().draw_line(_gc, _px, 0, _px, _h)

def _erase_vcline(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
def _draw_acline(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _xmin, _ymin, _xmax, _ymax = gimage.getView()
    _coords = self.clipToRegion(_xmin, _ymin, _xmax, _ymax)
    if _coords is not None:
        _lp = self.getLocation()
        _x1, _y1, _x2, _y2 = _coords
        _p1x, _p1y = gimage.coordToPixTransform(_x1, _y1)
        _p2x, _p2y = gimage.coordToPixTransform(_x2, _y2)
        _p1x, _p1y = gimage.coordToPixTransform(_x1, _y1)
        _p2x, _p2y = gimage.coordToPixTransform(_x2, _y2)
        if _col is None:
            _col = self.getColor()
        _dlist = self.getLinetype().getList()
        _ctx = gimage.getCairoContext()
        if _ctx is not None:
            _ctx.save()
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            if _dlist is not None:
                _ctx.set_dash(_dlist)
            _ctx.set_line_width(1.0)
            _ctx.move_to(_p1x, _p1y)
            _ctx.line_to(_p2x, _p2y)
            _ctx.stroke()
            _ctx.restore()
        else:
            _gc = gimage.getGC()
            _set_gc_values(_gc, _dlist, gimage.getColor(_col), 1)
            gimage.getPixmap().draw_line(_gc, _p1x, _p1y, _p2x, _p2y)

def _erase_acline(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
def _draw_cline(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _xmin, _ymin, _xmax, _ymax = gimage.getView()
    _coords = self.clipToRegion(_xmin, _ymin, _xmax, _ymax)
    if _coords is not None:
        _p1, _p2 = self.getKeypoints()
        _x1, _y1, _x2, _y2 = _coords
        _p1x, _p1y = gimage.coordToPixTransform(_x1, _y1)
        _p2x, _p2y = gimage.coordToPixTransform(_x2, _y2)
        if _col is None:
            _col = self.getColor()
        _dlist = self.getLinetype().getList()
        _ctx = gimage.getCairoContext()
        if _ctx is not None:
            _ctx.save()
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            if _dlist is not None:
                _ctx.set_dash(_dlist)
            _ctx.set_line_width(1.0)
            _ctx.move_to(_p1x, _p1y)
            _ctx.line_to(_p2x, _p2y)
            _ctx.stroke()
            _ctx.restore()
        else:
            _gc = gimage.getGC()
            _set_gc_values(_gc, _dlist, gimage.getColor(_col), 1)
            gimage.getPixmap().draw_line(_gc, _p1x, _p1y, _p2x, _p2y)

def _erase_cline(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
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

def _erase_ccircle(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    
def _format_layout(self, gimage, layout):
    _fd = pango.FontDescription()
    _fd.set_family(self.getFamily())
    _val = self.getStyle()
    if _val == text.TextStyle.FONT_NORMAL:
        _style = pango.STYLE_NORMAL
    elif _val == text.TextStyle.FONT_OBLIQUE:
        _style = pango.STYLE_OBLIQUE
    elif _val == text.TextStyle.FONT_ITALIC:
        _style = pango.STYLE_ITALIC
    else:
        raise ValueError, "Unexpected TextBlock font style: %d" % _val
    _fd.set_style(_style)
    _val = self.getWeight()
    if _val == text.TextStyle.WEIGHT_NORMAL:
        _weight = pango.WEIGHT_NORMAL
    elif _val == text.TextStyle.WEIGHT_LIGHT:
        _weight = pango.WEIGHT_LIGHT
    elif _val == text.TextStyle.WEIGHT_BOLD:
        _weight = pango.WEIGHT_BOLD
    elif _val == text.TextStyle.WEIGHT_HEAVY:
        _weight = pango.WEIGHT_HEAVY
    else:
        raise ValueError, "Unexpected TextBlock font weight: %d" % _val
    _fd.set_weight(_weight)
    _upp = gimage.getUnitsPerPixel()
    _sz = int(pango.SCALE * (self.getSize()/_upp))
    if _sz < pango.SCALE:
        _sz = pango.SCALE
    # print "pango units text size: %d" % _sz        
    _fd.set_size(_sz)
    #
    # todo: handle drawing rotated text
    #
    _align = self.getAlignment()
    if _align == text.TextStyle.ALIGN_LEFT:
        layout.set_alignment(pango.ALIGN_LEFT)
    elif _align == text.TextStyle.ALIGN_CENTER:
        layout.set_alignment(pango.ALIGN_CENTER)
    elif _align == text.TextStyle.ALIGN_RIGHT:
        layout.set_alignment(pango.ALIGN_RIGHT)
    else:
        raise ValueError, "Unexpected TextBlock alignment value: %d" % _align
    layout.set_font_description(_fd)
    if self.getLineCount() > 0:
        _w, _h = layout.get_pixel_size()
        self.setBounds((_w * _upp), (_h * _upp))

def _draw_textblock(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    try:
        _text=util.to_unicode(self.getText())
    except:
        print "Debug: Unable to unicode %s"%str(self.getText())
        _text='Error on converting in unicode'
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _layout = _ctx.create_layout()
        _layout.set_text(_text)
    else:
        _layout = gimage.getDA().create_pango_layout(_text)
    self._formatLayout(gimage, _layout)
    _x, _y = self.getLocation()
    _px, _py = gimage.coordToPixTransform(_x, _y)
    if _col is None:
        _col = self.getColor()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        _ctx.move_to(_px, _py)
        _ctx.show_layout(_layout)
        _ctx.restore()
    else:
        _gc = gimage.getGC()        
        _gc.set_foreground(gimage.getColor(_col))
        _gc.set_function(gtk.gdk.COPY)
        gimage.getPixmap().draw_layout(_gc, _px, _py, _layout)
    _layout = None
    
def _erase_textblock(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

def _draw_dimstrings(self, gimage, col=None):
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
    _da = gimage.getDA()
    #
    # fixme - calculating dimensions needs rework!
    #
    _image = gimage.getImage()
    _slen = _image.scaleLength(self.calculate())
    _dims = self.getDimensions(_slen)
    _dx, _dy = self.getLocation()
    _ds1 = _ds2 = _l1 = _l2 = _x1 = _y1 = _x2 = _y2 = None
    if self.getDualDimMode():
        _off = self.getDualModeOffset()
        _ds1 = self.getPrimaryDimstring()
        if _ctx is not None:
            _l1 = _ctx.create_layout()
            _l1.set_text(_ds1.getText())
        else:
            _l1 = _da.create_pango_layout(_ds1.getText())
        _ds1._formatLayout(gimage, _l1)
        _w1, _h1 = _ds1.getBounds()
        _ds1.setLocation((_dx - (_w1/2.0)), (_dy + _h1 + _off))
        _x1, _y1 = _ds1.getLocation()
        _ds2 = self.getSecondaryDimstring()
        if _ctx is not None:
            _l2 = _ctx.create_layout()
            _l2.set_text(_ds2.getText())
        else:
            _l2 = _da.create_pango_layout(_ds2.getText())
        _ds2._formatLayout(gimage, _l2)
        _w2, _h2 = _ds2.getBounds()
        _ds2.setLocation((_dx - (_w2/2.0)), (_dy - _off))
        _x2, _y2 = _ds2.getLocation()
        _brect = (min(_x1, _x2), # xmin
                  _y1, # ymax
                  max((_x1 + _w1), (_x2 + _w2)), # xmax
                  (_y2 - _h2)) # ymin
    else:
        _ds1 = self.getPrimaryDimstring()
        if _ctx is not None:
            _l1 = _ctx.create_layout()
            _l1.set_text(_ds1.getText())
        else:
            _l1 = _da.create_pango_layout(_ds1.getText())
        _ds1._formatLayout(gimage, _l1)
        _w, _h = _ds1.getBounds()
        _ds1.setLocation((_dx - (_w/2.0)), (_dy + (_h/2.0)))
        _x1, _y1 = _ds1.getLocation()
        _brect = (_x1, _y1, (_x1 + _w), (_y1 - _h))
    _bx1, _by1 = gimage.coordToPixTransform(_brect[0], _brect[1])
    _bx2, _by2 = gimage.coordToPixTransform(_brect[2], _brect[3])
    _pixmap = None
    _bgcol = _image.getOption('BACKGROUND_COLOR') #this is a string not an object
    print "Debug: _bhcol %s"%str(_bgcol)
    if _ctx is not None :
        _r, _g, _b = _bgcol.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        _ctx.rectangle((_bx1 - 2), (_by1 - 2),
                       ((_bx2 - _bx1) + 4), ((_by2 - _by1) + 4))
        _ctx.fill()
    else:
        _gc = gimage.getGC()
        _gc.set_function(gtk.gdk.COPY)
        _gc.set_foreground(gimage.getColor(_bgcol))
        _pixmap = gimage.getPixmap()
        _pixmap.draw_rectangle(_gc, True, (_bx1 - 2), (_by1 - 2),
                               ((_bx2 - _bx1) + 4), ((_by2 - _by1) + 4))
    _col = col
    
    if _col is None:
        _col = _ds1.getColor()
    _px, _py = gimage.coordToPixTransform(_x1, _y1)        
    if _ctx is not None:
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        _ctx.move_to(_px, _py)
        _ctx.show_layout(_l1)
    else:
        _gc.set_foreground(gimage.getColor(_col))
        _px, _py = gimage.coordToPixTransform(_x1, _y1)
        _pixmap.draw_layout(_gc, _px, _py, _l1)
    if _ds2 is not None:
        _col = col
        if _col is None:
            _col = _ds2.getColor()
        if _ctx is not None:
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            _px, _py = gimage.coordToPixTransform(_x2, _y2)
            _ctx.move_to(_px, _py)
            _ctx.show_layout(_l2)
        else:
            _gc.set_foreground(gimage.getColor(_col))
            _px, _py = gimage.coordToPixTransform(_x2, _y2)
            _pixmap.draw_layout(_gc, _px, _py, _l2)
        _col = col
        if _col is None:
            _col = self.getColor()
        _px1, _py1 = gimage.coordToPixTransform(_brect[0], _dy)
        _px2, _py2 = gimage.coordToPixTransform(_brect[2], _dy)
        if _ctx is not None:
            _r, _g, _b = _col.getColors()
            _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            _ctx.move_to(_px1, _py1)
            _ctx.line_to(_px2, _py2)
            _ctx.stroke()
        else:
            _gc.set_foreground(gimage.getColor(_col))                    
            _pixmap.draw_line(_gc, _px1, _py1, _px2, _py2)
        _l2 = None
    _l1 = None
    if _ctx is not None:
        _ctx.restore()

def _cairo_draw_arrow_endpt(ctx, gimage, cpts, mpts):
    #
    # crossbar/crossarc points
    #
    _cx, _cy = cpts[0]
    _cp1x, _cp1y = gimage.coordToPixTransform(_cx, _cy)
    _cx, _cy = cpts[1]
    _cp2x, _cp2y = gimage.coordToPixTransform(_cx, _cy)
    #
    # marker points
    #
    _mp = mpts[0]
    if _mp is not None:
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        ctx.move_to(_px, _py)
        ctx.line_to(_cp1x, _cp1y)
        _mp = mpts[1]
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        ctx.move_to(_px, _py)
        ctx.line_to(_cp1x, _cp1y)
    _mp = mpts[2]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    ctx.move_to(_px, _py)
    ctx.line_to(_cp2x, _cp2y)
    _mp = mpts[3]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    ctx.move_to(_px, _py)
    ctx.line_to(_cp2x, _cp2y)
    ctx.stroke()

def _cairo_draw_filled_arrow_endpt(ctx, gimage, cpts, mpts):
    #
    # crossbar/crossarc points
    #
    _cx, _cy = cpts[0]
    _cp1x, _cp1y = gimage.coordToPixTransform(_cx, _cy)
    _cx, _cy = cpts[1]
    _cp2x, _cp2y = gimage.coordToPixTransform(_cx, _cy)
    #
    # marker points
    #
    _mp = mpts[0]
    if _mp is not None:
        ctx.move_to(_cp1x, _cp1y)
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        ctx.line_to(_px, _py)
        _mp = mpts[1]
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        ctx.line_to(_px, _py)
        ctx.close_path()
        ctx.fill()
    _mp = mpts[2]
    ctx.move_to(_cp2x, _cp2y)
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    ctx.line_to(_px, _py)
    _mp = mpts[3]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    ctx.line_to(_px, _py)
    ctx.close_path()
    ctx.fill()

def _cairo_draw_slash_endpt(ctx, gimage, mpts):
    #
    # marker points
    #
    _mp = mpts[0]
    if _mp is not None:
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        ctx.move_to(_px, _py)
        _mp = mpts[1]
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        ctx.line_to(_px, _py)
    _mp = mpts[2]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    ctx.move_to(_px, _py)
    _mp = mpts[3]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    ctx.line_to(_px, _py)
    ctx.stroke()

def _cairo_draw_circle_endpt(ctx, gimage, cpts, size):
    #
    # crossbar/crossarc points
    #
    _cp = cpts[0]
    if _cp is not None:
        _cp1x, _cp1y = gimage.coordToPixTransform(_cp[0], _cp[1])
    _cx, _cy = cpts[1]
    _cp2x, _cp2y = gimage.coordToPixTransform(_cx, _cy)
    #
    # circle
    #
    _r = size/2.0
    _pw = int(round(_r))#/gimage.getUnitsPerPixel()))
    if _cp is not None:
        ctx.arc(_cp1x, _cp1y, _pw, 0, (2.0 * pi))
        ctx.fill()
    ctx.arc(_cp2x, _cp2y, _pw, 0, (2.0 * pi))
    ctx.fill()

def _gdk_draw_arrow_endpt(gc, gimage, pixmap, cpts, mpts):
    #
    # crossbar/crossarc points
    #
    _cx, _cy = cpts[0]
    _cp1x, _cp1y = gimage.coordToPixTransform(_cx, _cy)
    _cx, _cy = cpts[1]
    _cp2x, _cp2y = gimage.coordToPixTransform(_cx, _cy)
    #
    # marker points
    #
    _segs = []
    _mp = mpts[0]
    if _mp is not None:
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        _segs.append((_px, _py, _cp1x, _cp1y))
        _mp = mpts[1]
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        _segs.append((_px, _py, _cp1x, _cp1y))
    _mp = mpts[2]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    _segs.append((_px, _py, _cp2x, _cp2y))
    _mp = mpts[3]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    _segs.append((_px, _py, _cp2x, _cp2y))
    pixmap.draw_segments(gc, _segs)

def _gdk_draw_filled_arrow_endpt(gc, gimage, pixmap, cpts, mpts):
    #
    # crossbar/crossarc points
    #
    _cx, _cy = cpts[0]
    _cp1x, _cp1y = gimage.coordToPixTransform(_cx, _cy)
    _cx, _cy = cpts[1]
    _cp2x, _cp2y = gimage.coordToPixTransform(_cx, _cy)
    #
    # marker points
    #
    _mp = mpts[0]
    if _mp is not None:
        _p1 = []
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        _p1.append((_px, _py))
        _mp = mpts[1]
        _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
        _p1.append((_px, _py))
        _p1.append((_cp1x, _cp1y))
        pixmap.draw_polygon(gc, True, _p1)
    _p2 = []
    _mp = mpts[2]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    _p2.append((_px, _py))
    _mp = mpts[3]
    _px, _py = gimage.coordToPixTransform(_mp[0], _mp[1])
    _p2.append((_px, _py))
    _p2.append((_cp2x, _cp2y))
    pixmap.draw_polygon(gc, True, _p2)

def _gdk_draw_slash_endpt(gc, gimage, pixmap, mpts):
    #
    # marker points
    #
    _segs = []
    _mp = mpts[0]
    if _mp is not None:
        _px1, _py1 = gimage.coordToPixTransform(_mp[0], _mp[1])
        _mp = mpts[1]
        _px2, _py2 = gimage.coordToPixTransform(_mp[0], _mp[1])
        _segs.append((_px1, _py1, _px2, _py2))
    _mp = mpts[2]
    _px1, _py1 = gimage.coordToPixTransform(_mp[0], _mp[1])
    _mp = mpts[3]
    _px2, _py2 = gimage.coordToPixTransform(_mp[0], _mp[1])
    _segs.append((_px1, _py1, _px2, _py2))
    #
    pixmap.draw_segments(gc, _segs)

def _gdk_draw_circle_endpt(gc, gimage, pixmap, cpts, size):
    #
    # crossbar/crossarc points
    #
    _cp = cpts[0]
    if _cp is not None:
        _cp1x, _cp1y = gimage.coordToPixTransform(_cp[0], _cp[1])
    _cx, _cy = cpts[1]
    _cp2x, _cp2y = gimage.coordToPixTransform(_cx, _cy)
    #
    _r = size/2.0
    _pw = int(round(_r))#/gimage.getUnitsPerPixel()))
    _cw = _ch = _pw * 2
    if _cp is not None:
        _xm = _cp1x - _pw
        _ym = _cp1y - _pw
        pixmap.draw_arc(gc, True, _xm, _ym, _cw, _ch, 0, (360 * 64))
    _xm = _cp2x - _pw
    _ym = _cp2y - _pw
    pixmap.draw_arc(gc, True, _xm, _ym, _cw, _ch, 0, (360 * 64))

    
def _draw_ldim(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _bar1, _bar2 = self.getDimBars()
    _cbar = self.getDimCrossbar()
    if _col is None:
        _col = self.getColor()
    _lw = self.getThickness()#/gimage.getUnitsPerPixel()
    #
    # bars and crossbar coordinates
    #
    _tlist = []
    _ep1, _ep2 = _bar1.getEndpoints()
    _px1, _py1 = gimage.coordToPixTransform(_ep1[0], _ep1[1])
    _px2, _py2 = gimage.coordToPixTransform(_ep2[0], _ep2[1])
    _tlist.append((_px1, _py1, _px2, _py2))
    _ep1, _ep2 = _bar2.getEndpoints()
    _px1, _py1 = gimage.coordToPixTransform(_ep1[0], _ep1[1])
    _px2, _py2 = gimage.coordToPixTransform(_ep2[0], _ep2[1])
    _tlist.append((_px1, _py1, _px2, _py2))
    _ep1, _ep2 = _cbar.getEndpoints()
    _px1, _py1 = gimage.coordToPixTransform(_ep1[0], _ep1[1])
    _px2, _py2 = gimage.coordToPixTransform(_ep2[0], _ep2[1])
    _tlist.append((_px1, _py1, _px2, _py2))
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _lw < 1.0:
            _lw = 1.0
        _ctx.set_line_width(_lw)
        _p1x, _p1y, _p2x, _p2y = _tlist[0]
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _p1x, _p1y, _p2x, _p2y = _tlist[1]
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _p1x, _p1y, _p2x, _p2y = _tlist[2]
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _ctx.stroke()
    else:
        _gc = gimage.getGC()    
        _gc.set_function(gtk.gdk.COPY)
        _gc.set_foreground(gimage.getColor(_col))
        _t = int(round(_lw))
        if _t < 1: # no zero-pixel lines
            _t = 1
        _gc.set_line_attributes(_t, gtk.gdk.LINE_SOLID,
                            gtk.gdk.CAP_BUTT,
                            gtk.gdk.JOIN_MITER)
        _pixmap = gimage.getPixmap()
        _pixmap.draw_segments(_gc, _tlist)    
    #
    # draw endpoints
    #
    _etype = self.getEndpointType()
    if _etype != dimension.Dimension.DIM_ENDPT_NONE:
        _cpts = _cbar.getCrossbarPoints()
        if (_etype == dimension.Dimension.DIM_ENDPT_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_SLASH):
            _mpts = _cbar.getMarkerPoints()
            if _etype == dimension.Dimension.DIM_ENDPT_ARROW:
                if _ctx is not None:
                    _cairo_draw_arrow_endpt(_ctx, gimage, _cpts, _mpts)
                else:
                    _gdk_draw_arrow_endpt(_gc, gimage, _pixmap, _cpts, _mpts)
            elif _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW:
                if _ctx is not None:
                    _cairo_draw_filled_arrow_endpt(_ctx, gimage, _cpts, _mpts)
                else:
                    _gdk_draw_filled_arrow_endpt(_gc, gimage, _pixmap,
                                                 _cpts, _mpts)
            elif _etype == dimension.Dimension.DIM_ENDPT_SLASH:
                if _ctx is not None:
                    _cairo_draw_slash_endpt(_ctx, gimage, _mpts)
                else:
                    _gdk_draw_slash_endpt(_gc, gimage, _pixmap, _mpts)
            else:
                raise ValueError, "Unexpected end point type: %d" % _etype
        elif _etype == dimension.Dimension.DIM_ENDPT_CIRCLE:
            _size = self.getEndpointSize()
            if _ctx is not None:
                _cairo_draw_circle_endpt(_ctx, gimage, _cpts, _size)
            else:
                _gdk_draw_circle_endpt(_gc, gimage, _pixmap, _cpts, _size)
        else:
            raise ValueError, "Unexpected endpoint value: %d" % _etype
    self._drawDimStrings(gimage, col)
    if _ctx is not None:
        _ctx.restore()

def _draw_rdim(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    if _col is None:
        _col = self.getColor()
    _lw = self.getThickness()#/gimage.getUnitsPerPixel()
    #
    # Dimension bar
    #
    _cbar = self.getDimCrossbar()
    _ep1, _ep2 = _cbar.getEndpoints()
    _p1x, _p1y = gimage.coordToPixTransform(_ep1[0], _ep1[1])
    _p2x, _p2y = gimage.coordToPixTransform(_ep2[0], _ep2[1])
    _tlist = []
    _tlist.append((_p1x, _p1y, _p2x, _p2y))
    _dx, _dy = self.getLocation()
    _pdx, _pdy = gimage.coordToPixTransform(_dx, _dy)
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _lw < 1.0:
            _lw = 1.0
        _ctx.set_line_width(_lw)
        _p1x, _p1y, _p2x, _p2y = _tlist[0]
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _ctx.stroke()
    else:
        _gc = gimage.getGC()
        _gc.set_function(gtk.gdk.COPY)
        _gc.set_foreground(gimage.getColor(_col))
        _t = int(round(_lw))
        if _t < 1: # no zero-pixel lines
            _t = 1
        _gc.set_line_attributes(_t, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT,
                                gtk.gdk.JOIN_MITER)
        gimage.getPixmap().draw_segments(_gc, _tlist)
    #
    # draw marker points
    #
    _etype = self.getEndpointType()
    if _etype != dimension.Dimension.DIM_ENDPT_NONE:
        _cpts = _cbar.getCrossbarPoints()
        _dia_mode = self.getDiaMode()
        if (_etype == dimension.Dimension.DIM_ENDPT_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_SLASH):
            _mpts = _cbar.getMarkerPoints()
            if _etype == dimension.Dimension.DIM_ENDPT_ARROW:
                if _dia_mode:
                    _mpts[0] = None
                if _ctx is not None:
                    _cairo_draw_arrow_endpt(_ctx, gimage, _cpts, _mpts)
                else:
                    _gdk_draw_arrow_endpt(_gc, gimage, _pixmap, _cpts, _mpts)
            elif _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW:
                if _dia_mode:
                    _mpts[0] = None
                if _ctx is not None:
                    _cairo_draw_filled_arrow_endpt(_ctx, gimage, _cpts, _mpts)
                else:
                    _gdk_draw_filled_arrow_endpt(_gc, gimage, _pixmap,
                                                 _cpts, _mpts)
            elif _etype == dimension.Dimension.DIM_ENDPT_SLASH:
                if _dia_mode:
                    _mpts[0] = None
                if _ctx is not None:
                    _cairo_draw_slash_endpt(_ctx, gimage, _mpts)
                else:
                    _gdk_draw_slash_endpt(_gc, gimage, _pixmap, _mpts)
            else:
                raise ValueError, "Unexpected end point type: %d" % _etype
        elif _etype == dimension.Dimension.DIM_ENDPT_CIRCLE:
            _size = self.getEndpointSize()
            if _dia_mode:
                _cpts[0] = None
            if _ctx is not None:
                _cairo_draw_circle_endpt(_ctx, gimage, _cpts, _size)
            else:
                _gdk_draw_circle_endpt(gc, gimage, _pixmap, _cpts, _size)
        else:
            raise ValueError, "Unexpected endpoint value: %d" % _etype
    self._drawDimStrings(gimage, col)
    if _ctx is not None:
        _ctx.restore()

def _draw_adim(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _bar1, _bar2 = self.getDimBars()
    _carc = self.getDimCrossarc()
    if _col is None:
        _col = self.getColor()
    _lw = self.getThickness()#/gimage.getUnitsPerPixel()
    _sa = _carc.getStartAngle()
    _ea = _carc.getEndAngle()
    _vx, _vy = self.getVertexPoint().getCoords()
    _pvx, _pvy = gimage.coordToPixTransform(_vx, _vy)
    _dx, _dy = self.getLocation()
    _pdx, _pdy = gimage.coordToPixTransform(_dx, _dy)
    _pr = int(_carc.getRadius())#/gimage.getUnitsPerPixel())
    #
    # bars and crossarc coords
    #
    _tlist = []
    _ep1, _ep2 = _bar1.getEndpoints()        
    _p1x, _p1y = gimage.coordToPixTransform(_ep1[0], _ep1[1])
    _p2x, _p2y = gimage.coordToPixTransform(_ep2[0], _ep2[1])
    _tlist.append((_p1x, _p1y, _p2x, _p2y))
    _ep1, _ep2 = _bar2.getEndpoints()
    _p1x, _p1y = gimage.coordToPixTransform(_ep1[0], _ep1[1])
    _p2x, _p2y = gimage.coordToPixTransform(_ep2[0], _ep2[1])
    _tlist.append((_p1x, _p1y, _p2x, _p2y))
    _ctx = gimage.getCairoContext()
    if _ctx is not None:
        _ctx.save()
        _r, _g, _b = _col.getColors()
        _ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        if _lw < 1.0:
            _lw = 1.0
        _ctx.set_line_width(_lw)
        #
        # arc drawing relies on Cairo transformations
        #
        _ctx.scale(1.0, -1.0)
        _ctx.translate(_pvx, -(_pvy))
        _ctx.arc(0, 0, _pr, (_sa * _dtr), (_ea * _dtr))
        _ctx.identity_matrix()
        #
        _p1x, _p1y, _p2x, _p2y = _tlist[0]
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _p1x, _p1y, _p2x, _p2y = _tlist[1]
        _ctx.move_to(_p1x, _p1y)
        _ctx.line_to(_p2x, _p2y)
        _ctx.stroke()
    else:
        _gc = gimage.getGC()
        _gc.set_function(gtk.gdk.COPY)
        _gc.set_foreground(gimage.getColor(_col))
        _t = int(round(_lw))
        if _t < 1: # no zero-pixel lines
            _t = 1
        _gc.set_line_attributes(_t, gtk.gdk.LINE_SOLID,
                                gtk.gdk.CAP_BUTT,
                                gtk.gdk.JOIN_MITER)
        _pixmap = gimage.getPixmap()
        _pixmap.draw_segments(_gc, _tlist)        
        _pxmin = _pvx - _pr
        _pymin = _pvy - _pr
        _cw = _ch = _pr * 2
        if _sa < _ea:
            _sweep = _ea - _sa
        else:
            _sweep = 360.0 - (_sa - _ea)
        _pixmap.draw_arc(_gc, False, _pxmin, _pymin, _cw, _ch,
                         int(_sa * 64), int(_sweep * 64))
    #
    # draw endpoints
    #
    _etype = self.getEndpointType()
    if _etype != dimension.Dimension.DIM_ENDPT_NONE:
        _cpts = _carc.getCrossbarPoints()
        if (_etype == dimension.Dimension.DIM_ENDPT_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW or
            _etype == dimension.Dimension.DIM_ENDPT_SLASH):
            _mpts = _carc.getMarkerPoints()
            if _etype == dimension.Dimension.DIM_ENDPT_ARROW:
                if _ctx is not None:
                    _cairo_draw_arrow_endpt(_ctx, gimage, _cpts, _mpts)
                else:
                    _gdk_draw_arrow_endpt(_gc, gimage, _pixmap, _cpts, _mpts)
            elif _etype == dimension.Dimension.DIM_ENDPT_FILLED_ARROW:
                if _ctx is not None:
                    _cairo_draw_filled_arrow_endpt(_ctx, gimage, _cpts, _mpts)
                else:
                    _gdk_draw_filled_arrow_endpt(_gc, gimage, _pixmap,
                                                 _cpts, _mpts)
            elif _etype == dimension.Dimension.DIM_ENDPT_SLASH:
                if _ctx is not None:
                    _cairo_draw_slash_endpt(_ctx, gimage, _mpts)
                else:
                    _gdk_draw_slash_endpt(_gc, gimage, _pixmap, _mpts)
            else:
                raise ValueError, "Unexpected end point type: %d" % _etype
        elif _etype == dimension.Dimension.DIM_ENDPT_CIRCLE:
            _size = self.getEndpointSize()
            if _ctx is not None:
                _cairo_draw_circle_endpt(_ctx, gimage, _cpts, _size)
            else:
                _gdk_draw_circle_endpt(gc, gimage, _pixmap, _cpts, _size)
        else:
            raise ValueError, "Unexpected endpoint value: %d" % _etype
    self._drawDimStrings(gimage, col)
    if _ctx is not None:
        _ctx.restore()

def _erase_dim(self, gimage):
    pass 
    # originally the erase_dim set the color of the dimansion equal to the background color
    #for deleting the dimansion.
    #but when we close the application we get an error 
    #Adding pass to the erese_dim functions we not have any problems
    #self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

def _draw_layer(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _image = gimage.getImage()
    if _col is None:
        if self.isVisible() and _image.getActiveLayer() is not self:
            _col = _image.getOption('INACTIVE_LAYER_COLOR')
        else:
            _col = _image.getOption('BACKGROUND_COLOR')
    for _obj in self.getLayerEntities('point'):
        if _obj.isVisible():
            _obj.draw(gimage, _col)
    _ctypes = ['hcline', 'vcline', 'acline', 'cline', 'ccircle']
    for _ctype in _ctypes:
        for _obj in self.getLayerEntities(_ctype):
            if _obj.isVisible():
                _obj.draw(gimage, _col)
    _gtypes = ['segment', 'circle', 'arc', 'leader', 'polyline',
               'chamfer', 'fillet', 'textblock', 'linear_dimension',
               'horizontal_dimension', 'vertical_dimension',
               'radial_dimension', 'angular_dimension']
    for _gtype in _gtypes:
        for _obj in self.getLayerEntities(_gtype):
            if _obj.isVisible():
                _obj.draw(gimage, _col)
            
def _erase_layer(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
    for _pt in self.getLayerEntities('point'):
        _pt.erase(gimage)
    
def add_graphic_methods():
    _class = point.Point
    _class.draw = types.MethodType(_draw_point, None, _class)
    _class.erase = types.MethodType(_erase_point, None, _class)
    _class = segment.Segment
    _class.draw = types.MethodType(_draw_segment, None, _class)
    _class.erase = types.MethodType(_erase_segment, None, _class)
    _class = circle.Circle
    _class.draw = types.MethodType(_draw_circle, None, _class)
    _class.erase = types.MethodType(_erase_circle, None, _class)
    _class = arc.Arc
    _class.draw = types.MethodType(_draw_arc, None, _class)
    _class.erase = types.MethodType(_erase_arc, None, _class)
    _class = leader.Leader
    _class.draw = types.MethodType(_draw_leader, None, _class)
    _class.erase = types.MethodType(_erase_leader, None, _class)
    _class = polyline.Polyline
    _class.draw = types.MethodType(_draw_polyline, None, _class)
    _class.erase = types.MethodType(_erase_polyline, None, _class)
    _class = segjoint.Chamfer
    _class.draw = types.MethodType(_draw_chamfer, None, _class)
    _class.erase = types.MethodType(_erase_chamfer, None, _class)
    _class = segjoint.Fillet
    _class.draw = types.MethodType(_draw_fillet, None, _class)
    _class.erase = types.MethodType(_erase_fillet, None, _class)
    _class = hcline.HCLine
    _class.draw = types.MethodType(_draw_hcline, None, _class)
    _class.erase = types.MethodType(_erase_hcline, None, _class)
    _class = vcline.VCLine
    _class.draw = types.MethodType(_draw_vcline, None, _class)
    _class.erase = types.MethodType(_erase_vcline, None, _class)
    _class = acline.ACLine
    _class.draw = types.MethodType(_draw_acline, None, _class)
    _class.erase = types.MethodType(_erase_acline, None, _class)
    _class = cline.CLine
    _class.draw = types.MethodType(_draw_cline, None, _class)
    _class.erase = types.MethodType(_erase_cline, None, _class)
    _class = ccircle.CCircle
    _class.draw = types.MethodType(_draw_ccircle, None, _class)
    _class.erase = types.MethodType(_erase_ccircle, None, _class)
    _class = text.TextBlock
    _class._formatLayout = types.MethodType(_format_layout, None, _class)
    _class.draw = types.MethodType(_draw_textblock, None, _class)
    _class.erase = types.MethodType(_erase_textblock, None, _class)
    _class = dimension.LinearDimension
    _class.draw = types.MethodType(_draw_ldim, None, _class)
    _class = dimension.RadialDimension
    _class.draw = types.MethodType(_draw_rdim, None, _class)
    _class = dimension.AngularDimension
    _class.draw = types.MethodType(_draw_adim, None, _class)
    _class = dimension.Dimension
    _class.erase = types.MethodType(_erase_dim, None, _class)
    _class._drawDimStrings = types.MethodType(_draw_dimstrings, None, _class)
    _class = layer.Layer
    _class.draw = types.MethodType(_draw_layer, None, _class)
    _class.erase = types.MethodType(_erase_layer, None, _class)
