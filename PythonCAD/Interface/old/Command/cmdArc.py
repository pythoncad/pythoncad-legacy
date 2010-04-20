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
# <arc> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk
import math

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon

#
# Init
#---------------------------------------------------------------------------------------------------
def arc_center_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", arc_center_button_press_cb)
    _tool.setHandler("entry_event", arc_center_entry_event_cb)
    _tool.setHandler("initialize", arc_center_mode_init)
    
#
# Motion Notify
#---------------------------------------------------------------------------------------------------
def arc_angle_motion_notify_cb(gtkimage, widget, event, tool):
    cx, cy = tool.getCenter().point.getCoords()
    x, y = gtkimage.image.getCurrentPoint().getCoords()
    end_angle = (180.0 / math.pi) * math.atan2((y - cy), (x - cx))
    tool.setEndAngle(end_angle)
    # sample tool
    gtkimage.viewport.sample(tool)    
    return True

#---------------------------------------------------------------------------------------------------
def arc_radius_motion_notify_cb(gtkimage, widget, event, tool):
    cx, cy = tool.getCenter().point.getCoords()
    x, y = gtkimage.image.getCurrentPoint().getCoords()
    radius = math.hypot((cx - x), (cy - y))
    tool.setRadius(radius)
    tool.setStartAngle(0)
    tool.setEndAngle(360)
    # sample tool
    gtkimage.viewport.sample(tool)      
    return True

#
# Button press callBacks
#
#---------------------------------------------------------------------------------------------------
def arc_center_end_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray = { 'perpendicular':False, 'tangent':False }
    _snp = snap.getSnapPoint(_image,_tol,_snapArray)
    _x,_y = _snp.point.getCoords()
    _cx, _cy = tool.getCenter().point.getCoords()
    _angle = (180.0/math.pi) * math.atan2((_y - _cy),(_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setEndAngle(_angle)
    cmdCommon.create_entity(gtkimage)
    return True

#---------------------------------------------------------------------------------------------------
def arc_center_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setCenter,_tol,_snapArray)
    tool.setHandler("motion_notify", arc_radius_motion_notify_cb)
    tool.setHandler("entry_event", arc_center_radius_entry_cb)
    tool.setHandler("button_press", arc_center_radius_button_press_cb)
    gtkimage.setPrompt(_('Enter the radius or click in the drawing area'))
    return True

#---------------------------------------------------------------------------------------------------
def arc_center_radius_button_press_cb(gtkimage, widget, event, tool):
    _cx, _cy = tool.getCenter().point.getCoords()
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _snp=snap.getSnapPoint(_image,_tol,_snapArray)
    _x,_y=_snp.point.getCoords()
    _radius = math.hypot((_x - _cx), (_y - _cy))
    tool.setRadius(_radius)
    _angle = (180.0/math.pi) * math.atan2((_y - _cy), (_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setStartAngle(_angle)
    tool.delHandler("entry_event")
    tool.setHandler("motion_notify", arc_angle_motion_notify_cb)
    tool.setHandler("button_press", arc_center_end_button_press_cb)
    gtkimage.setPrompt(_('Click in the drawing area to finish the arc'))
    return True

#---------------------------------------------------------------------------------------------------
def arc_start_angle_button_press_cb(gtkimage, widget, event, tool):
    _cx, _cy = tool.getCenter()
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _snp=snap.getSnapPoint(_image,_tol,_snapArray)
    _x,_y=_snp.point.getCoords()
    _angle = (180.0/math.pi) * math.atan2((_y - _cy), (_x - _cx))
    if _angle < 0.0:
        _angle = _angle + 360.0
    tool.setStartAngle(_angle)
    tool.setHandler("motion_notify", arc_angle_motion_notify_cb)
    tool.setHandler("entry_event", arc_center_ea_entry_event_cb)
    gtkimage.setPrompt(_('Enter the end angle of the arc.'))
    return True

#
# Entry callBacks
#
#---------------------------------------------------------------------------------------------------
def arc_center_ea_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = util.make_c_angle(eval(_text, gtkimage.image.getImageVariables()))
        tool.setEndAngle(_angle)
        cmdCommon.create_entity(gtkimage)

#---------------------------------------------------------------------------------------------------
def arc_center_sa_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = util.make_c_angle(eval(_text, gtkimage.image.getImageVariables()))
        tool.setStartAngle(_angle)
        tool.setHandler("motion_notify", arc_angle_motion_notify_cb)
        tool.setHandler("entry_event", arc_center_ea_entry_event_cb)
        gtkimage.setPrompt(_('Enter the end angle of the arc.'))
        
#---------------------------------------------------------------------------------------------------
def arc_center_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setCenter(_x, _y)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)
        tool.setHandler("motion_notify", arc_radius_motion_notify_cb)
        tool.setHandler("button_press", arc_center_radius_button_press_cb)
        tool.setHandler("entry_event", arc_center_radius_entry_cb)
        gtkimage.setPrompt(_('Enter the arc radius or click in the drawing area'))

#---------------------------------------------------------------------------------------------------
def arc_center_radius_entry_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _r = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        tool.setRadius(_r)
        tool.setHandler("entry_event", arc_center_sa_entry_event_cb)
        tool.setHandler("button_press", arc_start_angle_button_press_cb)
        gtkimage.setPrompt(_('Enter the start angle of the arc.'))

#
# Suport functions
#