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
# <polygons> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
#
# Init
#
def polygon_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area to define the center'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", polygon_mode_init)
    _tool.setHandler("entry_event", polygon_center_entry_event_cb)
    _tool.setHandler("button_press", polygon_center_button_press_cb)
#
# Motion Notifie
#
def polygon_radius_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    _count = tool.getSideCount()
    if _cp is not None:
        _tx0, _ty0 = tool.getCoord(0)
        _px0, _py0 = gtkimage.coordToPixTransform(_tx0, _ty0)
        _px1 = _px0
        _py1 = _py0
        for _i in range(1, _count):
            _txi, _tyi = tool.getCoord(_i)
            _pxi, _pyi = gtkimage.coordToPixTransform(_txi, _tyi)
            _segs.append((_px1, _py1, _pxi, _pyi))
            _px1 = _pxi
            _py1 = _pyi
        _segs.append((_px1, _py1, _px0, _py0))
    tool.setCurrentPoint(_x, _y)
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setDinamicSnap(gtkimage,tool.setLocation,_snapArray)
    _tx0, _ty0 = tool.getCoord(0)
    _px0, _py0 = gtkimage.coordToPixTransform(_tx0, _ty0)
    _px1 = _px0
    _py1 = _py0
    for _i in range(1, _count):
        _txi, _tyi = tool.getCoord(_i)
        _pxi, _pyi = gtkimage.coordToPixTransform(_txi, _tyi)
        _segs.append((_px1, _py1, _pxi, _pyi))
        _px1 = _pxi
        _py1 = _pyi
    _segs.append((_px1, _py1, _px0, _py0))
    widget.window.draw_segments(_gc, _segs)
    return True
#
# Button press callBacks
#
def polygon_radius_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setLocation,_tol,_snapArray)
    cmdCommon.create_entity(gtkimage)
    return True

def polygon_center_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setCenter,_tol,_snapArray)
    tool.setHandler("motion_notify", polygon_radius_motion_notify_cb)
    tool.setHandler("button_press", polygon_radius_button_press_cb)
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    gtkimage.setPrompt(_('Click in the drawing area to place the second point'))
    return True
#
# Entry callBacks
#
def polygon_center_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setCenter(_x, _y)
        tool.setHandler("motion_notify", polygon_radius_motion_notify_cb)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)        
        tool.setHandler("button_press", polygon_radius_button_press_cb)
        tool.delHandler("entry_event") # ???
        gtkimage.setPrompt(_('Click in the drawing area to draw the polygon'))
#
# Suport functions
#