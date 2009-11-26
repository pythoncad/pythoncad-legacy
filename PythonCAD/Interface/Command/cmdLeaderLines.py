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

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
#
# Init
#
def leader_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area to enter the first point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", leader_mode_init)
    _tool.setHandler("button_press", leader_first_button_press_cb)
#
# Motion Notifie
#
def leader_second_motion_notify_cb(gtkimage, widget, event, tool):
    _segs = []
    _x2, _y2 = tool.getMidPoint().point.getCoords()
    _px2, _py2 = gtkimage.coordToPixTransform(_x2, _y2)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _segs.append((_px2, _py2, _xc, _yc))
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px2, _py2, _x, _y))
    widget.window.draw_segments(_gc, _segs)
    return True

def leader_first_motion_notify_cb(gtkimage, widget, event, tool):
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
    tool.setCurrentPoint(_x, _y)
    _segs.append((_px1, _py1, _x, _y))
    widget.window.draw_segments(_gc, _segs)
#
# Button press callBacks
#
def leader_final_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setFinalPoint,_tol,_snapArray)
    cmdCommon.create_entity(gtkimage)
    gtkimage.setPrompt(_('Click in the drawing area to place the initial point'))
    return True

def leader_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setMidPoint,_tol,_snapArray)
    tool.clearCurrentPoint()
    tool.setHandler("motion_notify", leader_second_motion_notify_cb)
    tool.setHandler("button_press", leader_final_button_press_cb)
    gtkimage.setPrompt(_('Click in the drawing area to place the final point'))
    return True

def leader_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setFirstPoint,_tol,_snapArray)
    tool.setHandler("motion_notify", leader_first_motion_notify_cb)
    tool.setHandler("button_press", leader_second_button_press_cb)
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    gtkimage.setPrompt(_('Click in the drawing area to place the second point'))
    return True
#
# Entry callBacks
#

#
# Suport functions
#