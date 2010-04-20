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

from math import hypot, pi, atan2

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
#
# Init
#
def cline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a Point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", cline_mode_init)
    _tool.setHandler("button_press", cline_first_button_press_cb)
    _tool.setHandler("entry_event", cline_first_entry_make_pt)
#
# Motion Notifie
#
def cline_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _x1, _y1 = tool.getFirstPoint().point.getCoords()
    _px1, _py1 = gtkimage.coordToPixTransform(_x1, _y1)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px1, _py1, _xc, _yc))
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setDinamicSnap(gtkimage,tool.setSecondPoint,_snapArray)
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px1, _py1, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True
#
# Button press callBacks
#
def cline_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setFirstPoint,_tol,_snapArray)
    tool.setHandler("button_press", cline_second_button_press_cb)
    tool.setHandler("entry_event", cline_second_entry_make_pt)
    tool.setHandler("motion_notify", cline_motion_notify_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True

def cline_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setSecondPoint,_tol,_snapArray)
    cmdCommon.create_entity(gtkimage)
    return True
#
# Entry callBacks
#
def cline_first_entry_make_pt(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstPoint(_x, _y)
        tool.setHandler("button_press", cline_second_button_press_cb)
        tool.setHandler("motion_notify", cline_motion_notify_cb)
        tool.setHandler("entry_event", cline_second_entry_make_pt)
        gtkimage.setPrompt(_('Enter the second Point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
def cline_second_entry_make_pt(gtkimage, widget, tool):
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

#
# two point construction line
#












