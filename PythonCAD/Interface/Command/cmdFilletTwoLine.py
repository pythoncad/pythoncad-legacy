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
# <Fillet two line> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk

from math import hypot, pi, atan2

from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Generic.segjoint import  Fillet
# import some functionality from thenormal fillet comand
from PythonCAD.Interface.Command.cmdFillet import * 

from PythonCAD.Interface.Command import cmdCommon
import  PythonCAD.Interface.Gtk.gtkdialog as gtkdialog


#
# Init
#
def fillet_two_line_mode_init(gtkimage, tool=None):
    """
        init function for the fillet two line comand
    """
    _image = gtkimage.getImage()
    if tool !=None and tool.rad!=None:
        _rad = tool.rad
        _tool=tool
    else:        
        _rad = _image.getOption('FILLET_RADIUS') 
        _tool = gtkimage.getImage().getTool()
    _msg  =  'Click on the first Entity ( ) or enter command options.'
    _tool.initialize()
    _tool.rad=_rad
    fillet_prompt_message(gtkimage,_tool,_msg)
    _tool.setHandler("initialize", fillet_two_line_mode_init)
    _tool.setHandler("button_press", fillet_two_button_press_cb)
    _tool.setHandler("entry_event", fillet_entry_event_cb)
    gtkimage._activateSnap=False
#
# Motion Notifie
#

#
# Button press callBacks
#
def fillet_two_button_press_cb(gtkimage, widget, event, tool):
    """
       First Entity selected
    """
    _image = gtkimage.getImage()
    _objs,pnt=snap.getSelections(gtkimage,Segment)
    if _objs!=None and pnt!=None:
        _image.startAction()
        try:
            tool.FirstLine=_objs
            tool.FirstPoint=pnt
            if(tool.rad!=None):
                _rad = tool.rad
                _mod=tool.TrimMode
            else:        
                _rad = _image.getOption('FILLET_RADIUS')
                _mod = _image.getOption('FILLET_TWO_TRIM_MODE')
            _msg  =  'Click on the Second Entity ( ) or enter command options.'
            fillet_prompt_message(gtkimage,tool,_msg)
            tool.setHandler("button_press", fillet_two_button_second_press_cb)
            #
        finally:
            _image.endAction()

def fillet_two_button_second_press_cb(gtkimage, widget, event, tool):
    """
        Second selection commad
    """
    _image = gtkimage.getImage()
    _objs,pnt=snap.getSelections(gtkimage,Segment)  
    if _objs!=None and pnt!=None:
        _image.startAction()
        try:
            tool.SecondLine=_objs
            tool.SecondPoint=pnt
            tool.Create(_image)
        except ValueError,err:
            _errmsg = "Fillet ValueError error: %s" % str(err)
            gtkdialog._error_dialog(gtkimage,_errmsg )
        except:
            _errmsg = "Fillet error: %s" % str( sys.exc_info()[0])
            gtkdialog._error_dialog(gtkimage,_errmsg )
            for s in sys.exc_info():
                print "Exception Error: %s"%str(s)
        finally:
            _image.endAction()
            gtkimage.redraw()
            fillet_two_line_mode_init(gtkimage,tool)
#
# Entry callBacks
#

#
# Suport functions
#