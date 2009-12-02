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

        
#----------------------------------------------------------------------------------------------------
def _draw_textblock(self, gimage, col=None):
    if not isinstance(gimage, gtkimage.GTKImage):
        raise TypeError, "Invalid GTKImage: " + `type(gimage)`
    _col = col
    if _col is not None and not isinstance(_col, color.Color):
        raise TypeError, "Invalid Color: " + `type(_col)`
    _text = self.getText()
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
    
#----------------------------------------------------------------------------------------------------
def _erase_textblock(self, gimage):
    self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))
