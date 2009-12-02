#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo
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
# <radial Dimension > command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic.dimension import Dimension
from PythonCAD.Generic import snap

from PythonCAD.Interface.Gtk import gtktext
from PythonCAD.Interface.Command.cmdCommon import * 
#
# Init
#
def radial_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on an arc or a circle to dimension.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", radial_mode_init)
    _tool.setHandler("button_press", radial_button_press_cb)
#
# Motion Notifie
#
def radial_txt_motion_notify_cb(gtkimage, widget, event, tool):
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _rdim = tool.getDimension()
    _crossbar = _rdim.getDimCrossbar()
    _cp = tool.getCurrentPoint()
    _segs = []
    if _cp is not None:
        _p1, _p2 = _crossbar.getEndpoints()
        _p0x, _p0y = gtkimage.coordToPixTransform(_p1[0], _p1[1])
        _p1x, _p1y = gtkimage.coordToPixTransform(_p2[0], _p2[1])
        _segs.append((_p0x, _p0y, _p1x, _p1y))
    tool.setCurrentPoint(_x, _y)
    _ix, _iy = gtkimage.image.getCurrentPoint()
    _rdim.setLocation(_ix, _iy)
    _rdim.calcDimValues(False)
    _p1, _p2 = _crossbar.getEndpoints()
    _p0x, _p0y = gtkimage.coordToPixTransform(_p1[0], _p1[1])
    _p1x, _p1y = gtkimage.coordToPixTransform(_p2[0], _p2[1])
    _segs.append((_p0x, _p0y, _p1x, _p1y))
    widget.window.draw_segments(_gc, _segs)
    return True
#
# Button press callBacks
#
def radial_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _dc = None
    _layers = [_image.getTopLayer()]
    while(len(_layers)):
        _layer = _layers.pop()
        if _layer.isVisible():
            _cobjs = (_layer.getLayerEntities("circle") +
                      _layer.getLayerEntities("arc"))
            for _cobj in _cobjs:
                _mp = _cobj.mapCoords(_x, _y, _tol)
                if _mp is not None:
                    _dc = _cobj
                    break
        _layers.extend(_layer.getSublayers())
    if _dc is not None:
        _x, _y = _mp
        tool.setDimObject(_dc)
        tool.setDimPosition(_x, _y)
        tool.makeDimension(_image)
        tool.setHandler("motion_notify", radial_txt_motion_notify_cb)
        tool.setHandler("button_press", radial_text_button_press_cb)
        gtkimage.setPrompt(_('Click where the dimension text should be placed.'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True
#
# Entry callBacks
#
def radial_text_button_press_cb(gtkimage, widget, event, tool):
    _x, _y = gtkimage.image.getCurrentPoint()
    _rdim = tool.getDimension()
    _rdim.setLocation(_x, _y)
    _rdim.calcDimValues()
    _rdim.reset()
    add_dimension(gtkimage)
    return True
#
# Suport functions
#