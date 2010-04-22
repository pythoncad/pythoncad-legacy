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
# <angle construction lines> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic.point import Point
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon

#
# Init
#
#---------------------------------------------------------------------------------------------------
def acline_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a Point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", acline_mode_init)
    _tool.setHandler("button_press", acline_first_button_press_cb)
    _tool.setHandler("entry_event", acline_entry_make_pt)
    
#
# Motion Notify
#
#---------------------------------------------------------------------------------------------------
def acline_motion_notify_cb(gtkimage, widget, event, tool):
    # first point of segement
    #p1 = tool.getFirstPoint().point
    # current pointer position
    p2 = gtkimage.getImage().getCurrentPoint()
    # manage horizontal vertical angle forced
##    p = tool.transformCoords(p1, p2)
    # set snap
    _snapArray = { 'perpendicular':False, 'tangent':False }
    snap.setDinamicSnap(gtkimage, tool.setLocation, _snapArray)
    # update point
    tool.setCurrentPoint(p2)
    # sample tool
    gtkimage.viewport.sample(tool)
    return True

#
# Button press callBacks
#
#---------------------------------------------------------------------------------------------------
def acline_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setPoint,_tol,_snapArray)
    tool.setHandler("button_press", acline_second_button_press_cb)
    tool.setHandler("entry_event", acline_entry_make_angle)
    tool.setHandler("motion_notify", acline_motion_notify_cb)
    gtkimage.setPrompt(_('Enter the angle or click in the drawing area'))
    return True

#---------------------------------------------------------------------------------------------------
def acline_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    snap.setSnap(_image,tool.setLocation,_tol,_snapArray)
    cmdCommon.create_entity(gtkimage)
    return True

#
# Entry callBacks
#
#---------------------------------------------------------------------------------------------------
def acline_entry_make_angle(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _angle = util.make_angle(eval(_text, gtkimage.image.getImageVariables()))
        tool.setAngle(_angle)
        cmdCommon.create_entity(gtkimage)
        
#---------------------------------------------------------------------------------------------------
def acline_entry_make_pt(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0, -1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setPoint(_x, _y)
        tool.setHandler("button_press", acline_second_button_press_cb)
        tool.setHandler("entry_event", acline_entry_make_angle)
        tool.setHandler("motion_notify", acline_motion_notify_cb)
        gtkimage.setPrompt(_('Enter the angle or click in the drawing area'))
        
#
# Suport functions
#

#
# angled construction lines
#


        









