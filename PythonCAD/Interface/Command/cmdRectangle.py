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
# Rectangle command functions/Class 
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
def rectangle_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", rectangle_mode_init)
    _tool.setHandler("button_press", rectangle_first_button_press_cb)
    _tool.setHandler("entry_event", rectangle_first_entry_event_cb)
#
# Motion Notifie
#
def rectangle_motion_notify_cb(gtkimage, widget, event, tool):
    _x1, _y1 = tool.getFirstPoint().point.getCoords()
    _px, _py = gtkimage.coordToPixTransform(_x1, _y1)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _xmin = min(_px, _xc)
        _ymin = min(_py, _yc)
        _width = abs(_px - _xc)
        _height = abs(_py - _yc)
        widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _width, _height)
    tool.setCurrentPoint(_x, _y)
    _xmin = min(_px, _x)
    _ymin = min(_py, _y)
    _width = abs(_px - _x)
    _height = abs(_py - _y)
    widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _width, _height)
    return True
#
# Button press callBacks
#
def rectangle_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    snap.setSnap(_image,tool.setSecondPoint,_tol)
    cmdCommon.create_entity(gtkimage)
    return True

def rectangle_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    snap.setSnap(_image,tool.setFirstPoint,_tol)
    tool.setHandler("button_press", rectangle_second_button_press_cb)
    tool.setHandler("motion_notify", rectangle_motion_notify_cb)
    tool.setHandler("entry_event", rectangle_second_entry_event_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True
#
# Entry call back
#
def rectangle_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondPoint(_x, _y)
        cmdCommon.create_entity(gtkimage)

def rectangle_first_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("button_press", rectangle_second_button_press_cb)
        tool.setHandler("entry_event", rectangle_second_entry_event_cb)
        tool.setHandler("motion_notify", rectangle_motion_notify_cb)
        gtkimage.setPrompt(_('Enter the second Point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
#
# Suport functions
#






