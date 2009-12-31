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
# <> command functions/Class 
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
def circle_tp_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", circle_tp_first_button_press_cb)
    _tool.setHandler("entry_event", circle_tp_first_entry_event_cb)
    _tool.setHandler("initialize", circle_tp_mode_init)
#
# Motion Notifie
#
def circle_tp_motion_notify_cb(gtkimage, widget, event, tool):
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _radius = tool.getRadius()
    _upp = gtkimage.getUnitsPerPixel()
    if _radius is not None:
        _cx, _cy = tool.getCenter().point.getCoords()
        _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
        _pr = int(_radius/_upp)
        _xmin = _pcx - _pr
        _ymin = _pcy - _pr
        _cw = _ch = _pr * 2
        widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,0, 360*64)
    snap.setDinamicSnap(gtkimage,tool.setSecondPoint,None)
    _cx, _cy = tool.getCenter().point.getCoords()
    _pcx, _pcy = gtkimage.coordToPixTransform(_cx, _cy)
    _radius = tool.getRadius()
    _pr = int(_radius/_upp)
    _xmin = _pcx - _pr
    _ymin = _pcy - _pr
    _cw = _ch = _pr * 2
    widget.window.draw_arc(_gc, False, _xmin, _ymin, _cw, _ch,0, 360*64)
    return True
#
# Button press callBacks
#
def circle_tp_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    #todo imlement the tangent snap for the two point circle
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setFirstPoint,_tol,_snapArray)
    tool.setHandler("button_press", circle_tp_second_button_press_cb)
    tool.setHandler("motion_notify", circle_tp_motion_notify_cb)
    tool.setHandler("entry_event", circle_tp_second_entry_event_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def circle_tp_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    #todo imlement the tangent snap for the two point circle
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setSecondPoint,_tol,_snapArray)
    cmdCommon.create_entity(gtkimage)
    return True

#
# Entry callBacks
#
def circle_tp_first_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("motion_notify", circle_tp_motion_notify_cb)
        tool.setHandler("entry_event", circle_tp_second_entry_event_cb)
        gtkimage.setPrompt(_('Enter another point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def circle_tp_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondPoint(_x, _y)
        cmdCommon.create_entity(gtkimage)
#
# Suport functions
#