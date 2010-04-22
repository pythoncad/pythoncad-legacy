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
# Circle command functions/Class 
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
def circle_center_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("button_press", circle_center_button_press_cb)
    _tool.setHandler("entry_event", circle_point_entry_event_cb)
    _tool.setHandler("initialize", circle_center_mode_init)
    
#
# Motion Notifie
#---------------------------------------------------------------------------------------------------
def circle_center_motion_notify_cb(gtkimage, widget, event, tool):
    cx, cy = tool.getCenter().point.getCoords()
    x, y = gtkimage.image.getCurrentPoint().getCoords()
    radius = math.hypot((cx - x), (cy - y))
    tool.setRadius(radius)
    # sample tool
    gtkimage.viewport.sample(tool)    
    return True        

#
# Button press callBacks
#---------------------------------------------------------------------------------------------------
def circle_radius_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    snap.setSnap(_image,tool.setRadiusPoint,_tol)
    _x,_y=tool.radiusPoint.point.getCoords()
    _cx,_cy=tool.getCenter().point.getCoords()
    _radius = math.hypot((_cx - _x), (_cy - _y))
    tool.setRadius(_radius)    
    cmdCommon.create_entity(gtkimage)
    return True

#---------------------------------------------------------------------------------------------------
def circle_center_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setCenter,_tol,_snapArray)
    tool.setHandler("button_press", circle_radius_button_press_cb)
    tool.setHandler("motion_notify", circle_center_motion_notify_cb)
    tool.setHandler("entry_event", circle_radius_entry_event_cb)
    gtkimage.setPrompt(_('Enter the radius or click in the drawing area'))
    return True

#
# Entry callBacks
#---------------------------------------------------------------------------------------------------
def circle_radius_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _r = util.get_float(eval(_text, gtkimage.image.getImageVariables()))
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        tool.setRadius(_r)
        cmdCommon.create_entity(gtkimage)

#---------------------------------------------------------------------------------------------------        
def circle_point_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setCenter(_x, _y)
        tool.setHandler("button_press", circle_radius_button_press_cb)
        tool.setHandler("motion_notify", circle_center_motion_notify_cb)
        tool.setHandler("entry_event", circle_radius_entry_event_cb)
        gtkimage.setPrompt(_('Enter the radius or click in the drawing area'))
##        gtkimage.getGC().set_function(gtk.gdk.INVERT)
        #stop snap object
        stopOneShutSnap(gtkimage) 
#
# Suport functions
#




