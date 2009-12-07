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
# <Hatch> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.tools import Tool
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
from PythonCAD.Interface.Gtk import gtkerror
from PythonCAD.Interface.Gtk import gtkdialog

#Entity supported for the hatch command
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.segjoint import Chamfer, Fillet

_suportedEntity="Segment,Circle,Arc,Polyline,Chamfer,Fillet"
#
# Init
#
def hatch_mode_init(gtkimage, tool=None):
    """
        Inizialize the hatch comand
    """
    gtkimage.setPrompt(_('Select the external boundary entitys RightClick for internal.'))
    _tool = gtkimage.getImage().getTool()
    _tool.action=0
    _tool.tempExtOljects=[]
    _tool.tempIntOljects=[]
    _tool.setHandler("initialize", hatch_mode_init)
    _tool.setHandler("button_press", hatch_entity_button_press_cb)
    _tool.setHandler("right_button_press",hatch_change_mode)
    _tool.setHandler("entry_event", hatch_option_entry_event_cb)
    
#
# Motion Notifie
#
#def segment_motion_notify_cb(gtkimage, widget, event, tool):
#
# Button press callBacks
#
def hatch_change_mode(gtkimage, widget, event, tool):
    """
        with the right mouse we change the imput selection
        from outer region
        to inner region
        to command creation
    """    
    tool.action+=1
    if tool.action > 2: # Restart the mode selector
        tool.action=0
    if tool.action==0:
        gtkimage.setPrompt(_('Select the External boundary entitys RightClick for switch Imput mode.'))
    if tool.action==1:
        gtkimage.setPrompt(_('Select the Internal boundary entitys RightClick for switch Imput mode.'))
    if tool.action==2:
        gtkimage.setPrompt(_('Click to create the Hatch RightClick for switch Imput mode.'))

def  hatch_entity_button_press_cb(gtkimage, widget, event, tool):
    """
        hatch entity press button
    """
    _type = event.type
    _button = event.button
    if _type== gtk.gdk.BUTTON_PRESS:
        if _button == 1:
            if tool.action==0:
                addSelectedEntity(gtkimage,tool,event,"External")
            if tool.action==1:
                addSelectedEntity(gtkimage,tool,event,"Internal")
            if tool.action==2:
                createHatch(gtkimage,tool)
                hatch_mode_init(gtkimage, tool)
#
# Entry callBacks
#
def hatch_option_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    print "Debug: entry not yet implemented"
    pass
#
# Suport functions
#
def addSelectedEntity(gtkimage,tool,event,mode):
    """
        add entity at the selection
    """
    _obj,_pnt=snap.getSelections(gtkimage,_suportedEntity)    
    if mode=="External":
        tool.tempExtOljects.append(_obj)
    if mode =="Internal":
        tool.tempIntOljects.append(_obj)
 
def createHatch(gtkimage,tool):
    """
        Create The hatch
    """    
    try:   
        tool.create()
    except pythonCadEntityCreatioError, (e):
        _msg="Error on command " + e.getCommand + " Message: " +e.getMessage
        gtkdialog._error_dialog(gtkimage,_msg)
    except :
        _msg="Unendled error "
        gtkdialog._error_dialog(gtkimage,_msg)