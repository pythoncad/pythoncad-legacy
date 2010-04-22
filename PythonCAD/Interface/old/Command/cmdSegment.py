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
# Segment command functions/Class 
#
import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Interface.Gtk import gtkdialog
from PythonCAD.Interface.Command import cmdCommon

#
# Init
#
#---------------------------------------------------------------------------------------------------
def segment_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point.'))
    _tool = gtkimage.getImage().getTool()
    _tool.direction = None
    _tool.setHandler("initialize", segment_mode_init)
    _tool.setHandler("button_press", segment_first_button_press_cb)
    _tool.setHandler("entry_event", segment_first_entry_event_cb)
    
#
# Motion Notify
#
#---------------------------------------------------------------------------------------------------
def segment_motion_notify_cb(gtkimage, widget, event, tool):
    """
        Segment notify motion event
    """
    # first point of segement
    p1 = tool.getFirstPoint().point
    # current pointer position
    p2 = gtkimage.getImage().getCurrentPoint()
    # manage horizontal vertical angle forced
    p = tool.transformCoords(p1, p2)
    tool.setCurrentPoint(p)
    # sample tool
    gtkimage.viewport.sample(tool)
    return True

#
# Button press callBack
#
#---------------------------------------------------------------------------------------------------
def segment_second_button_press_cb(gtkimage, widget, event, tool):
    tolerance = gtkimage.getTolerance()
    image = gtkimage.getImage()
    snap.setSnap(image, tool.setSecondPoint, tolerance)
    # force a point in a given direction (or ortho)
    if tool.direction is not None:
        # first point of segement
        p1 = tool.getFirstPoint().point
        # current pointer position
        p2 = tool.getSecondPoint().point
        # manage horizontal vertical angle forced
        p = transformCoords(p1, p2)
        # 
        _strP = snap.SnapPointStr("Freepoint", p, "None")
        tool.setSecondPoint(_strP)
    # create a segment
    try:
        cmdCommon.create_entity(gtkimage)  
        tool.direction = None 
    except:
        tool.setHandler("button_press", segment_second_button_press_cb)
        tool.setHandler("entry_event", segment_second_entry_event_cb)
        tool.setHandler("motion_notify", segment_motion_notify_cb)
        gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))   
    return True
    
#---------------------------------------------------------------------------------------------------
def segment_first_button_press_cb(gtkimage, widget, event, tool):
    tolerance = gtkimage.getTolerance()
    image = gtkimage.getImage()
    snap.setSnap(image, tool.setFirstPoint, tolerance)
    tool.setHandler("button_press", segment_second_button_press_cb)
    tool.setHandler("entry_event", segment_second_entry_event_cb)
    tool.setHandler("motion_notify", segment_motion_notify_cb)
    gtkimage.setPrompt(_('Enter the second point or click in the drawing area'))
    return True
   
#
# Entry call back
#
#---------------------------------------------------------------------------------------------------
def segment_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    if segment_set_direction(_text,tool):
        tool.setHandler("button_press", segment_second_button_press_cb)
        tool.setHandler("motion_notify", segment_motion_notify_cb)
        tool.setHandler("entry_event", segment_second_entry_event_cb)   
        _dir=str(tool.direction)
        gtkimage.setPrompt(_('Segmend d ' + _dir + 'Enter the second Point or click in the drawing area'))   
        _entry.delete_text(0, -1)
        gtkimage.redraw()
        return 
    _entry.delete_text(0, -1)    
    if len(_text):
        try:
            _x, _y = cmdCommon.make_tuple(_text, gtkimage.image.getImageVariables())
        except:
            if _text.strip()!="d:n" :
                gtkdialog._message_dialog(gtkimage,"Wrong comand","inser a touple of values x,y")
            return
        _str=snap.SnapPointStr("Freepoint",Point(_x, _y),None)
        tool.setSecondPoint(_str)
        cmdCommon.create_entity(gtkimage)

#---------------------------------------------------------------------------------------------------
def segment_first_entry_event_cb(gtkimage, widget, tool): 
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = cmdCommon.make_tuple(_text, gtkimage.image.getImageVariables())
        _str=snap.SnapPointStr("Freepoint",Point(_x, _y),None)
        tool.setFirstPoint(_str)
        tool.setHandler("button_press", segment_second_button_press_cb)
        tool.setHandler("motion_notify", segment_motion_notify_cb)
        tool.setHandler("entry_event", segment_second_entry_event_cb)        
        gtkimage.setPrompt(_('Enter the second Point or click in the drawing area'))
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

###
### Suport functions
###
###---------------------------------------------------------------------------------------------------
##def transformCoords(x,y,x1,y1,angle):
##    """
##        trasform the given cordinate with en angle
##        useful in case you whant to force a segment to be in a partuicular
##        direction
##    """
##    _x=x1
##    _y=y1
##    if angle is not None:
##        if angle == 90.0 or angle == 270.0:
##            _x=x
##        elif angle == 0.0 or angle == 180.0:
##            _y=y
##        else:
##            _radDir=(math.pi*angle)/180            
##            _tan=math.tan(_radDir)*abs(x-x1)  
##            if x>x1:
##                _y=y-_tan
##                _x=x-abs(x-x1)
##            else:
##                _y=y+_tan
##                _x=x+abs(x-x1)
##    return _x,_y
##
###---------------------------------------------------------------------------------------------------
##def segment_set_direction(text,tool):
##    """
##        parse the text and set the direction into the tool
##    """
##    if isinstance(text,str) :
##        if text.find(':') >0 :
##            cmdArgs=text.split(':')
##            if len(cmdArgs)==2:
##                _firstArgs=cmdArgs[0].strip().lower()
##                if _firstArgs == 'd' :
##                    _r = setSegmentDirection(tool,cmdArgs[1])            
##                    return _r
##                    
##    return False
##
###---------------------------------------------------------------------------------------------------
##def setSegmentDirection(tool,angle):
##    """
##        set the segment direction 
##    """
##    if str(angle).strip().lower() == "n" :
##        tool.direction=None
##        return False
##    else:
##        tool.direction=angle
##        return True
##    