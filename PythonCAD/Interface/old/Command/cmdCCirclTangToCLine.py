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
# <construction circle tangent to a construction line> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon

from PythonCAD.Generic import HCLine, VCLine, ACLine, CLine, CCircle

#
# Init
#---------------------------------------------------------------------------------------------------
def tangent_ccircle_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click on the construction object used for tangency.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", tangent_ccircle_mode_init)
    _tool.setHandler("button_press", ccircle_single_first_button_press_cb)
    
#
# Motion Notify
#---------------------------------------------------------------------------------------------------
def ccircle_single_motion_notify_cb(gtkimage, widget, event, tool):
    # current location of pointer
    point = gtkimage.image.getCurrentPoint()
    tool.setLocation(point)
    # sample tool
    gtkimage.viewport.sample(tool)    
    return True

#
# Button press callBacks
#---------------------------------------------------------------------------------------------------
def ccircle_single_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'tangent':True}
    ent=snap.getOnlySnap(_image,_tol,_snapArray).entity
    if ent is not None:
        _active_layer = _image.getActiveLayer()
        if isinstance(ent, (HCLine, VCLine, ACLine, CLine, CCircle)):
            tool.setConstructionLine(ent)
            tool.setHandler("button_press", ccircle_single_second_button_press_cb)
            tool.setHandler("motion_notify", ccircle_single_motion_notify_cb)
            gtkimage.setPrompt(_('Click where the circle should be drawn.'))
    return True

#---------------------------------------------------------------------------------------------------
def ccircle_single_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    point = snap.getSnapPoint(_image,_tol,_snapArray).point
    tool.setLocation(point)
    cmdCommon.create_entity(gtkimage)
    return True


#
# Entry callBacks
#

#
# Suport functions
#







