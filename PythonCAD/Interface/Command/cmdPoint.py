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
# Point command functions/Class 
#

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon

#
# points Cmd Callback
#

def point_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    snap.setSnap(_image,tool.setPoint,_tol)
    cmdCommon.create_entity(gtkimage)
    return True

def point_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setPoint(_x, _y)
        cmdCommon.create_entity(gtkimage)

def point_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter the point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", point_mode_init)
    _tool.setHandler("button_press", point_button_press_cb)
    _tool.setHandler("entry_event", point_entry_event_cb)