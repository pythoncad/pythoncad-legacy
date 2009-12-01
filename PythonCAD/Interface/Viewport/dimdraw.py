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

#----------------------------------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------------------------
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

    
#----------------------------------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------------------------
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

#----------------------------------------------------------------------------------------------------
def _erase_dim(self, gimage):
    pass 
    # originally the erase_dim set the color of the dimansion equal to the background color
    #for deleting the dimansion.
    #but when we close the application we get an error 
    #Adding pass to the erese_dim functions we not have any problems
    #self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

